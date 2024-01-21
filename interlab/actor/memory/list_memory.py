from typing import Any, Callable

from .base import BaseMemory, BaseMemoryItem


class ListMemory(BaseMemory):
    """
    A simple memory cosisting of a list of `BaseMemoryItem`s.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._items = []

    def count_memories(self) -> int:
        return len(self._items)

    def total_tokens(self) -> int:
        return sum(m.token_count for m in self._items)

    def add_memory(self, memory: str | Any, time: Any = None, data: Any = None):
        """
        Add a memory to the memory store.
        """
        self._items.append(
            BaseMemoryItem(
                memory=memory,
                time=time,
                data=data,
                token_count=self._count_tokens(memory),
            )
        )

    @property
    def items(self):
        """
        Return a tuple of all memories in the memory store.
        """
        return tuple(self._items)

    def format_memories(
        self,
        query: str = None,
        separator: str = "\n\n",
        formatter: Callable[[BaseMemoryItem], str] = None,
        item_limit: int = None,
        token_limit: int = None,
    ) -> str:
        return self._format_memories_helper(
            self._items,
            separator=separator,
            formatter=formatter,
            item_limit=item_limit,
            token_limit=token_limit,
        )
