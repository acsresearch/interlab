import json
import re

import dirtyjson

_JSON_REGEXPS = [
    re.compile(r"```(?:json)?\s*({.*})\s*```", re.I | re.M | re.S),
    re.compile(r"({.*})", re.I | re.M | re.S),
]


def find_and_parse_json_block(s: str, enforce_single=False) -> dict:
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
            return dirtyjson.loads(m.groups()[-1])
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
