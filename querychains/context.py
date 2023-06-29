import contextvars
import datetime
import inspect
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from threading import Lock
from dataclasses import dataclass

from .data import Data, serialize_with_type
from .utils import LOG, generate_uid, shorten_str

_CONTEXT_STACK = contextvars.ContextVar("_CONTEXT_STACK", default=())


class ContextState(Enum):
    NEW = "new"
    OPEN = "open"
    FINISHED = "finished"
    ERROR = "error"


class Event:
    def __init__(
        self, name: str, kind: Optional[str] = None, data: Optional[Any] = None
    ):
        self.name = name
        self.kind = kind
        self.data = data
        self.time = datetime.datetime.now()

    def to_dict(self):
        result = {
            "_type": "Event",
            "name": self.name,
            "time": self.time.isoformat(),
        }
        if self.kind:
            result["kind"] = self.kind
        if self.data:
            result["data"] = self.data


@dataclass
class Tag:
    name: str
    color: str


class Context:
    def __init__(
        self,
        name: str,
        kind: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Data]] = None,
        tags: Optional[List[str | Tag]] = None,
        storage: Optional["Storage"] = None,
        directory=False,
    ):
        if inputs:
            inputs = serialize_with_type(inputs)
        if meta:
            meta = serialize_with_type(meta)

        self.name = name
        self.kind = kind
        self.inputs = inputs
        self.result = None
        self.error = None
        self.state: ContextState = ContextState.NEW
        self.uid = generate_uid(name)
        self.children: List[Event, Context] = []
        self.tags = tags
        self.start_time = None
        self.end_time = None
        self.meta = meta
        self.storage = storage
        self.directory = directory
        self._token = None
        self._depth = 0
        self._lock = Lock()

        if storage:
            storage.register_context(self)

    def to_dict(self, with_children=True):
        with self._lock:
            result = {"_type": "Context", "name": self.name, "uid": self.uid}
            if self.state != ContextState.FINISHED:
                result["state"] = self.state.value
            for name in ["kind", "inputs", "result", "error", "tags"]:
                value = getattr(self, name)
                if value:
                    result[name] = value
            if with_children and self.children:
                result["children"] = [c.to_dict() for c in self.children]
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
                LOG.debug(
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
                LOG.debug(
                    f"{self._pad}-> ERR  {self.kind} error={shorten_str(exc_val, 50)}"
                )
            else:
                self.state = ContextState.FINISHED
                LOG.debug(
                    f"{self._pad}-> OK   {self.kind} result={shorten_str(repr(self.result), 50)}"
                )
            self.end_time = datetime.datetime.now()
            _CONTEXT_STACK.reset(self._token)
            self._token = None
        if self.storage:
            self.storage.write_context(self)
        return False  # Propagate any exception

    def add_tag(self, tag: str | Tag):
        with self._lock:
            if self.tags is None:
                self.tags = [tag]
            else:
                self.tags.append(tag)

    def add_event(
        self, name: str, kind: Optional[str] = None, data: Optional[Any] = None
    ) -> Event:
        with self._lock:
            event = Event(name=name, data=data, kind=kind)
            self.children.append(event)
            return event

    def add_input(self, name: str, value: any):
        with self._lock:
            if self.inputs is None:
                self.inputs = {}
            if name in self.inputs:
                raise Exception(f"Input {name} already exists")
            self.inputs[name] = serialize_with_type(value)

    def set_result(self, value: any):
        with self._lock:
            self.result = serialize_with_type(value)

    def set_error(self, exc: any):
        with self._lock:
            self.state = ContextState.ERROR
            self.error = serialize_with_type(exc)


def with_context(fn: Callable = None, *, name=None, kind=None):
    name = name or fn.__name__

    def helper(func):
        signature = inspect.signature(func)

        def wrapper(*a, **kw):
            binding = signature.bind(*a, **kw)
            with Context(
                name=name, kind=kind or "call", inputs=binding.arguments
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


def get_current_context(check: bool = True) -> Optional[Context]:
    stack = _CONTEXT_STACK.get()
    if not stack:
        if check:
            raise Exception("No current context")
        return None
    return stack[-1]


def add_event(
    name: str, kind: Optional[str] = None, data: Optional[Any] = None
) -> Event:
    return get_current_context().add_event(name, kind=kind, data=data)


def add_tag(tag: str | Tag):
    return get_current_context().add_tag(tag)


# Solving circular dependencies
from .storage import Storage  # noqa
