import numpy as np

from interlab.actor import Event
from interlab.actor.memory.experimental.associative_memory import AssociativeMemory


def test_embedding(text):
    h = any(x in text for x in ["swimming", "gardening", "hobbies"])
    t = any(x in text for x in ["sometimes", "morning", "time"])
    g = any(x in text for x in ["go"])
    return np.array([float(h), float(t), float(g)])


def dummy_embedding(_text):
    return np.ones(3)


def test_associative_memory():
    memory = AssociativeMemory(get_embedding=test_embedding)
    e1 = Event("I sometimes go swimming")
    e2 = Event("I forgot to eat breakfast this morning")
    e3 = Event("I do not like gardening")
    e4 = Event("It is time to go bed")
    events = [e1, e2, e3, e4]
    for e in events:
        memory.add_event(e)
    result = memory.get_events("hobbies", 2)
    assert result == (e1, e3)

    memory = AssociativeMemory(get_embedding=dummy_embedding)
    e1 = Event("I sometimes go swimming")
    e2 = Event("I forgot to eat breakfast this morning")
    e3 = Event("I do not like gardening")
    e4 = Event("It is time to go bed")
    events = [e1, e2, e3, e4]
    for i, e in enumerate(events):
        memory.add_event(e, time=i)
    result = memory.get_events("hobbies", 2)
    assert result == (e3, e4)

    memory = AssociativeMemory(get_embedding=dummy_embedding)
    e1 = Event("I sometimes go swimming")
    e2 = Event("I forgot to eat breakfast this morning")
    e3 = Event("I do not like gardening")
    e4 = Event("It is time to go bed")
    events = [e1, e2, e3, e4]
    for i, e in enumerate(events):
        memory.add_event(e, time=i, importance=(10.0 - i))
    result = memory.get_events("hobbies", 2)
    assert result == (e1, e2)
