import html
from typing import TYPE_CHECKING, Any, Iterable

from .event import Event


class FormatBase:
    def format_event(self, event: Event) -> Any:
        "Format the given Event for the given Actor. To be overriden in subclasses."
        raise NotImplementedError("Use one of the subclasses")

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

    def format_events(self, events: Iterable[Event]) -> any:
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


class HTMLFormat(TextFormat):
    CLASS_NAME_PREFIX = "InterLabHTMLFormat"
    "Default HTML-based formatter for human actors and observers"

    def format_events(self, events: Iterable[Event]) -> any:
        s = "\n".join(self.format_event(e) for e in events)
        return f'<div class="{self.CLASS_NAME_PREFIX}__box">\n{s}\n</div>'

    def format_event(self, event: Event) -> str:
        # Only for events with _style attribute (optional, API not quite resolved)
        if hasattr(event, "_style") and "color" in event._style:
            css_style = f'style="color: color-mix({event._style["color"]}, 50% black)'
        else:
            css_style = ""

        s = event.data_as_string()
        if isinstance(event.data, str):
            fs = f'<span class="{self.CLASS_NAME_PREFIX}__text" {css_style}">{html.escape(s)}</span>'
        else:
            # If the answer is a longer JSON, display over multiple lines
            if len(s) > 60:
                s = event.data_as_string(json_indent=2)
            fs = f'<code class="{self.CLASS_NAME_PREFIX}__json" {css_style}>{html.escape(s)}</code>'

        if event.origin is not None:
            fs = f'<span class="{self.CLASS_NAME_PREFIX}__origin">{html.escape(event.origin)}:</span> {fs}'
        return f'<div class="{self.CLASS_NAME_PREFIX}__message">{fs}:</div>'
