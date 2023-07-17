import random
from typing import Any

from ..context import Context
from ..utils import pseudo_random_color, shorten_str
from . import format
from . import memory as memory_module
from .event import Event


class Actor:
    """
    Interface for generic actor, to be used with LLMs, game theory or otherwise.

    Override methods _act and _observe in derived classes.

    Note: The interface is intentinally not async (for now, for usability reasons),
    use multi-threading for parallel inquiries. (Helpers for this are WIP.)
    """

    def __init__(self, name: str = None, *, style: dict[str, Any] = None):
        self.name = name
        if self.name is None:
            self.name = f"{self.__class__.__name__}{random.randint(0, 9999):i04}"
        self.style = style if style is not None else {}
        if self.style.get("color") is None:
            self.style["color"] = pseudo_random_color(self.name)

    def act(self, prompt: Any = None) -> Event:
        if prompt:
            name = f"{self.name} to act on {shorten_str(str(prompt))!r}"
            inputs = {"prompt": prompt}
        else:
            name = f"{self.name} to act"
            inputs = None
        with Context(name, kind="action", meta=self.style, inputs=inputs) as ctx:
            action = self._act(prompt)
            ctx.set_result(action)
            ev = Event(origin=self.name, data=action)  # _style=self.style)
        return ev

    def _act(self, prompt: Any = None) -> Any:
        raise NotImplementedError("Implement _act in a derived actor class")

    def observe(self, event: Event | Any, origin: str | None = None):
        """Observe the given Event.

        Instead of given Event object, you can also pass in observation and origin directly.
        """
        if not isinstance(event, Event):
            event = Event(data=event, origin=origin)
        with Context(
            f"{self.name} observes {shorten_str(str(event))!r}",
            kind="observation",
            meta=self.style,
            inputs={"origin": event.origin, "observation": event.data},
        ):
            self._observe(event)

    def _observe(self, event: Event):
        raise NotImplementedError("Implement _observe in a derived actor class")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class ActorWithMemory(Actor):
    """
    Actor with an instance of MemoryBase recording all observations.

    You still need to implement _act if you inherit from this actor.
    """

    DEFAULT_FORMAT = format.LLMTextFormat
    DEFAULT_MEMORY = memory_module.SimpleMemory

    def __init__(self, name=None, *, memory: memory_module.MemoryBase = None, **kwargs):
        super().__init__(name, **kwargs)
        self.memory = memory
        if self.memory is None:
            self.memory = self.DEFAULT_MEMORY(format=self.DEFAULT_FORMAT())

    def _observe(self, event: Event):
        self.memory.add_event(event)
