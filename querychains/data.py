from typing import Dict, List

import serde

Data = Dict[str, "Data"] | List["Data"] | int | float | str | bool


def serialize_with_type(obj: any) -> Data:
    if isinstance(obj, Exception):
        return {"_type": "error", "name": str(obj)}
    if isinstance(obj, list) or isinstance(obj, tuple):
        return [serialize_with_type(value) for value in obj]
    if isinstance(obj, dict):
        return {key: serialize_with_type(value) for key, value in obj.items()}
    serialized = serde.to_dict(obj)
    if isinstance(serialized, dict) and "_type" not in serialized:
        serialized["_type"] = type(obj).__name__
    return serialized


def serializer_with_type(cls, obj) -> Data:
    return serialize_with_type(obj)
