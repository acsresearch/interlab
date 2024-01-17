import abc
from dataclasses import KW_ONLY, dataclass
from typing import Any, Callable, Iterable

import numpy as np
from typing_extensions import Self

from ...queries.count_tokens import count_tokens
from ...utils.copying import checked_deepcopy


@dataclass(frozen=True)
class BaseMemoryItem:
    """
    Common class for memory items, may be extended by subclassing for each BaseMemory subclasses.

    `time` and `data` are optional and may be ignored by the memory system; they are also not contained
    in the textual representation of the memories by default.
    Note that if `content` is not of type `str`, it will be converted to `str` by most memories.

    These objects (as well as any derived classes) must be immutable once created, including any referred data!
    In particular, the `data` attribute should not refer to any complex InterLab structures
    (e.g. Actors, Environments, ...).
    """

    memory: str | Any
    _: KW_ONLY
    token_count: Any = None
    time: Any = None
    data: Any = None

    def __deepcopy__(self, memo):
        "The object and its contents are assumed to be immutable."
        return self


class BaseMemory(abc.ABC):
    """
    Base class for memory systems with textual memories.

    The memories may have attached time and any structured data, but most systems ignore those.
    Note that the system keeps track of the number of tokens of each memory in order to
    be able to e.g. limit returned historical context. Usually the default tokenizer (gpt-3.5)
    should give token counts similar to other common tokenizers, and should be fast enough not to be noticeable.
    """

    DEFAULT_COUNT_TOKENS_MODEL = "davinci"

    def __init__(self, count_tokens_model: str | Any = None):
        if not count_tokens_model:
            count_tokens_model = self.DEFAULT_COUNT_TOKENS_MODEL
        self.count_tokens_model = count_tokens_model

    def _count_tokens(self, text: str) -> int:
        return count_tokens(text, self.count_tokens_model)

    def copy(self) -> Self:
        """
        Create an independent copy of the memory state.

        Copying uses `copy.deepcopy` by default. You can simply use this implementation for
        any derived classses, unless they refer to large, effectively
        immutable objects (e.g. the weights of a local language model),
        or refer to non-copyable objects (e.g. server sockets or database connections).
        Note that those references may be indirect.

        In those cases, you may want to modify the deepcopy behavior around that object, or disable
        deep-copying of this object. See the documentation of `interlab.utis.checked_deepcopy` and the documentation
        of [`__deepcopy__`](https://docs.python.org/3/library/copy.html) for details.
        NB that overriding this method (`copy`) will not affect deep-copying of this object when contained
        in other copied objects!

        Note that individual `MemoryItem`s are already not duplicated upon copying.
        """
        return checked_deepcopy(self)

    def count_memories(self) -> int:
        """
        Return the current number of held memories.

        Note this is informational and specific to every memory implementation.
        In particular, it does not have to correspond to the number of all emories added over time.
        """
        raise NotImplementedError()

    def total_tokens(self) -> int:
        """
        Return the total number of tokens of all memories currently in memory, not including separators.

        Note this is informational and may be specific to every memory implementation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add_memory(self, memory: str, time: Any = None, data: Any = None):
        raise NotImplementedError()

    @abc.abstractmethod
    def format_memories(
        self,
        query: str = None,
        *,
        separator: str = "\n\n",
        formatter: Callable[[BaseMemoryItem], str] = None,
        item_limit: int = None,
        token_limit: int = None,
    ) -> str:
        """
        Return a string with memories, optionally relevant to the given query.

        Note that many memory systems may ignore the query - that is mostly aimed at
        associative and other advanced memory systems.
        The default behavior of the limits is to return the latest messages that fit the limit,
        or most relevant in the case of associative memory.
        """
        raise NotImplementedError()

    def _format_memories_helper(
        self,
        memories: Iterable[BaseMemoryItem],
        *,
        separator: str = "\n\n",
        formatter: Callable[[BaseMemoryItem], str] = None,
        item_limit: int = None,
        token_limit: int = None,
        priorities: np.ndarray = None,
    ) -> str:
        """
        Helper for formatting memories, used by most memory systems.

        When employing any limits, the memories are returned in their original order,
        but are selected from the end of the list (i.e. the latest memories), or from
        the ones with the highest priority when provided. Both limis can be used at the same time.
        """
        if formatter is None:
            items = [(m.memory, m.token_count) for m in memories]
        else:
            fmts = [str(formatter(m)) for m in memories]
            items = [(text, self._count_tokens(text)) for text in fmts]

        # This is in order to handle both limits and priorities, while preserving the original ordering
        include = np.ones(len(items), dtype=bool)
        if priorities is not None:
            priority_order = np.argsort(priorities)
        else:
            priority_order = np.arange(len(items))

        # Mask out all but `item_limit` highest-prority items
        if item_limit is not None:
            include[priority_order[:-item_limit]] = False

        # Mask out all but highest-prority items of up to `token_limit` tokens
        if token_limit is not None:
            tc_sep = self._count_tokens(separator)
            for i in priority_order[::-1]:
                if token_limit < items[i][1]:
                    include[i] = False
                token_limit -= items[1][1] + tc_sep

        return separator.join(item[0] for i, item in enumerate(items) if include[i])
