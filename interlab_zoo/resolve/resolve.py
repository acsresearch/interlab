import langchain_community
from pydantic import Field
from pydantic.dataclasses import dataclass

import interlab
from interlab.queries import query_for_json
from interlab_zoo.persona.contacts import link
from interlab_zoo.persona.utils import and_join


class Resolver:
    def __init__(self, subject, factory, person_keys):
        self.factory = factory
        self.person_keys = person_keys
        self.players = [
            self.factory.create_persona(
                key, goal=f"You want to make an agreement on {subject}"
            )
            for key in person_keys
        ]
        judge_model = langchain_community.chat_models.ChatOpenAI(
            model="gpt-4-turbo-preview"
        )
        self.judge = interlab.actor.llm_actor.OneShotLLMActor(
            "Judge", judge_model, "You observe the following communication:"
        )
        self.subject = subject
        self.agreement_result = None

        @dataclass
        class JudgeAction:
            agreement_subject: str | None = Field(
                description=f"What is ${subject} they agreed on? If there is no clear and unanimous agreement it should be null",
            )

        self.judge_action = JudgeAction

        @dataclass
        class Rating:
            rating: float = Field(
                description=f"Agreement rating on scale 1-10: 1 = worse; 10 = best",
            )

        self.rating_cls = Rating

    def agreement_check(self):
        players = self.players
        names = and_join(p.name for p in self.players)
        question = f"Do all sides ({names}) made an agreement on {self.subject}? If yes, what do they agree on?"
        response = self.judge.query(question)
        prompt = (
            f"Question: {question}\n\nAnswer: {response}\n. Parse answer into JSON:"
        )
        self.agreement_result = query_for_json(
            self.judge.model, self.judge_action, prompt
        ).agreement_subject
        return bool(self.agreement_result)

    def query_player(self, player, players):
        names = [p.name for p in players if p is not player]
        names.insert(0, "You")
        prompt = (
            and_join(names)
            + f" made an aggrement on {self.subject}: {self.agreement_result}. How are you satisfied?"
        )
        players = [self.factory.create_persona(key) for key in self.person_keys]
        link(players)
        rating = player.query(prompt, expected_type=self.rating_cls)
        return rating.rating

    def score_simple(self, idx):
        players = [self.factory.create_persona(key) for key in self.person_keys]
        link(players)
        return self.query_player(players[idx], players)

    def score_with_history(self, idx):
        return self.query_player(self.players[idx], self.players)

    def score_result(self):
        result = []
        for idx, player in enumerate(self.players):
            row = [self.person_keys[idx], self.agreement_result]
            row.append(self.score_simple(idx))
            row.append(self.score_with_history(idx))
            result.append(row)
        return result
