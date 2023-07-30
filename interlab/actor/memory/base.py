import abc
from typing import Any

from ..event import Event
from .format import FormatBase


class MemoryBase(abc.ABC):
    """Base class for memory systems; formatter may be None for unformatted events"""

    def __init__(self, *, format: FormatBase = None):
        self.format = format

    @abc.abstractmethod
    def add_event(self, event: Event):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_events(self, query: Any = None) -> tuple[Event]:
        raise NotImplementedError()

    def get_formatted(self, *args, **kwargs) -> Any:
        """Convenience wrapper for get_event with formatting"""
        assert self.format is not None
        events = self.get_events(*args, **kwargs)
        return self.format.format_events(events)
