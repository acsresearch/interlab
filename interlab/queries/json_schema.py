import dataclasses
import json
from typing import Any

import jsonref
import pydantic


def get_pydantic_model(T: type) -> type:
    """
    Convert the type to pydantic BaseModel.
    """
    if not issubclass(T, pydantic.BaseModel):
        if not dataclasses.is_dataclass(T):
            raise TypeError(
                "Only pydantic Model, or pydantic or standard dataclasses are accepted"
            )
        T = pydantic.dataclasses.create_pydantic_model_from_dataclass(T)
    assert issubclass(T, pydantic.BaseModel)  # In lieu of a test
    return T


def deref_jsonref(d: jsonref.JsonRef, check_json=True) -> Any:
    """
    Recursively replace JSONRef nested structure with normal dicts.

    Removes the "definitions" root field. Raises ValueError for recursive references.
    Checks the result to be valid json without refs (this may be skipped).
    NOTE: Could be improved to also work for recursive types with more work.
    """

    def _rec(a, seen_ids):
        # JSONRef instance to be replaced
        if isinstance(a, jsonref.JsonRef):
            assert isinstance(a, dict), "Only $refs to dicts are resolved now"
            if id(a) in seen_ids:
                raise ValueError("Can't dereference recursive JSON")
            return {k: _rec(v, seen_ids + (id(a),)) for k, v in a.items()}
        # Other containers: dict, list
        elif isinstance(a, dict):
            return {k: _rec(v, seen_ids) for k, v in a.items()}
        elif isinstance(a, list):
            return [_rec(v, seen_ids) for v in a]
        # Scalar types
        else:
            return a

    d2 = _rec(d, seen_ids=())
    d2.pop("definitions", None)
    if check_json:
        # Check for a clean JSON tree (e.g. no JSONRefs)
        json.dumps(d2)
    return d2


def get_json_schema(T: type, strip_root=True) -> Any:
    # pydantic schema
    schema = get_pydantic_model(T).schema()
    if strip_root:
        # remove root title and description (usually misleading to LLMs in dataclasses)
        schema.pop("title", None)
        schema.pop("description", None)
    # lazy dereferencing of $refs, converted into JSONRef
    schema_ref = jsonref.replace_refs(schema)

    # dereference all $refs, keep the old ref when recursive types are encountered
    return deref_jsonref(schema_ref)
