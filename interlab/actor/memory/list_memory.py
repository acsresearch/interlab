import warnings
from typing import Any, Callable

from .base import BaseMemory, BaseMemoryItem


class ListMemory(BaseMemory):
    """
    A simple memory cosisting of a list of `BaseMemoryItem`s.
    """

    def __init__(self):
        super().__init__()
        self.items = []

    def copy(self) -> "ListMemory":
        m = ListMemory()
        m.items = list(self.items)
        return m
    
    def count(self) -> int:
        return len(self.items)

    def add_memory(self, memory: str, time: Any = None, data: Any = None):
        self.items.append(BaseMemoryItem(memory=memory, time=time, data=data))

    def format_memories(
        self,
        query: str = None,
        separator: str = "\n\n",
        formatter: Callable[[BaseMemoryItem], str] = None,
    ) -> str:
        if query is not None and query:
            warnings.warn(
                f"{self.__class__.__name__}.format_memories() ignores the query parameter but received a non-empty query."
            )
        return self._format_memories_helper(
            self.items, separator=separator, formatter=formatter
        )
