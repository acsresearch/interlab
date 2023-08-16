import dataclasses
import traceback
from typing import Any, Callable, Dict, List, TypeVar

import numpy as np

Data = Dict[str, "Data"] | List["Data"] | int | float | str | bool | None

PRIMITIVES = (int, str, float, bool)


def _serialize_ndarray(obj):
    return {
        "shape": obj.shape,
        "values": obj.tolist(),
    }


CUSTOM_SERIALIZERS = {np.ndarray: _serialize_ndarray}


def _dataclass_serialize_helper(pairs):
    return {key: serialize_with_type(value) for key, value in pairs}


def check_type_key(serialized, obj):
    if isinstance(serialized, dict) and "_type" not in obj:
        serialized["_type"] = type(obj).__name__


def _serialize_exception(exc: BaseException) -> Data:
    result = {
        "_type": exc.__class__.__name__,
        "message": str(exc),
        "traceback": {
            "_type": "$traceback",
            "frames": [
                {
                    "name": t.name,
                    "filename": t.filename,
                    "lineno": t.lineno,
                    "line": t.line,
                }
                for t in traceback.extract_tb(exc.__traceback__)
            ],
        },
    }

    if exc.__context__:
        result["context"] = _serialize_exception(exc.__context__)

    return result


def serialize_with_type(obj: Any) -> Data:
    if obj is None:
        return None
    if isinstance(obj, PRIMITIVES):
        return obj
    if isinstance(obj, BaseException):
        return _serialize_exception(obj)
    if isinstance(obj, list) or isinstance(obj, tuple):
        return [serialize_with_type(value) for value in obj]
    if isinstance(obj, dict):
        return {key: serialize_with_type(value) for key, value in obj.items()}
    serializer = CUSTOM_SERIALIZERS.get(obj.__class__)
    if serializer is not None:
        serialized = serializer(obj)
        if "_type" not in serialized:
            serialized["_type"] = type(obj).__name__
        return serialized
    if hasattr(obj, "__log_to_context__"):
        serialized = obj.__log_to_context__()
        if isinstance(serialized, dict) and "_type" not in serialized:
            serialized["_type"] = type(obj).__name__
        return serialized
    if dataclasses.is_dataclass(obj):
        serialized = dataclasses.asdict(obj, dict_factory=_dataclass_serialize_helper)
        if "_type" not in serialized:
            serialized["_type"] = type(obj).__name__
        return serialized
    return {"_type": type(obj).__name__, "id": id(obj)}


def serializer_with_type(cls, obj) -> Data:
    return serialize_with_type(obj)


T = TypeVar("T")


def register_custom_serializer(cls: type[T], serialize_fn: Callable[[T], Data]):
    CUSTOM_SERIALIZERS[cls] = serialize_fn


def unregister_custom_serializer(cls):
    CUSTOM_SERIALIZERS.pop(cls, None)
