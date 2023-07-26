#
# WIP and untested
#

import numpy as np
from pydantic.dataclasses import dataclass

from ...event import Event
from ..base import MemoryBase


@dataclass
class RelevanceTextMemoryItem:
    event: Event
    text: str
    embedding: np.ndarray


class RelevanceTextMemory(MemoryBase):
    def __init__(
        self,
        embed_engine,
    ):
        self.embed_engine = embed_engine
        self.events = []

    def add_event(self, event: Event):
        # TODO: Consider less naive text to embed - e.g. formatted
        emb = self.embed_engine.embed_documents([str(event)])
        emb = emb / np.sum(emb**2) ** 0.5
        self.events.append(RelevanceTextMemoryItem(event, emb))

    def get_events(
        self, query: str = None, max_events: int = 10, max_tokens: int = None
    ) -> tuple[Event]:
        assert max_tokens is None
        emb = self.embed_engine.embed_query(str(query))
        emb = emb / np.sum(emb**2) ** 0.5
        scores = [np.dot(emb, e.embedding) for e in self.events]
        cutoff = np.sort(scores)[-max_events]
        return tuple(e for e, s in zip(self.events, scores) if s >= cutoff)
