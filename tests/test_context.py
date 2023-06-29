import dataclasses
import json

import pytest

from querychains import Context, Tag, add_tag, with_context
from querychains.context import ContextState, get_current_context
from tests.testutils import strip_tree


def test_context_basic():
    class TestException(Exception):
        pass

    @with_context
    def func1(param1, param2):
        assert with_context(lambda x: x)("abc") == "abc"
        assert with_context(lambda x: x, name="myfn")("abc") == "abc"
        return param1 + param2

    root_ctx = Context("Test", kind="root")
    root_ctx.state = ContextState.NEW
    assert get_current_context(check=False) is None

    with root_ctx as c:
        assert c.state == ContextState.OPEN
        assert get_current_context() is c
        with Context("c1") as c2:
            c2.set_result("blabla")
        assert c2.state == ContextState.FINISHED
        with pytest.raises(TestException, match="well"):
            with Context("c2") as c2:
                assert get_current_context() is c2
                raise TestException("Ah well")
        assert c2.state == ContextState.ERROR
        assert func1(10, 20) == 30

    assert c.state == ContextState.FINISHED
    # with_new_context("ch3", lambda d: f"Hello {d.name}", Data(name="LLM"))
    print(root_ctx.to_dict())
    output = strip_tree(root_ctx.to_dict())
    print(json.dumps(output, indent=2))
    assert output == {
        "_type": "Context",
        "name": "Test",
        "kind": "root",
        "children": [
            {"_type": "Context", "name": "c1", "result": "blabla"},
            {
                "_type": "Context",
                "name": "c2",
                "state": "error",
                "error": {"_type": "error", "name": "Ah well"},
            },
            {
                "_type": "Context",
                "name": "func1",
                "kind": "call",
                "inputs": {"param1": 10, "param2": 20},
                "result": 30,
                "children": [
                    {
                        "_type": "Context",
                        "name": "<lambda>",
                        "kind": "call",
                        "inputs": {"x": "abc"},
                        "result": "abc",
                    },
                    {
                        "_type": "Context",
                        "name": "myfn",
                        "kind": "call",
                        "inputs": {"x": "abc"},
                        "result": "abc",
                    },
                ],
            },
        ],
    }


def test_context_dataclass():
    @dataclasses.dataclass
    class MyData:
        name: str
        age: int

    with Context("root") as c:
        c.add_input("my_input", MyData("Bob", 25))
        c.set_result(MyData("Alice", 26))
    assert c.state == ContextState.FINISHED
    # with_new_context("ch3", lambda d: f"Hello {d.name}", Data(name="LLM"))
    output = strip_tree(c.to_dict())
    assert output == {
        "_type": "Context",
        "name": "root",
        "inputs": {"my_input": {"_type": "MyData", "age": 25, "name": "Bob"}},
        "result": {"name": "Alice", "age": 26, "_type": "MyData"},
    }


def test_context_lists():
    with Context("root", inputs={"a": [1, 2, 3]}) as c:
        c.set_result(["A", ["B", "C"]])
    output = strip_tree(c.to_dict())
    print(output)
    assert output == {
        "_type": "Context",
        "name": "root",
        "inputs": {"a": [1, 2, 3]},
        "result": ["A", ["B", "C"]],
    }


#
# def test_context_events():
#     with Context("root") as c:
#         c.add_event("Message", {"x": 10, "y": 20})
#     output = strip_tree(c.to_dict())
#     print(json.dumps(output, indent=2))
#     assert output == {
#         "_type": "Context",
#         "name": "root",
#         "children": [
#             {
#                 "name": "Message",
#                 "data": {"x": 10, "y": 20},
#                 "_type": "Event",
#             }
#         ],
#     }
#


@pytest.mark.asyncio
async def test_async_context():
    @with_context
    async def make_queries():
        return "a"

    with Context("root") as c:
        q1 = make_queries()
        q2 = make_queries()

        await q1
        await q2

    output = strip_tree(c.to_dict())
    assert output == {
        "_type": "Context",
        "name": "root",
        "children": [
            {
                "_type": "Context",
                "name": "make_queries",
                "kind": "acall",
                "result": "a",
            },
            {
                "_type": "Context",
                "name": "make_queries",
                "kind": "acall",
                "result": "a",
            },
        ],
    }


def test_context_tags():
    with Context("root", tags=["abc", "xyz"]) as c:
        c.add_tag("123")
        with Context("child"):
            add_tag("mmm")
            add_tag(Tag("nnn", color="green"))

    root = strip_tree(c.to_dict())
    print(json.dumps(root, indent=2))
    assert root == {
        "_type": "Context",
        "name": "root",
        "tags": ["abc", "xyz", "123"],
        "children": [
            {
                "_type": "Context",
                "name": "child",
                "tags": ["mmm", {"name": "nnn", "color": "green", "_type": "Tag"}],
            }
        ],
    }
