"""
This module provides the Context class, context log storage, logged data and parameter
serialization specialized for several data types (dataclasses, pydantic, etc),
and several special types that allow custom display of parts of any
serialized value (including deep in nested structures).

The objects with custom visualization in `data` submodule include images, custom HTML,
and tracking f-string-like substitution in string templates (with `FormatStr`).
"""


from . import context, data, storage  # noqa: F401
from .context import Context, Tag, current_context, with_context
from .storage import FileStorage, StorageBase

__all__ = [
    "data",
    "Context",
    "Tag",
    "current_context",
    "with_context",
    "FileStorage",
    "StorageBase",
]
