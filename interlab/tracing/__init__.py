"""
This module provides the TracingNode class, tracing log storage, logged data and parameter
serialization specialized for several data types (dataclasses, pydantic, etc),
and several special types that allow custom display of parts of any
serialized value (including deep in nested structures).

The objects with custom visualization in `data` submodule include images, custom HTML,
and tracking f-string-like substitution in string templates (with `FormatStr`).
"""


from . import tracingnode, data, storage  # noqa: F401
from .tracingnode import TracingNode, Tag, current_tracing_node, with_tracing
from .storage import FileStorage, StorageBase

__all__ = [
    "data",
    "TracingNode",
    "Tag",
    "current_tracing_node",
    "with_tracing",
    "FileStorage",
    "StorageBase",
]
