import dataclasses
import json
from dataclasses import dataclass


@dataclass
class Event:
    # str or any JSON-serializable type
    data: any
    # Origin of the event, usually agent name or None (if environmental observation)
    origin: str | None = None
    # Any styling data, currently only 'color' (as hex color) is supported
    style: dict[str, any] = dataclasses.field(default_factory=dict)

    def data_as_string(self, json_indent=None):
        "Return the data as JSON string (for dataclasses) or its __str__ representation (otherwise)."
        if dataclasses.is_dataclass(self.data):
            return json.dumps(dataclasses.asdict(self.data), indent=json_indent)
        # TODO(gavento): better handle primitive containers (e.g. list of dataclasses)
        return str(self.data)

    def __str__(self) -> str:
        if self.origin:
            return f"{self.origin}: {str(self.data)}"
        return str(self.data)
