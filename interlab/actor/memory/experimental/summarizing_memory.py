from dataclasses import dataclass
from typing import Any

import numpy as np

from interlab.actor.event import Event
from interlab.context import Context, current_context
from interlab.lang_models.count_tokens import count_tokens
from interlab.queries.summarize import summarize_with_limit
from interlab.utils.text import shorten_str

from ..list_memory import ListMemory

_LOG = __import__("logging").getLogger(__name__)


@dataclass
class _SummarizingMemoryItem:
    text: str
    tokens: int
    level: int = 0


class SummarizingMemory(ListMemory):
    def __init__(
        self,
        model: Any,
        token_limit=2000,
        one_message_limit=500,
        summary_limit=250,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.model = model
        self.token_limit = token_limit
        self.one_message_limit = one_message_limit
        self.summary_limit = summary_limit
        self.items = []

    def total_tokens(self) -> int:
        """Upper-bound of total tokens of the memory text (including separator newlines etc.)."""
        return sum(i.tokens for i in self.items)

    def summarize(self):
        """
        Perform one step of summarization, decreaasing the total token count.

        May need to be run repeatedly."""
        # First, are there any non-last long level-0 items?
        for i, item in enumerate(self.items[:-1]):
            if item.level == 0 and item.tokens > self.summary_limit:
                # Found one; summarize it
                msg = (
                    f"summarize: shortening {item.tokens} token message to {self.summary_limit}: "
                    f"{shorten_str(item.text)!r}"
                )
                _LOG.debug(msg)
                current_context().add_event(msg)
                item.text = summarize_with_limit(
                    item.text,
                    model=self.model,
                    token_limit=self.summary_limit - 5,
                )
                item.tokens = count_tokens(item.text, self.model) + 5
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
                current_context().add_event(msg)
                text = summarize_with_limit(
                    f"{i1.text}\n\n{i2.text}",
                    model=self.model,
                    token_limit=self.summary_limit - 5,
                )
                tokens = count_tokens(text, self.model)
                self.items[i : i + 2] = [
                    _SummarizingMemoryItem(
                        text, tokens + 5, level=max(i1.level, i2.level) + 1
                    )
                ]

                return
        raise Exception("Bug: summarization failed")

    def add_event(self, event: Event | str):
        with Context("SummarizingMemory.add_event", inputs=dict(event=event)) as c:
            text = str(event)
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

            self.items.append(_SummarizingMemoryItem(text, tokens + 5))
            while self.total_tokens() > self.token_limit:
                self.summarize()

    def get_events(self, query: Any = None) -> tuple[Event]:
        assert query is None, "Query not supported by this memory"
        return tuple(Event(i.text) for i in self.items)
