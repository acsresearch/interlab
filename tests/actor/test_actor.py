from unittest.mock import MagicMock, patch

from interlab.actor.base import ActorWithMemory, BaseActor
from interlab.actor.llm_actor import OneShotLLMActor


@patch.multiple(BaseActor, __abstractmethods__=set())
def test_simple_actor():
    a1 = BaseActor("Anna")
    a1._query = MagicMock()
    a1._query.return_value = "Bar!"
    o1 = a1.query("Foo?")
    assert o1 == "Bar!"
    assert a1._query.call_args.args == ("Foo?",)


@patch.multiple(ActorWithMemory, __abstractmethods__=set())
def test_memory_actor():
    a1 = ActorWithMemory("Barbara")
    a1._query = MagicMock()
    a1._query.return_value = "Bar!"
    o1 = a1.query("Foo?")
    a1.observe(o1)
    assert a1.memory.format_memories() == "Bar!"
    a1.observe("I noticed Baz")
    assert a1.memory.format_memories(separator="---") == "Bar!---I noticed Baz"
    # ListMemory ignores the query
    assert (
        a1.memory.format_memories(
            "query is ignored", separator="\n", formatter=lambda m: m.memory.upper()
        )
        == "BAR!\nI NOTICED BAZ"
    )


@patch.multiple(ActorWithMemory, __abstractmethods__=set())
def test_oneshot_actor_copy():
    a1 = OneShotLLMActor("Barbara", None, "Initial prompt")
    a1.observe("Foo", data=42, time=0.1)
    a2 = a1.copy()
    assert a2.name == "Barbara"
    a1.observe("Hello!")
    assert a1.memory.count_memories() == 2
    assert a2.memory.count_memories() == 1
    a2.observe("New event")
    assert a1.memory.count_memories() == 2
    assert a2.memory.count_memories() == 2
    assert a2.memory.items[0].data == 42
