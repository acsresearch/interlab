import html
import inspect
from typing import TYPE_CHECKING, Iterable

from .event import Event

if TYPE_CHECKING:
    from .actor import Actor


class FormatBase:
    def format_event(self, event: Event, observer: "Actor") -> any:
        "Format the given Event for the given Actor. To be overriden in subclasses."
        raise NotImplementedError("Use one of the subclasses")

    def format_events(self, events: Iterable[Event], observer: "Actor") -> any:
        "Format and join the given Events for the given Actor. To be overriden in subclasses."
        raise NotImplementedError("Use one of the subclasses")


class FunFormat(FormatBase):
    """
    Generic wrapper for a formatter defined by function (lambda).
    The function can take 1 or 2 parameters (event, observing_actor).
    """

    def __init__(self, fun: callable):
        self.fun = fun
        self.argnum = len(inspect.signature(self.fun).parameters)

    def format_event(self, event: Event, observer: "Actor") -> any:
        "Format the given Event for the given Actor using the provided function."
        if self.argnum == 1:
            return self.fun(event)
        return self.fun(event, observer)


class TextFormat(FormatBase):
    "Abstract base for plaintext-based formatters"
    JOIN_STR = "\n\n"

    def format_events(self, events: Iterable[Event], observer: "Actor") -> any:
        "Format events and join them with `JOIN_STR` (\\n\\n by default)."
        return self.JOIN_STR.join(self.format_event(e, observer) for e in events)


class LLMTextFormat(TextFormat):
    "Default plaintext-based formatter for LLMs"

    def format_event(self, event: Event, observer: "Actor") -> str:
        s = event.data_as_string()
        if event.origin is not None:
            return f"{event.origin}: {s}"
        return s


class HumanTextFormat(TextFormat):
    "Default plaintext-based formatter for human actors and observers"

    def format_event(self, event: Event, observer: "Actor") -> str:
        s = event.data_as_string(json_indent=2)
        if event.origin is not None:
            return f"{event.origin}:\n{s}"
        return s


class HTMLFormat(TextFormat):
    "Default HTML-based formatter for human actors and observers"

    def format_event(self, event: Event, observer: "Actor") -> str:
        s = f"<code>{html.escape(event.data_as_string(json_indent=2))}</code>"
        if event.origin is not None:
            return f"<span>{html.escape(event.origin)}:</span> {s}"
        return s
