import pytest

from interlab import Context, QueryFailure, repeat_on_failure
from tests.testutils import strip_tree


def test_repeat_pass():
    with Context("root") as root:
        result = repeat_on_failure(lambda: 123)
    assert result == 123
    assert strip_tree(root.to_dict()) == {
        "_type": "Context",
        "children": [
            {
                "_type": "Context",
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
        with Context("root") as root:
            repeat_on_failure(fail)

    assert strip_tree(root.to_dict()) == {
        "_type": "Context",
        "children": [
            {
                "_type": "Context",
                "error": {"_type": "error", "name": "MyException"},
                "kind": "repeat_on_failure",
                "name": "fail: 1/3",
                "state": "error",
            }
        ],
        "error": {"_type": "error", "name": "MyException"},
        "name": "root",
        "state": "error",
    }


def test_repeat_query_fail():
    def query_fail():
        raise QueryFailure("MyFail")

    with pytest.raises(QueryFailure, match="Subqueries failed on all 3 repetitions"):
        with Context("root") as root:
            repeat_on_failure(query_fail)

    assert strip_tree(root.to_dict()) == {
        "_type": "Context",
        "children": [
            {
                "_type": "Context",
                "error": {"_type": "error", "name": "MyFail"},
                "kind": "repeat_on_failure",
                "name": "query_fail: 1/3",
                "state": "error",
            },
            {
                "_type": "Context",
                "error": {"_type": "error", "name": "MyFail"},
                "kind": "repeat_on_failure",
                "name": "query_fail: 2/3",
                "state": "error",
            },
            {
                "_type": "Context",
                "error": {"_type": "error", "name": "MyFail"},
                "kind": "repeat_on_failure",
                "name": "query_fail: 3/3",
                "state": "error",
            },
        ],
        "error": {"_type": "error", "name": "Subqueries failed on all 3 repetitions"},
        "name": "root",
        "state": "error",
    }
