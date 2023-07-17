import dataclasses
import json
import re

import jsonref
import pydantic

JSON = dict | list | str | int | bool | float | None

_JSON_REGEXPS = [
    re.compile(r"```(?:json)?\s*({.*})\s*```", re.I | re.M | re.S),
    re.compile(r"({.*})", re.I | re.M | re.S),
]


def find_and_parse_json_block(s: str, enforce_single=False) -> JSON:
    """
    Uses several heuristics to find a chunk of valid JSON in the input text.

    Finds the JSON block first as "```"-delimited block, then just by matching first and last "{}".

    Returns the parsed JSON on success, raises ValueError on failure.

    TODO: consider only allowing "```" markers to start at the beginning of a line (after only whitespace)
    TODO(low priority): Third fallback with adding lines in reverse from last "}" until it parses as JSON.
    """
    for i, r in enumerate(_JSON_REGEXPS):
        try:
            m = r.search(s)
            if not m:
                raise ValueError("No JSON fragment found")
            if len(m.groups()) > 1 and enforce_single:
                raise ValueError("Multiple JSON fragments found")
            return json.loads(m.groups()[-1])
        except json.JSONDecodeError as e:
            if i < len(_JSON_REGEXPS) - 1:
                continue
            raise ValueError(
                "Failed to find valid JSON, candidate blocks failed parsing"
            ) from e
        except ValueError as e:
            if i < len(_JSON_REGEXPS) - 1:
                continue
            raise e


def into_pydantic_model(T: type) -> type:
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


def jsonref_deref(d: jsonref.JsonRef, check_json=True) -> JSON:
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
        # Check for a clean JSON tree (no JSONRefs)
        json.dumps(d2)
    return d2


def json_schema(T: type, strip_root=True) -> JSON:
    # pydantic schema
    schema = into_pydantic_model(T).schema()
    if strip_root:
        # remove root title and description (usually misleading to LLMs in dataclasses)
        schema.pop("title", None)
        schema.pop("description", None)
    # lazy dereferencing of $refs, converted into JSONRef
    schema_ref = jsonref.replace_refs(schema)

    # dereference all $refs, keep the old ref when recursive types are encountered
    return jsonref_deref(schema_ref)
