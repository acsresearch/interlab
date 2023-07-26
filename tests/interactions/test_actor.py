from unittest.mock import MagicMock, patch

from interlab.interactions.actor.base import ActorBase, ActorWithMemory
from interlab.interactions.event import Event


@patch.multiple(ActorBase, __abstractmethods__=set())
def test_simple_actor():
    a1 = ActorBase("Anna")
    a1._act = MagicMock()
    a1._act.return_value = "Bar!"
    o1 = a1.act("Foo?")
    assert o1.data == "Bar!"
    assert o1.origin == a1.name
    assert a1._act.call_args.args == ("Foo?",)


@patch.multiple(ActorWithMemory, __abstractmethods__=set())
def test_memory_actor():
    a1 = ActorWithMemory("Barbara")
    a1._act = MagicMock()
    a1._act.return_value = "Bar!"
    o1 = a1.act("Foo?")
    assert a1.memory.format.format_event(o1) == "Barbara: Bar!"

    a1.observe(o1)
    assert a1.memory.get_events() == (o1,)
    a1.observe(Event("Baz"))
    assert a1.memory.get_formatted("ignored") == "Barbara: Bar!\n\nBaz"
