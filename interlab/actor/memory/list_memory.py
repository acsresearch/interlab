from typing import Any

from ..event import Event
from .base import MemoryBase


class ListMemory(MemoryBase):
    """Simple memory that is effectively just a list of Events"""

    def __init__(self, events=None, **kwargs):
        super().__init__(**kwargs)
        self.events = events or []

    def add_event(self, event: Event):
        self.events.append(event)

    def copy(self) -> "ListMemory":
        return ListMemory(events=self.events[:], format=self.format)

    def get_events(self, query: Any = None, limit_events: int = None) -> tuple[Event]:
        return tuple(
            self.events[(-limit_events if limit_events is not None else None) :]
        )
