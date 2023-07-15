from dataclasses import dataclass

import numpy as np

from .event import Event


class MemoryBase:
    def add_event(self, event: Event):
        raise NotImplementedError()

    # TODO: Not quite happy with this!
    # Now I think that memory should also have a formatter argument and
    # return formatted memory chunk (which also allows various summaries to take place,
    # whether by LLMs or in the games)
    def events_for_query(
        self, query: str = None, max_events: int = None, max_tokens: int = None
    ) -> tuple[Event]:
        raise NotImplementedError()


class SimpleMemory(MemoryBase):
    def __init__(self):
        self.events = []

    def add_event(self, event: Event):
        self.events.append(event)

    def events_for_query(
        self, query: str = None, max_events: int = None, max_tokens: int = None
    ) -> tuple[Event]:
        assert max_tokens is None
        if max_events is not None:
            return tuple(self.events[-max_events:])
        return tuple(self.events)


@dataclass
class RelevanceTextMemoryItem:
    event: Event
    embedding: np.ndarray


class RelevanceTextMemory(MemoryBase):
    def __init__(self, embed_engine):
        self.embed_engine = embed_engine
        self.events = []

    def add_event(self, event: Event):
        # TODO: Consider less naive text to embed - e.g. formatted
        emb = self.embed_engine.embed_documents([str(event)])
        emb = emb / np.sum(emb**2) ** 0.5
        self.events.append(RelevanceTextMemoryItem(event, emb))

    def events_for_query(
        self, query: str = None, max_events: int = 10, max_tokens: int = None
    ) -> tuple[Event]:
        assert max_tokens is None
        emb = self.embed_engine.embed_query(str(query))
        emb = emb / np.sum(emb**2) ** 0.5
        scores = [np.dot(emb, e.embedding) for e in self.events]
        cutoff = np.sort(scores)[-max_events]
        return tuple(e for e, s in zip(self.events, scores) if s >= cutoff)
