# Storage

InterLab storage manages serialized contexts.
The current implementation allows to store contexts as (compresed) files into a directory structure.

## Basics

Storage can be initialized by instantiating [](pdoc:interlab.context.FileStorage)

```python
from interlab.context import FileStorage

storage = FileStorage("/path/to/a/directory")
```

A context can be written manually as follows:

```python
with Context("root") as ctx:
    pass

storage.write_context(ctx)
```

Or a context can be directly created with storage:

```python
with Context("root", storage=storage):
    pass
```

The latter have advantage that context is known to the storage
from the initialization and it is visible in Data Browser even in the running state.
However, context is physically written into the persistent storage after the computation is finished.


## Storage and `with` block

Storage can be used as a context manager, in such a case all root contexts are automatically written 
into the storage.

```python
from interlab.context import FileStorage

storage = FileStorage("/path/to/a/directory")
with storage:
    with Context("root"):
        pass
```

## Directory

By default a context is stored into a single file with all its children. If `directory` flag is set to `True` then
context is stored as a directory and its children are stored in files in it (or sub-directories
when a child has also `directory` flag). 

```python
with Context("root", directory=True, storage=storage):  # <-- Stored as a dictionary
    with Context("child1"):  # <-- Stored as file
        pass
```

# Loading contexts

Contexts can be loaded from storage. 

```python
# Read all stored (root) contexts
for context in storage.read_all_contexts():
    ...

# Recursively search for specific contexts
for context in storage.find_contexts(lambda ctx: ctx.has_tag_name("hello")):
    ...

# Read a context by uid
context = storage.read_context(uid)
```