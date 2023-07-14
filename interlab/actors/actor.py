import random

from ..context import Context
from ..utils import pseudo_random_color, shorten_str
from . import format, memory as memory_
from .event import Event


class Actor:
    DEFAULT_FORMAT = format.LLMTextFormat

    def __init__(
        self,
        name: str | None = None,
        *,
        color: str | None = None,
        memory: memory_.MemoryBase = None,
        format: format.FormatBase = None,
    ):
        self.name = name or f"self.__class__.__name__{random.randint(0, 9999):i04}"
        self.memory = memory or memory_.SimpleMemory()
        self.formatter = format or self.DEFAULT_FORMAT()
        self.style = {"color": color or pseudo_random_color(self.name)}

    def formatted_memories(self, query: any = None) -> any:
        return self.formatter.format_events(self.memory.events_for_query(query), self)

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
            ev = Event(origin=self.name, data=action, style=self.style)
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
        self.memory.add_event(event)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"
