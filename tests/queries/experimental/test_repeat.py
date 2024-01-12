import pytest

from interlab.queries.experimental.repeat import QueryFailure, repeat_on_failure
from tests_treetrace.testutils import strip_tree
from treetrace import TracingNode


def test_repeat_pass():
    with TracingNode("root") as root:
        result = repeat_on_failure(lambda: 123)
    assert result == 123
    assert strip_tree(root.to_dict()) == {
        "_type": "TracingNode",
        "children": [
            {
                "_type": "TracingNode",
                "kind": "repeat_on_failure",
                "name": "<lambda>: 1/3",
                "result": 123,
            }
        ],
        "name": "root",
    }


def test_repeat_fail():
    class MyException(Exception):
        pass

    def fail():
        raise MyException("MyException")

    with pytest.raises(MyException, match="MyException"):
        with TracingNode("root") as root:
            repeat_on_failure(fail)

    assert strip_tree(root.to_dict(), erase_error_details=True) == {
        "_type": "TracingNode",
        "children": [
            {
                "_type": "TracingNode",
                "error": {
                    "_type": "MyException",
                    "message": "MyException",
                    "traceback": {"_type": "$traceback"},
                },
                "kind": "repeat_on_failure",
                "name": "fail: 1/3",
                "state": "error",
            }
        ],
        "error": {
            "_type": "MyException",
            "message": "MyException",
            "traceback": {"_type": "$traceback"},
        },
        "name": "root",
        "state": "error",
    }


def test_repeat_query_fail():
    def query_fail():
        raise QueryFailure("MyFail")

    with pytest.raises(QueryFailure, match="Subqueries failed on all 3 repetitions"):
        with TracingNode("root") as root:
            repeat_on_failure(query_fail)

    assert strip_tree(root.to_dict(), erase_error_details=True) == {
        "_type": "TracingNode",
        "children": [
            {
                "_type": "TracingNode",
                "error": {
                    "_type": "QueryFailure",
                    "message": "MyFail",
                    "traceback": {"_type": "$traceback"},
                },
                "kind": "repeat_on_failure",
                "name": "query_fail: 1/3",
                "state": "error",
            },
            {
                "_type": "TracingNode",
                "error": {
                    "_type": "QueryFailure",
                    "message": "MyFail",
                    "traceback": {"_type": "$traceback"},
                },
                "kind": "repeat_on_failure",
                "name": "query_fail: 2/3",
                "state": "error",
            },
            {
                "_type": "TracingNode",
                "error": {
                    "_type": "QueryFailure",
                    "message": "MyFail",
                    "traceback": {"_type": "$traceback"},
                },
                "kind": "repeat_on_failure",
                "name": "query_fail: 3/3",
                "state": "error",
            },
        ],
        "error": {
            "_type": "QueryFailure",
            "message": "Subqueries failed on all 3 repetitions",
            "traceback": {"_type": "$traceback"},
        },
        "name": "root",
        "state": "error",
    }
