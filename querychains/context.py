import contextvars
import datetime
import uuid
from dataclasses import dataclass, field
from typing import Callable, Union

from .utils import Data, IntoData, QueryFailure, into_data

_CONTEXT_STACK = contextvars.ContextVar("_CONTEXT_STACK")

# Representation of a context
@dataclass
class Context:
    kind: str
    input: Data = None
    result: Union[Data, QueryFailure] = None
    tags: list[str] = field(default_factory=list)
    uuid: str = field(default_factory=uuid.uuid4)
    children: list["Context"] = field(default_factory=list)
    start_time: datetime.datetime = None
    end_time: datetime.datetime = None
    meta: dict[str, any] = field(default_factory=dict)
    _token: contextvars.Token = None

    def __enter__(self):
        assert not self._token
        self.start_time = datetime.datetime.now()
        parent = _CONTEXT_STACK.get()
        if parent is not None:
            parent.children.append(self)
        self._token = _CONTEXT_STACK.set(self)

    def __exit__(self, _exc_type, exc_val, _exc_tb):
        assert self._token
        if exc_val and isinstance(exc_val, QueryFailure):
            self.result = exc_val
        self.end_time = datetime.datetime.now()
        _CONTEXT_STACK.reset(self._token)
        self._token = None
        return False  # Propagate any exception

    def set_result(self, data: IntoData):
        self.result = into_data(data)

    @property
    def failed(self) -> bool:
        return isinstance(self.result, QueryFailure)


def with_new_context(
    kind_code, fn: Callable[[IntoData], IntoData], input: IntoData
) -> IntoData:
    c = Context(kind=kind_code)
    c.input = into_data(input)
    with c:
        r = fn(input)
        c.set_result(r)
        return r
