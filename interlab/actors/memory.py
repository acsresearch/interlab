from typing import Any, Callable

import numpy as np
from pydantic.dataclasses import dataclass

from .event import Event
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


class SimpleMemory(MemoryBase):
    """Simple memory that is effectively just a list of Events"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.events = []

    def add_event(self, event: Event):
        self.events.append(event)

    def get_events(self, query: Any = None, limit: int = None) -> tuple[Event]:
        return tuple(self.events[(-limit if limit is not None else None) :])


#
# WIP: untested
#

# @dataclass
# class RelevanceTextMemoryItem:
#     event: Event
#     text: str
#     embedding: np.ndarray


# class RelevanceTextMemory(MemoryBase):
#     def __init__(
#         self,
#         embed_engine,
#     ):
#         self.embed_engine = embed_engine
#         self.events = []

#     def add_event(self, event: Event):
#         # TODO: Consider less naive text to embed - e.g. formatted
#         emb = self.embed_engine.embed_documents([str(event)])
#         emb = emb / np.sum(emb**2) ** 0.5
#         self.events.append(RelevanceTextMemoryItem(event, emb))

#     def get_events(
#         self, query: str = None, max_events: int = 10, max_tokens: int = None
#     ) -> tuple[Event]:
#         assert max_tokens is None
#         emb = self.embed_engine.embed_query(str(query))
#         emb = emb / np.sum(emb**2) ** 0.5
#         scores = [np.dot(emb, e.embedding) for e in self.events]
#         cutoff = np.sort(scores)[-max_events]
#         return tuple(e for e, s in zip(self.events, scores) if s >= cutoff)
