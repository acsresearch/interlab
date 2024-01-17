import abc

from typing_extensions import Self

from interlab.utils.copying import checked_deepcopy
from treetrace import TracingNode


class BaseEnvironment(abc.ABC):
    """
    This is base class for Environment.

    When subclassed you have to override the `_advance` method.

    E.g.:

    ```
    class MyEnv(BaseEnvironment):
        def __init__(self, actor1, actor2):
            super().__init__()
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

    def __init__(self):
        self._steps_counter = 0
        self._is_finished = False

    @property
    def steps(self) -> int:
        return self._steps_counter

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    def set_finished(self):
        self._is_finished = True

    def step(self, *args, **kwargs):
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
        name = f"{self.__class__.__name__} [step {self.steps}]"
        with TracingNode(name) as node:
            if args:
                node.add_input("args", args)
            if kwargs:
                node.add_input("kwargs", kwargs)
            result = self._step(*args, **kwargs)
            node.set_result(result)
            self._steps_counter += 1
            return result

    @abc.abstractmethod
    def _step(self):
        raise NotImplementedError("Implement _step with the environment logic.")

    def copy(self) -> Self:
        """
        Create an independent copy of the environment and any contained objects (actor, sub-environments).

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
