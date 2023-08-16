import base64
import mimetypes
from typing import Optional

MIME_OCTET_STREAM = "application/octet-stream"


class DataWithMime:
    def __init__(self, data: bytes, mime_type: str = MIME_OCTET_STREAM):
        """
        Wrapper around bytes that are serialized by base64.
        Data Browser renders some MIME types in a specific way
        (e.g. images are rendered directly into browser).
        """
        self.data = data
        self.mime_type = mime_type

    def __log_to_context__(self):
        return {
            "_type": "$blob",
            "data": base64.b64encode(self.data).decode(),
            "mime_type": self.mime_type,
        }


def load_file(filename: str, mime_type: Optional[str] = None) -> DataWithMime:
    if mime_type is None:
        mime_type = mimetypes.guess_type(filename, strict=False)[0] or MIME_OCTET_STREAM
    with open(filename, "rb") as f:
        return DataWithMime(f.read(), mime_type)
