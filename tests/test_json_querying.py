import re
from dataclasses import dataclass
from functools import partial

import pytest

from interlab.llm import json_querying


@dataclass
class Foo:
    z: bool = True
    x: int = 0
    y: list[str] | None = None


FOO_SCHEMA_RE = r"```json\s*\n\s*{'type':\s*'object',\s'properties':\s{'z':"


@pytest.mark.parametrize("with_example", [False, Foo(z=False, x=33, y=["a", "b"])])
def test_query_for_json(with_example=False):
    def eng(q):
        if "TEST_A" in q:
            return "heh {'z': \"0\"} zzz"
        if "TEST_B" in q:
            return "```{'z': \"0\", 'x': 33}``` {'z': 1}"
        if "TEST_C" in q:
            assert re.search(FOO_SCHEMA_RE, q, re.MULTILINE)
            return "{'x':3}"
        raise Exception()

    query_for_json = partial(json_querying.query_for_json, with_example=with_example)

    assert query_for_json(eng, Foo, "TEST_A") == Foo(z=False)
    assert query_for_json(eng, Foo, "{absent} TEST_B {FORMAT_PROMPT} zzz") == Foo(
        z=False, x=33
    )
    with pytest.raises(ValueError):
        query_for_json(eng, Foo, "{FORMAT_PROMPT} TEST_A {FORMAT_PROMPT}")
    query_for_json(eng, Foo, "zzz {FORMAT_PROMPT}TEST_C") == Foo(x=3)
    query_for_json(eng, Foo, "TEST_C") == Foo(x=3)
