from interlab.tracing import TracingNode, FileStorage
from interlab.actor import OneShotLLMActor
from pydantic.dataclasses import dataclass, Field
import json


@dataclass
class Person:
    name: str
    description: str
    age: int


def load_people():
    with open("data.json") as file:
        data = json.loads(file.read())
    result = []
    for name, data in data.items():
        result.append(Person(name=name, description=data["desc"], age=data["age"]))
    return result

def make_actor(model, person, other):
    prompt = f"You are {person.name} (age {person.age}).\n{person.description}\nYou are communicating with {other.name} (age {other.age})\n"
    return OneShotLLMActor(person.name, model, initial_prompt=prompt)

@dataclass
class ObserverAction:
    agreement: Field(bool, description="True if and only if both sides made an agreement on the same movie. Otherwise False")
    movie_name: Field(str | None, description="Name of the movie that both parties agreed on; otherwise None")

def resolve(model, person1, person2):
    actor1 = make_actor(model, person1, person2)
    actor2 = make_actor(model, person2, person1)

    actors = [actor1, actor2]

    observer = OneShotLLMActor("Observer", model)

    for i in range(10):
        sender = actors[i % 2]
        receiver = actors[(i + 1) % 2]

        evt = sender.query(f"You want to watch a movie with {receiver.name}. Write an email to {receiver.name}. You have agree on the same movie that you will watch together.")
        actor1.observe(evt)
        actor2.observe(evt)
        observer.observe(evt)
        if i > 2:
            observer.query("")

def main():
    model =
    people = load_people()[:2]
    print(people)

    storage = FileStorage("logs/")

    with TracingNode("movie_exp", storage=storage):
        for p1 in people:
            for p2 in people:
                if p1 == p2:
                    continue
                resolve(p1, p2)

if __name__ == "__main__":
    main()
