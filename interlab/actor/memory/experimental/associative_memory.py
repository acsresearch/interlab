import math
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np

from interlab.actor import Event
from interlab.actor.memory import MemoryBase


@dataclass
class AssociativeMemoryItem:
    event: Event
    create_at: float
    last_accessed: float
    importance: float
    embedding: np.ndarray


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class AssociativeMemory(MemoryBase):
    importance_weight: float = 1.0
    recency_weight: float = 1.0
    similarity_weight: float = 1.0
    time_speed_multiplier: float = 1.0

    def __init__(
        self,
        get_embedding: Callable[[str], np.ndarray],
    ):
        self.items: list[AssociativeMemoryItem] = []
        self.get_embedding = get_embedding

    def add_event(
        self, event: Event, time: float | None = None, importance: float = 1.0
    ):
        if time is None:
            time = self.items[-1].create_at if self.items else 0.0
        embedding = self.get_embedding(event.data_as_string())
        self.items.append(
            AssociativeMemoryItem(
                event=event,
                create_at=time,
                last_accessed=time,
                embedding=embedding,
                importance=importance,
            )
        )

    def _relevance(
        self, query_embedding: np.ndarray, now: float, item: AssociativeMemoryItem
    ) -> float:
        importance = self.importance_weight * item.importance
        similarity = self.similarity_weight * cosine_similarity(
            query_embedding, item.embedding
        )
        recency = self.recency_weight * math.pow(
            0.99, (now - item.last_accessed) * self.time_speed_multiplier
        )
        return importance + similarity + recency

    def get_events(
        self, query: Any = None, max_events: int = None, now: float | None = None
    ) -> tuple[Event]:
        if max_events is None or max_events >= len(self.items):
            return tuple(item.event for item in self.items)
        if now is None:
            now = self.items[-1].last_accessed
        query_embedding = self.get_embedding(query)
        relevancy = [
            (self._relevance(query_embedding, now, item), item) for item in self.items
        ]
        relevancy.sort(key=lambda x: x[0])
        top_relevant: list[AssociativeMemoryItem] = [
            item for (_, item) in relevancy[-max_events:]
        ]
        top_relevant.sort(key=lambda x: x.create_at)
        return tuple(item.event for item in top_relevant)
