import copy
import dataclasses
import json

import pytest

from treetrace import TracingNode, Tag, current_tracing_node, with_trace
from treetrace.tracing.tracingnode import TracingNodeState
from tests_treetrace.testutils import strip_tree


def serialization_check(node: TracingNode):
    d = node.to_dict()
    assert d == TracingNode.deserialize(d).to_dict()


def test_tracing_node_basic():
    class TestException(Exception):
        pass

    @with_trace
    def func1(param1, param2):
        assert with_trace(lambda x: x)("abc") == "abc"
        assert with_trace(lambda x: x, name="myfn")("abc") == "abc"
        return param1 + param2

    root_node = TracingNode("Test", kind="root")
    serialization_check(root_node)
    assert root_node.state == TracingNodeState.NEW
    assert current_tracing_node(check=False) is None

    with root_node as c:
        assert c.state == TracingNodeState.OPEN
        assert current_tracing_node() is c
        with TracingNode("c1") as c2:
            c2.set_result("blabla")
        assert c2.state == TracingNodeState.FINISHED
        with pytest.raises(TestException, match="well"):
            with TracingNode("c2") as c2:
                assert current_tracing_node() is c2
                serialization_check(c2)
                raise TestException("Ah well")
        assert c2.state == TracingNodeState.ERROR
        assert func1(10, 20) == 30

    assert c.state == TracingNodeState.FINISHED
    serialization_check(c)
    output = strip_tree(root_node.to_dict())

    print(json.dumps(output, indent=2))
    assert output == {
        "_type": "TracingNode",
        "name": "Test",
        "kind": "root",
        "children": [
            {"_type": "TracingNode", "name": "c1", "result": "blabla"},
            {
                "_type": "TracingNode",
                "name": "c2",
                "state": "error",
                "error": {
                    "_type": "TestException",
                    "message": "Ah well",
                    "traceback": {
                        "_type": "$traceback",
                        "frames": [
                            {
                                "name": "test_tracing_node_basic",
                                "filename": __file__,
                                "line": 'raise TestException("Ah well")',
                            }
                        ],
                    },
                },
            },
            {
                "_type": "TracingNode",
                "name": "func1",
                "kind": "call",
                "inputs": {"param1": 10, "param2": 20},
                "result": 30,
                "children": [
                    {
                        "_type": "TracingNode",
                        "name": "<lambda>",
                        "kind": "call",
                        "inputs": {"x": "abc"},
                        "result": "abc",
                    },
                    {
                        "_type": "TracingNode",
                        "name": "myfn",
                        "kind": "call",
                        "inputs": {"x": "abc"},
                        "result": "abc",
                    },
                ],
            },
        ],
    }


def test_tracing_node_inner_exception():
    def f1():
        raise Exception("Exception 1")

    def f2():
        try:
            f1()
        except Exception:
            raise Exception("Exception 2")

    with pytest.raises(Exception):
        with TracingNode("root") as c:
            f2()

    output = strip_tree(c.to_dict())
    print(json.dumps(output, indent=2))
    assert output == {
        "_type": "TracingNode",
        "name": "root",
        "state": "error",
        "error": {
            "_type": "Exception",
            "message": "Exception 2",
            "traceback": {
                "_type": "$traceback",
                "frames": [
                    {
                        "name": "test_tracing_node_inner_exception",
                        "filename": __file__,
                        "line": "f2()",
                    },
                    {
                        "name": "f2",
                        "filename": __file__,
                        "line": 'raise Exception("Exception 2")',
                    },
                ],
            },
            "tracing": {
                "_type": "Exception",
                "message": "Exception 1",
                "traceback": {
                    "_type": "$traceback",
                    "frames": [
                        {
                            "name": "f2",
                            "filename": __file__,
                            "line": "f1()",
                        },
                        {
                            "name": "f1",
                            "filename": __file__,
                            "line": 'raise Exception("Exception 1")',
                        },
                    ],
                },
            },
        },
    }


def test_tracing_dataclass():
    @dataclasses.dataclass
    class MyData:
        name: str
        age: int

    with TracingNode("root") as c:
        c.add_input("my_input", MyData("Bob", 25))
        c.set_result(MyData("Alice", 26))
    assert c.state == TracingNodeState.FINISHED
    # with_new_context("ch3", lambda d: f"Hello {d.name}", Data(name="LLM"))
    output = strip_tree(c.to_dict())
    assert output == {
        "_type": "TracingNode",
        "name": "root",
        "inputs": {"my_input": {"_type": "MyData", "age": 25, "name": "Bob"}},
        "result": {"name": "Alice", "age": 26, "_type": "MyData"},
    }


def test_tracing_node_add_inputs():
    class A:
        pass

    a = A()

    with TracingNode("root") as c:
        with TracingNode("child1") as c2:
            c2.add_inputs({"x": 10, "y": a})
        with TracingNode("child1", inputs={"z": 20}) as c2:
            c2.add_inputs({"x": 10, "y": a})
    output = strip_tree(c.to_dict())
    print(output)
    assert output == {
        "_type": "TracingNode",
        "name": "root",
        "children": [
            {
                "_type": "TracingNode",
                "name": "child1",
                "inputs": {"x": 10, "y": {"_type": "A", "id": id(a)}},
            },
            {
                "_type": "TracingNode",
                "name": "child1",
                "inputs": {
                    "z": 20,
                    "x": 10,
                    "y": {"_type": "A", "id": id(a)},
                },
            },
        ],
    }


def test_tracing_node_lists():
    with TracingNode("root", inputs={"a": [1, 2, 3]}) as c:
        c.set_result(["A", ["B", "C"]])
    output = strip_tree(c.to_dict())
    print(output)
    assert output == {
        "_type": "TracingNode",
        "name": "root",
        "inputs": {"a": [1, 2, 3]},
        "result": ["A", ["B", "C"]],
    }


def test_tracing_node_events():
    with TracingNode("root") as c:
        c.add_event("Message to Alice", kind="message", data={"x": 10, "y": 20})
    output = strip_tree(c.to_dict())
    print(json.dumps(output, indent=2))
    assert output == {
        "_type": "TracingNode",
        "name": "root",
        "children": [
            {
                "_type": "TracingNode",
                "name": "Message to Alice",
                "kind": "message",
                "result": {"x": 10, "y": 20},
            }
        ],
    }


@pytest.mark.asyncio
async def test_async_tracing_node():
    @with_trace
    async def make_queries():
        return "a"

    with TracingNode("root") as c:
        q1 = make_queries()
        q2 = make_queries()

        await q1
        await q2

    output = strip_tree(c.to_dict())
    assert output == {
        "_type": "TracingNode",
        "name": "root",
        "children": [
            {
                "_type": "TracingNode",
                "name": "make_queries",
                "kind": "acall",
                "result": "a",
            },
            {
                "_type": "TracingNode",
                "name": "make_queries",
                "kind": "acall",
                "result": "a",
            },
        ],
    }


def test_tracing_node_tags():
    with TracingNode("root", tags=["abc", "xyz"]) as c:
        c.add_tag("123")
        with TracingNode("child"):
            current_tracing_node().add_tag("mmm")
            current_tracing_node().add_tag(Tag("nnn", color="green"))

    data = c.to_dict()
    root = strip_tree(copy.deepcopy(data))
    assert root == {
        "_type": "TracingNode",
        "name": "root",
        "tags": [
            {"name": "abc", "color": None, "_type": "Tag"},
            {"name": "xyz", "color": None, "_type": "Tag"},
            {"name": "123", "color": None, "_type": "Tag"},
        ],
        "children": [
            {
                "_type": "TracingNode",
                "name": "child",
                "tags": [
                    {"name": "mmm", "color": None, "_type": "Tag"},
                    {"name": "nnn", "color": "green", "_type": "Tag"},
                ],
            }
        ],
    }
    print(json.dumps(data, indent=2))
    root2 = TracingNode.deserialize(data).to_dict()
    assert data == root2


def test_find_tracing_nodes():
    with TracingNode("root") as c:
        c.add_tag("123")
        with TracingNode("child"):
            with TracingNode("child3") as c3:
                c3.add_tag("x")
                c3.set_result("abc")
        with TracingNode("child2", tags=[Tag("x")]) as c4:
            pass

    assert c.find_nodes(lambda ctx: ctx.has_tag_name("x")) == [c3, c4]


@pytest.mark.parametrize(
    "result",
    [pytest.param(None, id="None"), pytest.param("", id='""'), 0, 1, "abc", {"x": 10}],
)
def test_to_dict(result):
    with TracingNode("root") as c:
        c.set_result(result)
    assert c.result == result

    c_dict = c.to_dict()
    for key, c_dict_val in c_dict.items():
        if key.startswith("_") or key == "version" or key == "interlab":
            # ignore private attributes or version attributes
            continue
        c_val = getattr(c, key)
        if type(c_val) not in (int, float, str, bool, list, dict, type(None)):
            # only check attributes which are json serializable
            continue
        assert c_dict_val == c_val
