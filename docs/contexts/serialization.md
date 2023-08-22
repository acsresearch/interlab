# Serialization to JSON

Context can be serialized into JSON via [to_dict](pdoc:interlab.context.Context.to_dict) method:

```python
from interlab.context import Context

with Context("my context", inputs={"x": 42}) as c:
    c.set_result("my_result")
```

Calling ```c.to_dict()``` returns:

```python
{
  "_type": "Context",
  "name": "my context",
  "uid": "2023-08-23T16:41:35-my_context-Z9YpEb",
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
@dataclass
class Person:
    name: str
    age: int
    
@with_context
def say_hi(person):
    return f"Hi {person.name}!"

with Context("root") as c:
    person = Person("Alice", 21)
    say_hi(person)
```

creates the following context:

```python
{
  "_type": "Context",
  "name": "root",
  "uid": "2023-08-23T16:52:43-root-H4JCSN",
  "children": [
    {
      "_type": "Context",
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

### Method `__log_to_context__`

A user type may define method `__log_to_context__` to provide a custom serializer.

```
class Person:
    name: str
    age: int
    
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __log_to_context__(self):
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
    from interlab.context.serialization import register_custom_serializer

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