import abc
from typing import Any, Iterable

from ..event import Event


class FormatBase(abc.ABC):
    @abc.abstractmethod
    def format_event(self, event: Event) -> Any:
        "Format the given Event for the given Actor. To be overriden in subclasses."
        raise NotImplementedError("Use one of the subclasses")

    @abc.abstractmethod
    def format_events(self, events: Iterable[Event]) -> Any:
        "Format and join the given Events for the given Actor. To be overriden in subclasses."
        raise NotImplementedError("Use one of the subclasses")

    def __call__(self, ev: Event | Iterable[Event]) -> Any:
        "Forwarded to self.format_event(ev) or self.format_events(ev)"
        if isinstance(ev, Event):
            return self.format_event(ev)
        elif isinstance(ev, Iterable):
            return self.format_events(ev)
        else:
            raise TypeError(
                f"only Event or iterable of events can be formatted, got {ev.__class__}"
            )


class TextFormat(FormatBase):
    "Abstract base for plaintext-based formatters"
    JOIN_STR = "\n\n"

    def format_events(self, events: Iterable[Event]) -> Any:
        "Format events and join them with `JOIN_STR` (\\n\\n by default)."
        return self.JOIN_STR.join(self.format_event(e) for e in events)


class LLMTextFormat(TextFormat):
    "Default plaintext-based formatter for LLMs"

    def format_event(self, event: Event) -> str:
        s = event.data_as_string()
        return f"{event.origin}: {s}" if event.origin is not None else s


class HumanTextFormat(TextFormat):
    "Default plaintext-based formatter for human actors and observers"

    def format_event(self, event: Event) -> str:
        s = event.data_as_string()
        # If the answer is a longer JSON, display over multiple lines
        if len(s) > 60 and not isinstance(event.data, str):
            s = event.data_as_string(json_indent=2)
        return f"{event.origin}: {s}" if event.origin is not None else s
