from typing import Any

from ..event import Event
from .base import MemoryBase


class ListMemory(MemoryBase):
    """Simple memory that is effectively just a list of Events"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.events: list[Event] = []

    def add_event(self, event: Event, time: float | None = None):
        self.events.append(event)

    def get_events(self, query: Any = None, max_events: int = None) -> tuple[Event]:
        if max_events is None:
            return tuple(self.events)
        else:
            return tuple(self.events[-max_events:])
