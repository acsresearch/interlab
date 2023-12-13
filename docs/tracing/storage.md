# Storage

InterLab storage manages serialized tracing nodes.
The current implementation allows to store nodes as (compresed) files into a directory structure.

## Basics

Storage can be initialized by instantiating [](pdoc:interlab.tracing.FileStorage)

```python
from interlab.tracing import FileStorage

storage = FileStorage("/path/to/a/directory")
```

A node can be written manually as follows:

```python
with TracingNode("root") as ctx:
    pass

storage.write_node(ctx)
```

Or a node can be directly created with storage:

```python
with TracingNode("root", storage=storage):
    pass
```

The latter have advantage that the node is known to the storage
from the initialization and it is visible in Data Browser even in the running state.
However, node is physically written into the persistent storage after the computation is finished.


## Storage and `with` block

Storage can be used as a context manager, in such a case all root nodes are automatically written
into the storage.

```python
from interlab.tracing import FileStorage

storage = FileStorage("/path/to/a/directory")
with storage:
    with TracingNode("my root"):
        pass
```

## Directory

By default a node is stored into a single file with all its children. If `directory` flag is set to `True` then
the node is stored as a directory and its children are stored in files in it (or sub-directories
when a child has also `directory` flag).

```python
with TracingNode("root", directory=True, storage=storage):  # <-- Stored as a dictionary
    with TracingNode("child1"):  # <-- Stored as file
        pass
```

# Loading tracing nodes

Tracing nodes can be loaded from storage.

```python
# Read all stored (root) nodes
for node in storage.read_all_nodes():
    ...

# Recursively search for specific tracing nodes
for node in storage.find_nodes(lambda ctx: ctx.has_tag_name("hello")):
    ...

# Read a tracing node by uid
node = storage.read_node(uid)
```