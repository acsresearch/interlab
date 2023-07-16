import dataclasses
import json
from dataclasses import dataclass
from typing import Any


@dataclass
class Event:
    # str or any JSON-serializable type
    data: Any
    # Origin of the event, usually agent name or None (if environmental observation)
    origin: str | None = None

    def data_as_string(self, json_indent=None):
        "Return the data as JSON string (for dataclasses) or its __str__ representation (otherwise)."
        if dataclasses.is_dataclass(self.data):
            return json.dumps(dataclasses.asdict(self.data), indent=json_indent)
        # TODO(gavento): better handle primitive containers (e.g. list of dataclasses)
        return str(self.data)

    def __str__(self) -> str:
        s = self.data_as_string()
        return f"{self.origin}: {s}" if self.origin else s


# @dataclass
# class StyledEvent(Event):
#     # Any styling data, currently only 'color' (as hex color) is supported
#     _style: dict[str, Any] = dataclasses.field(default_factory=dict)
    