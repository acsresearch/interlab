#
# WIP and untested
#


from dataclasses import KW_ONLY, dataclass
from typing import Any, Callable

import numpy as np
import openai

from ..base import BaseMemory, BaseMemoryItem


@dataclass(frozen=True)
class SimpleAssociativeMemoryItem(BaseMemoryItem):
    _: KW_ONLY
    embedding: np.ndarray = None


class SimpleAssociativeMemory(BaseMemory):
    DEAULT_EMBED_MODEL_FACTORY = lambda: openai.Embedding("text-embedding-ada-002")

    def __init__(self, embed_model=None):
        if embed_model is None:
            embed_model = self.DEAULT_EMBED_MODEL_FACTORY()
        self.embed_model = embed_model

    def _embed(self, text: str) -> np.ndarray:
        emb = np.array(self.embed_model.embed_documents([text])[0], dtype=np.float16)
        return emb / np.sum(emb**2) ** 0.5  # Normalize to L_2(emb)=1

    def add_memory(self, memory: str, time: Any = None, data: Any = None):
        memory = str(memory)
        self.items.append(
            SimpleAssociativeMemoryItem(
                memory=memory,
                token_count=self._count_tokens(memory),
                time=time,
                data=data,
                embedding=self._embed(memory),
            )
        )

    def format_memories(
        self,
        query: str = None,
        *,
        separator: str = "\n\n",
        formatter: Callable[[BaseMemoryItem], str] = None,
        item_limit: int = None,
        token_limit: int = None,
    ):
        if query is not None:
            emb = self._embed(query)
            scores = [np.dot(emb, e.embedding) for e in self.items]
            # TODO(gavento): Consider adding temporal scoring, and scoring relative to token count
        else:
            scores = None  # Default priority of preferring later messages
        return super()._format_memories_helper(
            self.items,
            priorities=scores,
            separator=separator,
            formatter=formatter,
            item_limit=item_limit,
            token_limit=token_limit,
        )
