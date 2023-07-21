from dataclasses import dataclass

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
        raise Exception()

    assert json_querying.query_for_json(eng, Foo, "TEST_A")
