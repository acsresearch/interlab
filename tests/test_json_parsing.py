import json
from dataclasses import dataclass

import jsonref
import pytest

from interlab.llm import json_parsing


def test_find_and_parse_json_block():
    assert json_parsing.find_and_parse_json_block('{"b":42}') == {"b": 42}
    assert json_parsing.find_and_parse_json_block("a ```json\n\n{ } ```") == {}
    assert json_parsing.find_and_parse_json_block("```\n\n{ } ``` zz") == {}
    assert json_parsing.find_and_parse_json_block(
        'asd```json\n{"a":1}\n```{\n"b":2\n}da\nsd'
    ) == {"a": 1}
    with pytest.raises(ValueError):
        json_parsing.find_and_parse_json_block(
            'asddf ``` json\n\n\n{"a":1}\n```{\n"b":2\n} da\nsd'
        )
    assert json_parsing.find_and_parse_json_block(
        'asd{"a":"```json\\n{a:1}\\n```"}zzz'
    ) == {"a": "```json\n{a:1}\n```"}


BAZ_SCHEMA = """{
    "type": "object",
    "properties": {"q": {"$ref": "#/definitions/Bar"}},
    "definitions": {
        "Foo": { "type": "object", "properties": {"x": {"type": "integer"}}},
        "Bar": { "type": "object", "properties": {"f": {"$ref": "#/definitions/Foo"}}}
    }
}"""

BAZ_SCHEMA_DEREF = """{
    "properties": {
        "q": {"properties": {
            "f": {"properties": {
                "x": {"type": "integer"}},
            "type": "object"}},
        "type": "object"}},
    "type": "object"
}"""

REC_SCHEMA = """{
    "type": "object",
    "properties": {"q": {"$ref": "#/definitions/Rec"}},
    "definitions": {
        "Rec": {
            "type": "object",
            "properties": {"f": {"$ref": "#/definitions/Rec"}}
        }
    }
}"""


def test_jsonref_deref():
    baz_schema = jsonref.loads(BAZ_SCHEMA)
    assert json_parsing.jsonref_deref(baz_schema) == json.loads(BAZ_SCHEMA_DEREF)
    rec_schema = jsonref.loads(REC_SCHEMA)
    with pytest.raises(ValueError):
        json_parsing.jsonref_deref(rec_schema)


@dataclass
class A:
    x: int = 42


@dataclass
class B:
    f: A | None


B_SCHEMA_DEREF_FULL = """{
    "type": "object", "properties": {
        "f": {"title": "A", "type": "object", "properties": {
            "x": {"title": "X", "default": 42, "type": "integer"}}}},
    "required": ["f"]
}"""


def test_json_schema():
    sch = json_parsing.json_schema(B)
    print(json.dumps(sch))
    assert sch == json.loads(B_SCHEMA_DEREF_FULL)
    with pytest.raises(TypeError):
        json_parsing.json_schema(str)
