from dataclasses import dataclass
from typing import Any

import numpy as np

from interlab.context.serialization import (
    register_custom_serializer,
    serialize_with_type,
    unregister_custom_serializer,
)


def test_log_to_context():
    class MyClass:
        def __init__(self):
            self.x = "hi!"

        def __log_to_context__(self):
            return {"attr": self.x}

    class MyOtherClass:
        pass

    @dataclass
    class Root:
        my_class: MyClass
        my_other_class: MyOtherClass
        other: Any

    r = Root(my_class=MyClass(), my_other_class=MyOtherClass(), other=lambda: 0)
    output = serialize_with_type(r)
    assert isinstance(output["my_other_class"].pop("id"), int)
    assert isinstance(output["other"].pop("id"), int)

    assert output == {
        "_type": "Root",
        "my_class": {"_type": "MyClass", "attr": "hi!"},
        "my_other_class": {"_type": "MyOtherClass"},
        "other": {"_type": "function"},
    }


def test_custom_serializer():
    class MyClass:
        def __init__(self, x):
            self.x = x

    def serializer(m: MyClass):
        return {"abc": "MySerializer", "x": m.x}

    register_custom_serializer(MyClass, serializer)
    try:
        mm = MyClass(123)
        output = serialize_with_type(mm)
        print(output)
        assert output == {"abc": "MySerializer", "x": 123, "_type": "MyClass"}
    finally:
        unregister_custom_serializer(MyClass)


def test_serialize_ndarray():
    array = np.array([[1.2, 2.3, 4.5], [0.0, 0.0, 1.0]])
    assert serialize_with_type(array) == {
        "_type": "ndarray",
        "shape": (2, 3),
        "values": [[1.2, 2.3, 4.5], [0.0, 0.0, 1.0]],
    }
