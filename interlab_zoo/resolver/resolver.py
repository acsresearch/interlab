import uuid

from treetrace import TracingNode, FileStorage, with_trace
from interlab.queries import query_for_json, ParsingFailure
from interlab.actor import OneShotLLMActor
from pydantic.dataclasses import dataclass, Field
from serde.json import from_json
import click
import langchain
import dotenv
import pandas as pd
import tqdm

dotenv.load_dotenv()


@dataclass
class Model:
    name: str
    temp: float


@dataclass
class Person:
    name: str
    public: str
    private: str


@dataclass
class ActorDefinition:
    name: str
    person: str
    model: Model


@dataclass
class Pair:
    first: ActorDefinition
    second: ActorDefinition
    evaluation_model: Model


@dataclass
class Experiment:
    experiment_name: str
    prompt: str
    message_header: str
    agreement_topic: str
    max_messages: int

    people: list[Person]
    pairs: list[Pair]

    tries_per_pair: int

    metrics: list[str]

    @staticmethod
    def load(path):
        with open(path) as file:
            data = file.read()
        return from_json(Experiment, data)

    def run(self):
        person_map = {p.name: p for p in self.people}
        entries = []
        for pair in tqdm.tqdm(self.pairs):
            person1 = person_map[pair.first.person]
            person2 = person_map[pair.second.person]

            model1 = make_model(pair.first.model)
            model2 = make_model(pair.second.model)
            evaluation_model = make_model(pair.evaluation_model)

            for i in range(self.tries_per_pair):
                resolve_uuid = uuid.uuid4()
                with TracingNode(
                    "resolve",
                    inputs={"pair": pair, "resolve_uuid": resolve_uuid},
                ) as node:
                    actor1 = make_actor(model1, person1, person2)
                    actor2 = make_actor(model2, person2, person1)
                    with TracingNode("resolve"):
                        steps, result, observer = self.resolve(
                            evaluation_model, actor1, actor2
                        )
                    entry = [
                        resolve_uuid,
                        pair.first.person,
                        pair.first.model.name,
                        pair.first.model.temp,
                        pair.second.person,
                        pair.second.model.name,
                        pair.second.model.temp,
                        result,
                    ]
                    result_dict = {
                        "agreement_on": result,
                    }
                    with TracingNode("scoring"):
                        if "score_basic" in self.metrics:
                            entry.append(
                                self.score_basic(evaluation_model, person1, result)
                            )
                            result_dict["score_basic"] = entry[-1]
                        if "score_history" in self.metrics:
                            entry.append(
                                self.score_with_history(person1, result, observer)
                            )
                            result_dict["score_history"] = entry[-1]
                    entries.append(entry)
                    node.set_result(result_dict)

        headers = [
            "uuid",
            "person1",
            "model1",
            "temp1",
            "person2",
            "model2",
            "temp2",
            "result",
        ]
        if "score_basic" in self.metrics:
            headers.append("score_basic")
        if "score_history" in self.metrics:
            headers.append("score_history")
        df = pd.DataFrame(entries, columns=headers)
        return df.set_index("uuid")

    def score_basic(self, model, person1, agreement_result):
        if agreement_result is None:
            return None
        prompt = (
            f"You are {person1.name}\n\n"
            f"Public information about {person1.name}: {person1.public}\n\n"
            f"Private information about {person1.name}: {person1.private}\n\n"
            f"After a negotiation, we made the following agreement on {self.agreement_topic}: {agreement_result}\n\n"
            "Rate how much you are satisfied with the result of the agreement"
        )
        with TracingNode("score_basic") as node:
            try:
                result = query_for_json(
                    model,
                    Score,
                    prompt,
                ).score
            except ParsingFailure:
                result = None
            node.set_result(result)
            return result

    def score_with_history(self, person1, agreement_result, observer):
        if agreement_result is None:
            return None
        prompt = (
            f"Public information about {person1.name}: {person1.public}\n\n"
            f"Private information about {person1.name}: {person1.private}\n\n"
            f"After a negotiation, we made the following agreement on {self.agreement_topic}: {agreement_result}\n\n"
            f"Rate how much {person1.name} is satisfied with the result of the agreement"
        )
        with TracingNode("score_basic") as node:
            try:
                result = observer.query(
                    prompt,
                    expected_type=Score,
                ).score
            except ParsingFailure:
                result = None
            node.set_result(result)
            return result

    def resolve(self, evaluation_model, actor1, actor2):
        actors = [actor1, actor2]

        observer = OneShotLLMActor(
            "Observer",
            evaluation_model,
            f"You are observing communication between {actor1.name} and {actor2.name}.",
        )

        @dataclass
        class ObserverAction:
            has_agreement: int = Field(
                description=f"1 if and only if both sides made an agreement on {self.agreement_topic}. Otherwise 0",
            )
            agreement_result: str | None = Field(
                description=f"{self.agreement_topic} that both parties agreed on; otherwise null",
            )

        max_steps = 10
        for i in range(max_steps):
            sender = actors[i % 2]
            receiver = actors[(i + 1) % 2]

            prompt = f"Write an email to {receiver.name}. You have to agree on {self.agreement_topic} that you will watch together."
            message_text = sender.query(prompt)
            header = self.message_header.replace("$sender", sender.name)
            header = header.replace("$receiver", receiver.name)
            message = f"{header}: {message_text}"
            actor1.observe(message)
            actor2.observe(message)
            observer.observe(message)
            if i > 1:
                result = observer.query(
                    "Do they make an agreement?", expected_type=ObserverAction
                )
                if result.has_agreement:
                    return i, result.agreement_result, observer
        return max_steps, None, observer


def make_model(model_def):
    return langchain.chat_models.ChatOpenAI(
        model_name=model_def.name, temperature=model_def.temp
    )


def make_actor(model, person, other):
    prompt = (
        f"You are {person.name}\n\n"
        f"Public information about {person.name}: {person.public}\n\n"
        f"Private information about {person.name}: {person.private}\n\n"
        f"You are communicating by email with {other.name}\n\n"
        f"Public information about {other.name}: {other.public}\n\n"
    )
    return OneShotLLMActor(person.name, model, prompt)


@dataclass
class Score:
    score: int = Field(
        description="Rating on scale 1-10: 10 is the best, 1 is the worst",
    )


@click.command()
@click.argument("filename")
@click.argument("logs_path")
@click.argument("output_csv")
def run_experiment(filename, logs_path, output_csv):
    storage = FileStorage(logs_path)
    experiment = Experiment.load(filename)
    with TracingNode(experiment.experiment_name, storage=storage):
        result = experiment.run()
    result.to_csv(output_csv)


if __name__ == "__main__":
    run_experiment()
