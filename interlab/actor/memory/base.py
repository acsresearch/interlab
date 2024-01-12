import abc
from dataclasses import dataclass
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class BaseMemoryItem:
    """
    Common class for memory items, may be extended by subclassing for each BaseMemory subclasses.

    `time` and `data` are optional and may be ignored by the memory system; they are also not contained
    in the textual representation of the memories by default.
    Note that if `content` is not of type `str`, it will be converted to `str` by most memories.

    In general, the items are assumed to be immutable once created and should not refer to complex
    InterLab structures (Actors, Environments, ...).
    """

    memory: str | Any
    time: Any = None
    data: Any = None


class BaseMemory(abc.ABC):
    """
    Base class for memory systems; formatter may be None for unformatted events.
    """

    def copy(self) -> "BaseMemory":
        """
        Full copy of the memory. The copy must be independent from the original instance. May be copy-on-write for efficiency.
        """
        raise NotImplementedError()

    def count(self) -> int:
        """
        Return the current number of held memories.
        
        Note this is informational and specific to every memory implementation. 
        In particular, it does not have to correspond to the number of memories added."""
        raise NotImplementedError()

    @abc.abstractmethod
    def add_memory(self, memory: str, time: Any = None, data: Any = None):
        raise NotImplementedError()

    @abc.abstractmethod
    def format_memories(
        self,
        query: str = None,
        separator: str = "\n\n",
        formatter: Callable[[BaseMemoryItem], str] = None,
    ) -> str:
        raise NotImplementedError()

    def _format_memories_helper(
        self,
        memories: Iterable[BaseMemoryItem],
        separator: str = "\n\n",
        formatter: Callable[[BaseMemoryItem], str] = None,
    ) -> str:
        return separator.join(
            str(m.memory) if formatter is None else str(formatter(m)) for m in memories
        )
