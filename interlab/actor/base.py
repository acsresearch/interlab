import abc
import random
from abc import ABC
from copy import copy
from typing import Any, Sequence, Type

from treetrace import TracingNode, HtmlColor, shorten_str
from .affordance import Affordance
from . import memory as memory_module
from .event import Event
from .memory import format


class BaseActor(abc.ABC):
    """
    Interface for generic actor, to be used with LLMs, game theory or otherwise.

    Override methods _query and _observe in derived classes.

    Note: The interface is intentionally not async (for now, for usability reasons),
    use multi-threading for parallel inquiries. (Helpers for this are WIP.)
    """

    def __init__(self, name: str = None, *, style: dict[str, Any] = None):
        self.name = name
        if self.name is None:
            self.name = f"{self.__class__.__name__}{random.randint(0, 9999):i04}"
        self.style = style if style is not None else {}
        if self.style.get("color") is None:
            self.style["color"] = str(
                HtmlColor.random_color(self.name, saturation=0.5, lighness=0.3)
            )

    def copy(self):
        raise NotImplementedError

    def act(
        self,
        affordances: Sequence[Affordance],
        *,
        prompt: Any = None,
        **kwargs,
    ) -> Event:
        """Calls self._act to determine the action, wraps the action in Event, and wraps the call in TracingNode.
        Query does not modify the actor's memory. Call .observe(event) on actor if agent should observe the result.
        """
        if prompt:
            name = f"{self.name} acts, prompt: {text.shorten_str(str(prompt))!r}"
            inputs = {"prompt": prompt}
        else:
            name = f"{self.name} acts"
            inputs = {}
        if affordances is not None:
            inputs["affordances"] = [aff.name for aff in affordances]
        inputs.update(**kwargs)

        with TracingNode(name, kind="action", meta=self.style, inputs=inputs) as ctx:
            action = self._act(prompt=prompt, affordances=affordances, **kwargs)
            ctx.set_result(action)
            # TODO: Consider conversion to expected_type (if a Pydantic type) or type verification
        return action

    def query(
        self,
        prompt: Any = None,
        *,
        expected_type: Type | None = None,
        **kwargs,
    ) -> Event:
        """Calls self._query to determine the action, wraps the action in Event, and wraps the call in TracingNode.
        Query does not modify the actor's memory. Call .observe(event) on actor if agent should observe the result.
        """
        if prompt:
            name = f"{self.name} acts, prompt: {shorten_str(str(prompt))!r}"
            inputs = {"prompt": prompt}
        else:
            name = f"{self.name} acts"
            inputs = {}
        if expected_type is not None:
            inputs[
                "expected_type"
            ] = f"{expected_type.__module__}.{expected_type.__qualname__}"
        inputs.update(**kwargs)

        with TracingNode(name, kind="action", meta=self.style, inputs=inputs) as ctx:
            action = self._query(prompt, expected_type=expected_type, **kwargs)
            ctx.set_result(action)
            # TODO: Consider conversion to expected_type (if a Pydantic type) or type verification
            ev = Event(origin=self.name, data=action)
        return ev

    @abc.abstractmethod
    def _query(self, prompt: Any = None, **kwargs) -> Any:
        raise NotImplementedError("Implement _query in a derived actor class")

    @abc.abstractmethod
    def _act(
        self, affordances: Sequence[Affordance], prompt: Any = None, **kwargs
    ) -> Any:
        raise NotImplementedError("Implement _act in a derived actor class")

    def observe(self, event: Event | Any, origin: str | None = None):
        """Observe the given Event.

        Instead of given Event object, you can also pass in observation and origin directly.
        """
        if not isinstance(event, Event):
            event = Event(data=event, origin=origin)
        with TracingNode(
            f"{self.name} observes {shorten_str(str(event))!r}",
            kind="observation",
            meta=self.style,
            inputs={"origin": event.origin, "observation": event.data},
        ):
            self._observe(event)

    @abc.abstractmethod
    def _observe(self, event: Event):
        raise NotImplementedError("Implement _observe in a derived actor class")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class ActorWithMemory(BaseActor, ABC):
    """
    Actor with an instance of MemoryBase recording all observations.

    You still need to implement _query if you inherit from this actor.
    """

    DEFAULT_FORMAT = format.DefaultTextFormat
    DEFAULT_MEMORY = memory_module.ListMemory

    def __init__(self, name=None, *, memory: memory_module.BaseMemory = None, **kwargs):
        super().__init__(name, **kwargs)
        self.memory = memory
        if self.memory is None:
            self.memory = self.DEFAULT_MEMORY(format=self.DEFAULT_FORMAT())

    def _observe(self, event: Event):
        self.memory.add_event(event)

    def copy(self):
        actor = copy(self)
        actor.memory = self.memory.copy()
        return actor
