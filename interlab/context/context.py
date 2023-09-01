import contextvars
import datetime
import functools
import inspect
import logging
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from ..utils.text import generate_uid, shorten_str
from ..version import VERSION
from .serialization import Data, serialize_with_type

CONTEXT_FORMAT_VERSION = "1.0"

_LOG = logging.getLogger(__name__)

_CONTEXT_STACK = contextvars.ContextVar("_CONTEXT_STACK", default=())


class ContextState(Enum):
    """
    An enumeration representing the state of a context.
    """

    NEW = "new"
    """The context has been created but has not started yet."""
    OPEN = "open"
    """The context is currently running."""
    FINISHED = "finished"
    """The context has successfully finished execution."""
    ERROR = "error"
    """The context finished with an exception."""


@dataclass
class Tag:
    """
    A simple class representing a tag that can be applied to a context. Optionally with style information.
    """

    name: str
    """The name of the tag; any short string."""
    color: Optional[str] = None
    """HTML hex color code, e.g. `#ff0000`."""

    @staticmethod
    def into_tag(obj: Union[str, "Tag"]) -> "Tag":
        if isinstance(obj, Tag):
            return obj
        if isinstance(obj, str):
            return Tag(obj)
        raise Exception(f"Object {obj!r} cannot be converted into Tag")


class Context:
    """
    A context object that represents a single request or (sub)task in a nested hierarchy.

    The class has several attributes that are intended as read-only; use setters to modify them.

    The `Context` can be used as context manager, e.g.:

    ```python
    with Context("my context", inputs={"z": 42}) as c:
        c.add_input("x", 1)
        y = do_some_computation(x=1)
        # The context would also note any exceptions raised here
        # (letting it propagate upwards), but a result needs to be set manually:
        c.set_result(y)
    # <- Here the context is already closed.
    ```
    """

    def __init__(
        self,
        name: str,
        kind: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Data]] = None,
        tags: Optional[Sequence[str | Tag]] = None,
        storage: Optional["StorageBase"] = None,
        directory=False,
        result=None,
    ):
        """
        - `name` - A description or name for the context.
        - `kind` - Indicates category of the context, may e.g. influence display of the context.
        - `inputs` - A dictionary of inputs for the context.
        - `meta` - A dictionary of any metadata for the context, e.g. UI style data.
        - `tags` - A list of tags for the context
        - `storage` - A storage object for the context. Set on the root context to log all contexts below it.
        - `directory` - Whether to create a sub-directory for the context while storing.
          This allows you to split the stored data across multiple files.
        - `result` - The result value of the context, if it has already been computed.
        """

        if storage is None and current_context(False) is None:
            storage = current_storage()

        if inputs:
            assert isinstance(inputs, dict)
            assert all(isinstance(key, str) for key in inputs)
            inputs = serialize_with_type(inputs)

        if meta:
            meta = serialize_with_type(meta)

        if result:
            result = serialize_with_type(result)

        if tags is not None:
            tags = [Tag.into_tag(tag) for tag in tags]

        self.name = name
        self.kind = kind
        self.inputs = inputs
        self.result = result
        self.error = None
        self.state: ContextState = (
            ContextState.NEW if result is None else ContextState.FINISHED
        )
        self.uid = generate_uid(name)
        self.children: List[Context] = []
        self.tags: List[Tag] = tags
        self.start_time = None
        self.end_time = None if result is None else datetime.datetime.now()
        self.meta = meta
        self.storage = storage
        self.directory = directory
        self._token = None
        self._depth = 0
        self._lock = Lock()

        if storage:
            storage.register_context(self)

    @classmethod
    def deserialize(cls, data: Data, depth=0):
        """
        Deserialize a `Context` object from given JSON data.

        - `data` - A dictionary containing the serialized context data.
        """
        assert isinstance(data, dict)
        assert data["_type"] == "Context"
        self = cls.__new__(cls)
        self.uid = data["uid"]
        self.name = data["name"]

        state = data.get("state")
        if state:
            state = ContextState(state)
        else:
            state = ContextState.FINISHED
        self.state = state
        for name in ["kind", "inputs", "result", "error", "tags", "meta"]:
            setattr(self, name, data.get(name))
        self.kind = data.get("kind")
        self.inputs = data.get("inputs")
        self.tags = data.get("tags")

        start_time = data.get("start_time")
        if start_time is None:
            self.start_time = None
        else:
            self.start_time = datetime.datetime.fromisoformat(start_time)

        end_time = data.get("end_time")
        if end_time is None:
            self.end_time = None
        else:
            self.end_time = datetime.datetime.fromisoformat(end_time)

        children = data.get("children")
        if children is None:
            self.children = None
        else:
            new_depth = depth + 1
            self.children = [
                Context.deserialize(child, depth=new_depth) for child in children
            ]

        self._token = None
        self._depth = depth
        self._lock = Lock()
        return self

    def to_dict(self, with_children=True, root=True):
        """
        Serialize `Context` object into JSON structure.

        - `with_children` - If True then children are recursively serialized.
                            If False then serialization of children is skipped and only
                            children UIDs are put into key `children_uids`
        """
        with self._lock:
            result = {"_type": "Context", "name": self.name, "uid": self.uid}
            if root:
                result["version"] = CONTEXT_FORMAT_VERSION
                result["interlab"] = VERSION
            if self.state != ContextState.FINISHED:
                result["state"] = self.state.value
            for name in ["kind", "result", "error", "tags"]:
                value = getattr(self, name)
                if value is not None:
                    result[name] = value
            if self.inputs:
                result["inputs"] = self.inputs
            if with_children and self.children:
                result["children"] = [c.to_dict(root=False) for c in self.children]
            if not with_children and self.children:
                result["children_uids"] = [c.uid for c in self.children]
            if self.start_time:
                result["start_time"] = self.start_time.isoformat()
            if self.end_time:
                result["end_time"] = self.end_time.isoformat()
            if self.meta:
                result["meta"] = self.meta
            if self.tags:
                result["tags"] = serialize_with_type(self.tags)
            return result

    @property
    def _pad(self):
        return " " * self._depth

    def __enter__(self):
        def _helper(depth):
            with self._lock:
                assert not self._token
                assert self.state == ContextState.NEW
                self.start_time = datetime.datetime.now()
                self._depth = depth
                self._token = _CONTEXT_STACK.set(parents + (self,))
                self.state = ContextState.OPEN
                _LOG.debug(
                    f"{self._pad}Context {self.kind} inputs={shorten_str(self.inputs, 50)}"
                )

        # First we need to get Lock from parent to not get in collision
        # with to_dict() that goes down the tree
        parents = _CONTEXT_STACK.get()
        if parents:
            parent = parents[-1]
            with parent._lock:  # noqa
                _helper(len(parents))
                parent.children.append(self)
        else:
            _helper(0)
        return self

    def __exit__(self, _exc_type, exc_val, _exc_tb):
        with self._lock:
            assert self._token
            assert self.state == ContextState.OPEN
            if exc_val:
                # Do not call set_error here as it takes a lock
                self.state = ContextState.ERROR
                self.error = serialize_with_type(exc_val)
                _LOG.debug(
                    f"{self._pad}-> ERR  {self.kind} error={shorten_str(exc_val, 50)}"
                )
            else:
                self.state = ContextState.FINISHED
                _LOG.debug(
                    f"{self._pad}-> OK   {self.kind} result={shorten_str(repr(self.result), 50)}"
                )
            self.end_time = datetime.datetime.now()
            _CONTEXT_STACK.reset(self._token)
            self._token = None
        if self.storage:
            self.storage.write_context(self)
        return False  # Propagate any exception

    def add_tag(self, tag: str | Tag):
        """
        Add a tag to the context.
        """
        with self._lock:
            if self.tags is None:
                self.tags = [Tag.into_tag(tag)]
            else:
                self.tags.append(Tag.into_tag(tag))

    def add_event(
        self,
        name: str,
        kind: Optional[str] = None,
        data: Optional[Any] = None,
        meta: Optional[Dict[str, Data]] = None,
        tags: Optional[List[str | Tag]] = None,
    ) -> "Context":
        event = Context(name=name, kind=kind, result=data, meta=meta, tags=tags)
        with self._lock:
            self.children.append(event)
        return event

    def add_input(self, name: str, value: object):
        """
        Add a named input value to the context.

        If an input of the same name already exists, an exception is raised.
        """
        with self._lock:
            if self.inputs is None:
                self.inputs = {}
            if name in self.inputs:
                raise Exception(f"Input {name} already exists")
            self.inputs[name] = serialize_with_type(value)

    def add_inputs(self, inputs: dict[str, object]):
        """
        Add a new input values to the context.

        If an input of the same name already exists, an exception is raised.
        """
        with self._lock:
            if self.inputs is None:
                self.inputs = {}
            for name in inputs:
                if name in self.inputs:
                    raise Exception(f"Input {name} already exists")
            for name, value in inputs.items():
                self.inputs[name] = serialize_with_type(value)

    def set_result(self, value: Any):
        """
        Set the result value of the context.
        """
        with self._lock:
            self.result = serialize_with_type(value)

    def set_error(self, exc: Any):
        """
        Set the error value of the context (usually an `Exception` instance).
        """
        with self._lock:
            self.state = ContextState.ERROR
            self.error = serialize_with_type(exc)

    def has_tag_name(self, tag_name: str):
        """
        Returns `True` if the context has a tag with the given name.
        """
        if not self.tags:
            return False
        for tag in self.tags:
            if tag == tag_name or (isinstance(tag, Tag) and tag.name == tag_name):
                return True
        return False

    def find_contexts(self, predicate: Callable) -> List["Context"]:
        """
        Find all contexts matching the given callable `predicate`.

        The predicate is called with a single argument, the `Context` to check, and should return `bool`.
        """

        def _helper(context: Context):
            with context._lock:
                if predicate(context):
                    result.append(context)
                if context.children:
                    for ctx in context.children:
                        _helper(ctx)

        result = []
        _helper(self)
        return result


def with_context(
    fn: Callable = None, *, name=None, kind=None, tags: Optional[List[str | Tag]] = None
):
    """
    A decorator wrapping every execution of the function in a new `Context`.

    The `inputs`, `result`, and `error` (if any) are set automatically.
    Note that you can access the created context in your function using `current_context`.

    *Usage:*

    ```python
    @with_context
    def func():
        pass

    @with_context(name="custom_name", kind="custom_kind", tags=['tag1', 'tag2'])
    def func():
        pass
    ```
    """
    if isinstance(fn, str):
        raise TypeError("use `with_context()` with explicit `name=...` parameter")
    name = name or fn.__name__

    def helper(func):
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*a, **kw):
            binding = signature.bind(*a, **kw)
            with Context(
                name=name, kind=kind or "call", inputs=binding.arguments, tags=tags
            ) as ctx:
                result = func(*a, **kw)
                ctx.set_result(result)
                return result

        async def async_wrapper(*a, **kw):
            binding = signature.bind(*a, **kw)
            with Context(
                name=name, kind=kind or "acall", inputs=binding.arguments
            ) as ctx:
                result = await func(*a, **kw)
                ctx.set_result(result)
                return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    if fn is not None:
        assert callable(fn)
        return helper(fn)
    else:
        return helper


def current_context(check: bool = True) -> Optional[Context]:
    """
    Returns the inner-most open context, if any.

    Throws an error if `check` is `True` and there is no current context. If `check` is `False` and there is
    no current context, it returns `None`.
    """
    stack = _CONTEXT_STACK.get()
    if not stack:
        if check:
            raise Exception("No current context")
        return None
    return stack[-1]


# Solving circular dependencies
from .storage import StorageBase, current_storage  # noqa
