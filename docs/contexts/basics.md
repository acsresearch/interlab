# Contexts

InterLab Contexts are a framework for logging, tracing,
result storage, and visualization of nested computations and actor interactions.
They have been designed with large textual and structured (e.g. JSON) inputs and outputs in mind, as well as generic and
custom visualizations.

An instance of [Context](pdoc:interlab.context.Context) is a core object of InterLab logging infrastructure and 
represents a single (sub)task in a nested hierarchy.

The [Context](pdoc:interlab.context.Context) can be used as context manager, e.g.:

```python
from interlab.context import Context

with Context("my context", inputs={"x": 42}) as c:
    y = do_a_computation(x=42)
    c.set_result(y)
```

## Nesting contexts

Contexts can be nested and creates a hierarchy:

```python
with Context("root"):
    with Context("child-1"):
       with Context("child-1-1"):
           pass
       with Context("child-1-2"):
           pass
    with Context("child-2"):
       pass
```

If this context are visualized in [Data Browser](databrowser.md):

![Data browser screenshot](../assets/imgs/hierarchy.png)

## Context states

A context is in one of the following states: 

* *New* - Newly created Context
* *Open* - Running context
* *Finished* - Successfully finished context
* *Error* - Unsuccessfully finished context

```python
ctx = Context("my context")  # Context in NEW state
with ctx:
    # Context in OPEN state
    compute_something()    
# Context in FINISHED state
```

When an unhandled exception goes through a boundary of context then it sets context in the ERROR state. Example:

```python
with Context("my context"):
    raise Exception("Something is wrong")
# Context in ERROR state
```

Alternatively, method `.set_error` can be called on context to explicitly set a context into the ERROR state.

## Context inputs and results

Context may have one or more named inputs and at most one result.

```python
from interlab.context import Context

with Context("my context", inputs={"x": 42}) as c: # Set inputs when context is created
    c.add_inputs({"y": 123, "z": 321})  # Add inputs dynamically
    c.set_result("my_result")  # Set result explicitly
```

The name of the input has to be string.

## `with_context` decorator

A function can be annotated with [with_context](pdoc:interlab.context.with_context) decorator. It automatically
creates a new context that captures inputs and result when the function is called. 

```python
from interlab.context import with_context

@with_context
def my_computation(x):
    ...
```

## Events

An events is an instant context with immediate result and no children contexts.

```python
with Context("root") as c:
    c.add_event("Message to Alice", kind="message", data="Hi, Alice!")
```


## Tags

Tags are user-defined labels that can be attached to any Context. Later, contexts may be filtered by tags.
A tag is instance of class [`Tag`](pdoc:interlab.context.Tag). You may also provide just a string and it will be
automatically converted into a tag.

Tag may have attached a string with HTML color, that defines how the tag is shown in Data Browser.

```python
from interlab.context import Context, Tag

with Context("root", tags=["tag1", Tag("tag2")]) as c:
    c.add_tag("exp1")  # Add to a context dynamically
    c.add_tag(Tag("success!", color="lightgreen"))  # Add colored tag
```

## Meta information

A meta information can be attached to every context.
It is a dictionary with string keys. Keys and values may be user defined; however, some keys are recognized by
DataBrowser and influences how the context is rendered.

```python
with Context("root", meta={"key": "value"}) as c:
    pass
```

Interlab recognizes the following keys:

* "color": [HTML color] - The main color of the Context. In the current version, it is used for title of context and a line when context is expanded. 
* "color_bg": [HTML color] - The color of background of the Context.
* "color_border": [HTML color] - Enables a border around Context with the given color

