import contextvars
import datetime
from enum import Enum
import json
import uuid
from dataclasses import dataclass, field
from typing import Callable, Union

from .data import Data, IntoData
from .utils import LOG, QueryFailure, shorten_str

_CONTEXT_STACK = contextvars.ContextVar("_CONTEXT_STACK", default=())


class ContextState(Enum):
    NEW = 0
    OPEN = 1
    CLOSED = 2
    ERROR = 3


# Representation of a context
@dataclass
class Context:
    kind: str
    input: Data = None
    result: Data = None
    error: QueryFailure = None
    state: ContextState = ContextState.NEW
    tags: list[str] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    children: list["Context"] = field(default_factory=list)
    start_time: datetime.datetime = None
    end_time: datetime.datetime = None
    meta: dict[str, any] = field(default_factory=dict)
    _token: contextvars.Token = None
    _pad: str = None

    def to_json(self):
        others = ("kind", "tags", "uuid", "meta")
        return dict(
            _type="default",
            input=self.input.to_json() if self.input else None,
            result=self.result.to_json() if self.result else None,
            state=self.state.name,
            children=[c.to_json() for c in self.children],
            start_time=self.start_time.isoformat(),
            end_time=self.end_time.isoformat(),
            **{k: getattr(self, k) for k in others},
        )

    def __enter__(self):
        assert not self._token
        assert self.state == ContextState.NEW
        self.start_time = datetime.datetime.now()
        parents = _CONTEXT_STACK.get()
        self._pad = "  " * len(parents)
        if parents:
            parents[-1].children.append(self)
        self._token = _CONTEXT_STACK.set(parents + (self,))
        self.state = ContextState.OPEN
        LOG.debug(f"{self._pad}Context {self.kind} input={shorten_str(self.input, 50)}")
        return self

    def __exit__(self, _exc_type, exc_val, _exc_tb):
        assert self._token
        assert self.state == ContextState.OPEN
        if exc_val:
            if isinstance(exc_val, QueryFailure):
                self.set_error(exc_val)
                self.state = ContextState.ERROR
                LOG.debug(
                    f"{self._pad}-> ERR  {self.kind} err={shorten_str(exc_val, 50)}"
                )
        else:
            self.state = ContextState.CLOSED
            LOG.debug(
                f"{self._pad}-> OK   {self.kind} result={shorten_str(self.result, 50)}"
            )
        self.end_time = datetime.datetime.now()
        _CONTEXT_STACK.reset(self._token)
        self._token = None
        return False  # Propagate any exception

    def set_result(self, data: IntoData):
        self.result = Data(data)

    def set_error(self, exc: QueryFailure):
        self.error = exc
        self.result = Data(exc)

    @property
    def failed(self) -> bool:
        return isinstance(self.result, QueryFailure)


def with_new_context(
    kind_code, fn: Callable[[IntoData], IntoData], input: IntoData
) -> IntoData:
    c = Context(kind=kind_code)
    c.input = Data(input)
    with c:
        r = fn(input)
        c.set_result(r)
        return r


def test_context_saving():
    import pytest

    with Context("root") as c:
        assert c.state == ContextState.OPEN
        with Context("ch1") as c2:
            c2.set_result("blabla")
        with pytest.raises(QueryFailure, match="well"):
            with Context("ch2"):
                raise QueryFailure("Ah well")
        with_new_context("ch3", lambda d: f"Hello {d.name}", Data(name="LLM"))
    print(json.dumps(c.to_json(), indent=2))
