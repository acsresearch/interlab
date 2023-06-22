from dataclasses import dataclass
from typing import Any

from querychains.data import serialize_with_type


def test_custom_serialize():
    class MyClass:
        def __init__(self):
            self.x = "hi!"

        def __log__(self):
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
