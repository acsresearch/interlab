# Serialization to JSON

`TracingNode` can be serialized into JSON via [to_dict](pdoc:treetrace.TracingNode.to_dict) method:

```python
from treetrace import TracingNode

with TracingNode("my node", inputs={"x": 42}) as node:
    node.set_result("my_result")
```

Calling ```node.to_dict()``` returns:

```python
{
  "_type": "TracingNode",
  "name": "my node",
  "uid": "2023-08-23T16-41-35-my_node-Z9YpEb",
  "inputs": {
    "x": 42
  },
  "result": "my_result",
  "start_time": "2023-08-23T16:41:35.811159",
  "end_time": "2023-08-23T16:41:35.811210"
}
```

When inputs or a result are not directly serializable into JSON options are provided:

### Serialization of dataclasses

Dataclasses are serialized as `dict`:

```python
from dataclasses import dataclass
from treetrace import TraceNode, with_trace

@dataclass
class Person:
    name: str
    age: int

@with_trace
def say_hi(person):
    return f"Hi {person.name}!"

with TracingNode("root") as c:
    person = Person("Alice", 21)
    say_hi(person)
```

creates the following JSON description of the node:

```python
{
  "_type": "TracingNode",
  "name": "root",
  "uid": "2023-08-23T16:52:43-root-H4JCSN",
  "children": [
    {
      "_type": "TracingNode",
      "name": "say_hi",
      "uid": "2023-08-23T16:52:43-say_hi-GGfCCe",
      "kind": "call",
      "result": "Hi Alice!",
      "inputs": {
        "person": {                     # <<<<
          "name": "Alice",              # <<<<
          "age": 21,                    # <<<<
          "_type": "Person"             # <<<<
        }
      },
      "start_time": "2023-08-23T16:52:43.115548",
      "end_time": "2023-08-23T16:52:43.115572"
    }
  ],
  "start_time": "2023-08-23T16:52:43.115449",
  "end_time": "2023-08-23T16:52:43.115585"
}
```

### Method `__trace_to_node__`

A user type may define method `__trace_to_node__` to provide a custom serializer.

```python
class Person:
    name: str
    age: int

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __trace_to_node__(self):
        return {"name": self.name, "age": self.age}

person = Person("Peter", 24)
```

When `person` is serialized, the following dictionary is produced:

```python
{
    "name": "Peter",
    "age": 24,
    "_type": "Person"
}
```

### Registration of serializer

Sometimes we do not or we cannot modify a class. Registration a serializer for a given type is there for this purpose.

```python
from treetrace import register_custom_serializer


class MyClass:
    def __init__(self, x):
        self.x = x


def myclass_serializer(m: MyClass):
    return {"x": m.x}


register_custom_serializer(MyClass, myclass_serializer)
```

### Fallback

When no mechanism above is used then only name of the type and object `id` is serialized.

E.g.:

```python
{
    "_type": "Person",
    "id": 140263930622832
}
```