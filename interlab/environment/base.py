import abc
import copy
from typing import Sequence

from interlab.actor import BaseActor
from treetrace import TracingNode


class BaseEnvironment(abc.ABC):
    """
    This is base class for Environment.

    When subclassed you have to override the `_advance` method.

    E.g.:

    ```
    class MyEnv(BaseEnvironment):
        def __init__(self, ...):
            super().__init__([actor1, actor2])
            ...

        def _advance(self, ...):
            active = self.actors[self.steps % 2]
            other = self.actors[(self.steps + 1) % 2]

            action = active.query(...)
            ...
            active.observe("You did X, resulting in Y.")
            other.observe("The other did X, you did not see the result.")

            if ...:
                self.set_finished()
            return action # advance can return value
    ```
    """

    def __init__(self, actors: Sequence[BaseActor]):
        self._actors = list(actors)
        self._advance_counter = 0
        self._is_finished = False

    @property
    def actors(self) -> tuple[BaseActor]:
        return tuple(self._actors)

    @property
    def advance_counter(self) -> int:
        return self._advance_counter

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    def set_finished(self):
        self._is_finished = True

    def advance(self, *args, **kwargs):
        """
        Advance the environment state via `self._advance`.

        How much progress should be made is environment specific
        and can be e.g. specified by parameters).

        This is a wrapper method not supposed to be overriden - override `_advance`.
        You can pass arbitrary environment-specific arguments.
        Note that a tracing node including the step number.
        """
        if self.is_finished:
            raise Exception("Calling `advance` on a finished environment")
        name = f"{self.__class__.__name__} (advance #{self.advance_counter})"
        with TracingNode(name) as node:
            if args:
                node.add_input("args", args)
            if kwargs:
                node.add_input("kwargs", kwargs)
            result = self._advance(*args, **kwargs)
            node.set_result(result)
            self._advance_counter += 1
            return result

    def copy(self):
        """
        A deep copy of the environment, including all actors and sub-environemnts.

        You can override this method to perform e.g. copy-on-write for efficiency if appropriate.
        """
        return copy.deepcopy(self)

    # Methods to overload

    @abc.abstractmethod
    def _advance(self):
        raise NotImplementedError("Implement _advance with the environment logic.")
