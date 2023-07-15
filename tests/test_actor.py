from unittest.mock import MagicMock

from interlab.actors.actor import Actor
from interlab.actors.event import Event


def test_simple_actor():
    a1 = Actor("Anna")
    a1._act = MagicMock()
    a1._act.return_value = "Bar!"
    o1 = a1.act("Foo?")
    assert o1.data == "Bar!"
    assert o1.origin == a1.name
    assert a1._act.call_args.args == ("Foo?",)

    assert a1.formatter.format_event(o1, a1) == "Anna: Bar!"

    a1.observe(o1)
    assert a1.memory.events_for_query() == (o1,)
    a1.observe(Event("Baz"))
    assert a1.formatted_memories("ignored") == "Anna: Bar!\n\nBaz"
