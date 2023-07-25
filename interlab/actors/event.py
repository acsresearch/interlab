import json
from dataclasses import dataclass
from typing import Any

from fastapi.encoders import jsonable_encoder


@dataclass
class Event:
    # str or any JSON-serializable type
    data: Any
    # Origin of the event, usually agent name or None (if environmental observation)
    origin: str | None = None

    def data_as_string(self, json_indent=None):
        """Return the data as string for logging and passing to LLMs as text.

        This is intended as a minimal conversion to text for the above two cases; we encourage you
        to write your own serialization.
        Strings are passed thrugh, other values are JSON-encoded after pre-processing with fastapi
        `jsonable_encoder`, which handles botj JSON-like data but also dataclasses, Pydantic classes,
        datetime, etc.
        """
        if isinstance(self.data, str):
            return self.data
        return json.dumps(jsonable_encoder(self.data), indent=json_indent)

    def __str__(self) -> str:
        s = self.data_as_string()
        return f"{self.origin}: {s}" if self.origin else s


# @dataclass
# class StyledEvent(Event):
#     # Any styling data, currently only 'color' (as hex color) is supported
#     _style: dict[str, Any] = dataclasses.field(default_factory=dict)
