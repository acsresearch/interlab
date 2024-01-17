import abc
import random
from abc import ABC
from typing import Any

from typing_extensions import Self

from treetrace import HtmlColor, TracingNode, shorten_str

from ..utils.copying import checked_deepcopy
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

    def copy(self) -> Self:
        """
        Create an independent copy of the actor and its state (incl. memory).

        Copying uses `copy.deepcopy` by default. You can simply use this implementation for
        any subclassses, unless they refer to large, effectively
        immutable objects (e.g. the weights of a local language model),
        or refer to non-copyable objects (e.g. server sockets or database connections).
        Note that those references may be indirect.

        In those cases, you may want to modify the deepcopy behavior around that object, or disable
        deep-copying of this object. See the documentation of `interlab.utis.checked_deepcopy` and the documentation
        of [`__deepcopy__`](https://docs.python.org/3/library/copy.html) for details.
        NB that overriding this method (`copy`) will not affect deep-copying of this object when contained
        in other copied objects!

        Note that e.g. langchain API models are thin wrappers that are cheap to copy, and e.g.
        individual `MemoryItem`s are already not duplicated upon copying the actor and its memory.
        Also note that strings are immutable in Python and so are also not duplicated.
        """
        return checked_deepcopy(self)

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
