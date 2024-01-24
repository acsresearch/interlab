from treetrace import TracingNode, FileStorage, with_trace
from interlab.queries import query_for_json
from interlab.actor import OneShotLLMActor
from pydantic.dataclasses import dataclass, Field
import json


@dataclass
class Person:
    name: str
    public: str
    private: str


def load_people(path: str) -> list[Person]:
    with open(path) as file:
        data = file.read()
    result = []
    for name, data in json.loads(data).items():
        result.append(Person(name=name, public=data["public"], private=data["private"]))
    return result


@dataclass
class Experiment:
    prompt: str
    message_header: str
    agreement_topic: str
    max_messages: int

    actors_file: str
    pairs: str


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


@dataclass
class ScoreRecord:
    me: str
    other: str
    score: int


@dataclass
class Result:
    people: list[Person]
    agreement: str | None
    steps: int
    scores: dict[str, list[ScoreRecord]] | None = None


def score_just_answer(model, person1, person2, agreement_result):
    prompt = (
        f"You are {person1.name}\n\n"
        f"Public information about {person1.name}: {person1.public}\n\n"
        f"Private information about {person1.name}: {person1.private}\n\n"
        f"After a negotiation, we made the following agreement on the same movie: {agreement_result}\n\n"
        "Rate how much you are satisfied with the result of the agreement"
    )
    return ScoreRecord(
        me=person1.name,
        other=person2.name,
        score=query_for_json(
            model,
            Score,
            prompt,
        ).score,
    )


def score_with_history(person1, person2, agreement_result, observer):
    prompt = (
        f"Public information about {person1.name}: {person1.public}\n\n"
        f"Private information about {person1.name}: {person1.private}\n\n"
        f"After a negotiation, we made the following agreement on the same movie: {agreement_result}\n\n"
        f"Rate how much {person1.name} is satisfied with the result of the agreement"
    )
    return ScoreRecord(
        me=person1.name,
        other=person2.name,
        score=observer.query(
            prompt,
            expected_type=Score,
        ).score,
    )


@with_trace()
def resolve(model, person1, person2):
    actor1 = make_actor(model, person1, person2)
    actor2 = make_actor(model, person2, person1)

    actors = [actor1, actor2]

    observer = OneShotLLMActor(
        "Observer",
        model,
        f"You are observing communication between {person1.name} and {person2.name}.",
    )

    @dataclass
    class ObserverAction:
        agreement: int = Field(
            description="1 if and only if both sides made an agreement on the same movie. Otherwise 0",
        )
        movie_name: str | None = Field(
            description="Name of the movie that both parties agreed on; otherwise null",
        )

    max_steps = 10
    for i in range(max_steps):
        sender = actors[i % 2]
        receiver = actors[(i + 1) % 2]

        prompt = f"Write an email to {receiver.name}. You have to agree on the same movie that you will watch together."
        message = sender.query(prompt)
        message = f"Message from {sender.name} to {receiver.name}: {message}"
        actor1.observe(message)
        actor2.observe(message)
        observer.observe(message)
        if i > 1:
            result = observer.query(
                "Do they make an agreement?", expected_type=ObserverAction
            )
            if result.agreement:
                break
    else:
        return Result(people=[person1, person2], steps=max_steps, agreement=None)
    agreement_result = result.movie_name
    scores = {"just_answer": [], "with_history": []}
    scores["just_answer"].append(
        score_just_answer(model, person1, person2, agreement_result)
    )
    scores["just_answer"].append(
        score_just_answer(model, person2, person1, agreement_result)
    )
    scores["with_history"].append(
        score_with_history(person1, person2, agreement_result, observer)
    )
    scores["with_history"].append(
        score_with_history(person2, person1, agreement_result, observer)
    )
    return Result(
        people=[person1, person2], steps=i, agreement=agreement_result, scores=scores
    )


def resolve_pairs(model, people):
    results = []
    for p1 in people:
        for p2 in people:
            if p1 == p2:
                continue
            results.append(resolve(model, p1, p2))
    return results


# def main():
#     model =
#     people = load_people()
#     print(people)
#
#     storage = FileStorage("logs/")
#
#     with TracingNode("movie_exp", storage=storage):
#         for p1 in people:
#             for p2 in people:
#                 if p1 == p2:
#                     continue
#                 resolve(p1, p2)
#
# if __name__ == "__main__":
#     main()
