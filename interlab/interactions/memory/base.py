from typing import Any

from ..event import Event
from .format import FormatBase


class MemoryBase:
    """Base class for memory systems; formatter may be None for unformatted events"""

    def __init__(self, *, format: FormatBase = None):
        self.format = format

    def add_event(self, event: Event):
        raise NotImplementedError()

    def get_events(self, query: Any = None, limit: int = None) -> tuple[Event]:
        raise NotImplementedError()

    def get_formatted(self, *args, **kwargs) -> Any:
        """Convenience wrapper for get_event with formatting"""
        assert self.format is not None
        events = self.get_events(*args, **kwargs)
        return self.format.format_events(events)
