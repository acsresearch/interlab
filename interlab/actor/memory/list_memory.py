from typing import Any

from ..event import Event
from .base import BaseMemory


class ListMemory(BaseMemory):
    """Simple memory that is effectively just a list of Events"""

    def __init__(self, events=None, **kwargs):
        super().__init__(**kwargs)
        if events is None:
            events = []
        self.events = events

    def add_event(self, event: Event):
        self.events.append(event)

    def get_events(self, query: Any = None, limit_events: int = None) -> tuple[Event]:
        return tuple(
            self.events[(-limit_events if limit_events is not None else None) :]
        )

    def copy(self):
        return ListMemory(self.events[:], format=self.format)
