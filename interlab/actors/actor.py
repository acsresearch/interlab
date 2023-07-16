import random
from typing import Any
from pydantic.dataclasses import dataclass, Field

from ..context import Context
from ..utils import pseudo_random_color, shorten_str
from . import format
from . import memory as memory_module
from .event import Event


@dataclass
class Actor:
    """
    Interface for generic actor, to be used with LLMs, game theory or otherwise.

    Override methods _act and _observe in derived classes.

    Note: The interface is intentinally not async (for now, for usability reasons),
    use multi-threading for parallel inquiries. (Helpers for this are WIP.)
    """

    name: str = None
    _style: dict[str, Any] = Field(
        description="optional styling hints for visualization", default_factory=dict
    )

    def __post_init__(self):
        if self.name is None:
            self.name = f"{self.__class__.__name__}{random.randint(0, 9999):i04}"
        if self._style.get("color") is None:
            self._style["color"] = pseudo_random_color(self.name)

    def act(self, prompt: any = None) -> Event:
        if prompt:
            name = f"{self.name} to act on {shorten_str(str(prompt))!r}"
            inputs = {"prompt": prompt}
        else:
            name = f"{self.name} to act"
            inputs = None
        with Context(name, kind="action", meta=self.style, inputs=inputs) as ctx:
            action = self._act(prompt)
            ctx.set_result(action)
            ev = Event(origin=self.name, data=action, _style=self.style)
        return ev

    def _act(self, prompt: any = None) -> any:
        raise NotImplementedError("Implement _act in a derived actor class")

    def observe(self, event: Event):
        with Context(
            f"{self.name} observes {shorten_str(str(event))!r}",
            kind="observation",
            meta=self.style,
            inputs={"event": event},
        ):
            self._observe(event)

    def _observe(self, event: Event):
        raise NotImplementedError("Implement _observe in a derived actor class")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


@dataclass
class ActorWithMemory(Actor):
    """
    Actor with an instance of MemoryBase recording all observations.

    You still need to implement _act if you inherit from this actor.
    """

    DEFAULT_FORMAT = format.LLMTextFormat
    DEFAULT_MEMORY = memory_module.SimpleMemory

    memory: memory_module.MemoryBase = None

    def __post_init__(self):
        if self.memory is None:
            self.memory = self.DEFAULT_MEMORY(format=self.DEFAULT_FORMAT())

    def _observe(self, event: Event):
        self.memory.add_event(event)
