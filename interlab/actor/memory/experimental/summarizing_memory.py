import warnings
from dataclasses import KW_ONLY, dataclass
from typing import Any

import numpy as np

from interlab.queries import count_tokens, summarize_with_limit
from treetrace import TracingNode, current_tracing_node, shorten_str

from ..list_memory import BaseMemoryItem, ListMemory

_LOG = __import__("logging").getLogger(__name__)


@dataclass(frozen=True)
class SummarizingMemoryItem(BaseMemoryItem):
    _: KW_ONLY
    tokens: int = 0
    level: int = 0


class SummarizingMemory(ListMemory):
    def __init__(
        self,
        model: Any,
        token_limit=2000,
        one_message_limit=500,
        summary_limit=250,
    ):
        super().__init__()
        self.model = model
        self.token_limit = token_limit
        self.one_message_limit = one_message_limit
        self.summary_limit = summary_limit

    def total_tokens(self) -> int:
        """Upper-bound of total tokens of the memory text (including separator newlines etc.)."""
        return sum(i.tokens for i in self.items)

    def copy(self) -> "SummarizingMemory":
        m = SummarizingMemory(
            model=self.model,
            token_limit=self.token_limit,
            one_message_limit=self.one_message_limit,
            summary_limit=self.summary_limit,
        )
        m.items = list(self.items)
        return m

    def summarize(self):
        """
        Perform one step of summarization, decreasing the total token count.

        May need to be run repeatedly.
        """
        # First, are there any non-last long level-0 items?
        for i, item in enumerate(self.items[:-1]):
            if item.level == 0 and item.tokens > self.summary_limit:
                # Found one; summarize it
                msg = (
                    f"summarize: shortening {item.tokens} token message to {self.summary_limit}: "
                    f"{shorten_str(item.memory)!r}"
                )
                _LOG.debug(msg)
                current_tracing_node().add_event(msg)
                item.memory = summarize_with_limit(
                    item.memory,
                    model=self.model,
                    token_limit=self.summary_limit - 5,
                )
                item.tokens = count_tokens(item.memory, self.model) + 5
                return

        # Find most abundant level and summarize two consecutive items of that level
        # (or that level and the following item, in sme extreme situations)
        level_counts = [0] * 20
        for i, item in enumerate(self.items[:-1]):
            level_counts[item.level] += 1
        summary_level = np.argmax(level_counts)

        # Find the first item of that level
        for i, item in enumerate(self.items[:-1]):
            if item.level == summary_level:
                i1, i2 = self.items[i : i + 2]
                msg = (
                    f"summarize: summarizing {i1.tokens} tokens (level {i1.level}) and {i2.tokens} tokens "
                    f"(level {i2.level}) messages to {self.summary_limit} tokens"
                )
                _LOG.debug(msg)
                current_tracing_node().add_event(msg)
                text = summarize_with_limit(
                    f"{i1.memory}\n\n{i2.memory}",
                    model=self.model,
                    token_limit=self.summary_limit - 5,
                )
                tokens = count_tokens(text, self.model)
                self.items[i : i + 2] = [
                    SummarizingMemoryItem(
                        memory=text,
                        tokens=tokens + 5,
                        level=max(i1.level, i2.level) + 1,
                        time=i1.time,
                    )
                ]

                return
        raise Exception("Error: summarization failed")

    def add_memory(self, memory: str, time: Any = None, data: Any = None):
        with TracingNode(
            "SummarizingMemory.add_memory",
            inputs=dict(memory=memory, time=time),
            kind="debug",
        ) as c:
            if not isinstance(memory, str):
                warnings.warn(
                    f"{self.__type__.__name__} converts all memories to str (got {type(memory)})."
                )
            if data is not None:
                warnings.warn(
                    f"{self.__type__.__name__} discards memory `data` field but got nonempty `data`."
                )

            text = str(memory)
            tokens = count_tokens(text, self.model)  # Estimate for newlines etc.
            if tokens > self.one_message_limit:
                msg = f"add_event: shortening {tokens} token message to {self.one_message_limit}: {shorten_str(text)!r}"
                c.add_event(msg)
                _LOG.debug(msg)
                text = summarize_with_limit(
                    text,
                    model=self.model,
                    token_limit=self.one_message_limit - 5,
                )
                tokens = count_tokens(text, self.model)  # Estimate for newlines etc.

            self.items.append(
                SummarizingMemoryItem(text, tokens=tokens + 5, level=0, time=time)
            )
            while self.total_tokens() > self.token_limit:
                self.summarize()
