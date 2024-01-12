import abc
import random
from abc import ABC
from copy import copy
from typing import Any

from treetrace import HtmlColor, TracingNode, shorten_str

from . import memory as memory_module


class BaseActor(abc.ABC):
    """
    Interface for generic actor, to be used with LLMs, game theory or otherwise.

    Override methods _query and _observe in derived classes.

    Note: The interface is intentionally not async (for usability reasons), use multi-threading for parallel inquiries.
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
        """
        Full copy of the actor and all its data (memories etc.).

        The copy must be independent from the original instance. May be copy-on-write for efficiency, or via
        serialization/deserialization.
        """
        raise NotImplementedError()

    def query(self, prompt: Any = None, *, expected_type=None, **kwargs) -> Any:
        """
        Query the actor for an answer to prompt, optionally requesting a dataclass.

        Prompt may be a string in case of LLM actors, or any structure in game-theoretic and other contexts.
        In case of LLM agents, this can be used both for taking actions and asking auxiliary questions.
        In general, query does not update the agent of its own answers or actions - use `observe` for that!
        """
        if prompt:
            name = f"{self.name} queried with {shorten_str(str(prompt))!r}"
            inputs = {"prompt": prompt}
        else:
            name = f"{self.name} queried"
            inputs = {}
        if expected_type is not None:
            inputs[
                "expected_type"
            ] = f"{expected_type.__module__}.{expected_type.__qualname__}"
        inputs.update(**kwargs)

        with TracingNode(name, kind="action", meta=self.style, inputs=inputs) as ctx:
            reply = self._query(prompt, expected_type=expected_type, **kwargs)
            # TODO: Consider conversion to expected_type (if a Pydantic type) or type verification
            ctx.set_result(reply)
        return reply

    @abc.abstractmethod
    def _query(self, prompt: Any = None, **kwargs) -> Any:
        raise NotImplementedError("Implement _query in a derived actor class")

    def observe(self, observation: str | Any, time: Any = None, data: Any = None):
        """
        Update the agent with an observation.

        In general, the observation should be from the point of view of the actor.
        This is especially relevant in the case of LLMs: The observation may be e.g.
        "Bob sent you this message: ..." or "You wrote Alice this email: ...".

        Note that The `observation` is interpreted as str by many agents and memory systems.
        Non-str observations may

        `time` and `data` are optional user-attributes preserved but ignored by many algorithms,
        though e.g. time may be relevant for associative memory.
        """
        inputs = {"observation": observation}
        if data is not None:
            inputs["data"] = data
        if time is not None:
            inputs["time"] = time
        msg = f"{self.name} observed {shorten_str(str(observation))!r}"
        with TracingNode(msg, kind="observation", meta=self.style, inputs=inputs):
            self._observe(observation, time=time, data=data)

    @abc.abstractmethod
    def _observe(self, observation: str | Any, time: Any = None, data: Any = None):
        raise NotImplementedError("Implement _observe in a derived actor class")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class ActorWithMemory(BaseActor, ABC):
    """
    Actor with an instance of MemoryBase recording all observations in their memory.

    Agents with memory inject the context of their memories to all `query` calls.
    You still need to implement _query if you inherit from this actor.
    """

    DEFAULT_MEMORY = memory_module.ListMemory

    def __init__(self, name=None, *, memory: memory_module.BaseMemory = None, **kwargs):
        super().__init__(name, **kwargs)
        if memory is None:
            memory = self.DEFAULT_MEMORY()
        self.memory = memory

    def _observe(self, observation: str | Any, time: Any = None, data: Any = None):
        self.memory.add_memory(observation, time=time, data=data)

    def copy(self):
        actor = copy(self)  # TODO(gavento): this seems hacky
        actor.memory = self.memory.copy()
        return actor
