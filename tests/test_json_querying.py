from dataclasses import dataclass

import pytest

from interlab.llm import json_querying


@dataclass
class Foo:
    z: bool
    x: int = 0
    y: list[str] | None = None


def test_query_for_json():
    def eng(q):
        if "TEST_A" in q:
            return "heh {'z': \"0\"} zzz"
        if "TEST_B" in q:
            return "```{'z': \"0\", 'x': 33}``` {'z': 1}"
        raise Exception()

    assert json_querying.query_for_json(eng, Foo, "TEST_A") == Foo(z=False)
    assert json_querying.query_for_json(
        eng, Foo, "{absent} TEST_B {FORMAT_PROMPT} zzz"
    ) == Foo(z=False, x=33)
    with pytest.raises(ValueError):
        json_querying.query_for_json(eng, Foo, "{FORMAT_PROMPT} TEST_A {FORMAT_PROMPT}")
