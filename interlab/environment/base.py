import abc
from copy import copy
from typing import Sequence

from interlab.actor import BaseActor
from treetrace import TracingNode


class BaseEnvironment(abc.ABC):
    """
    This is base class for Environment.

    When subclassed you have to override "_step" method.
    By default, "copy" method makes a shallow copy of other argument added by subclasss.
    If shallow copy is not enough you have to override also "copy":

    E.g.:

    class MyEnv(BaseEnvironment):
        def __init__(self, ...):
            ...
            self.my_list = []

        ...

        def copy(self):
            env = super().copy()
            env.my_list = self.my_list[:]
            return env
    """

    def __init__(self, actors: Sequence[BaseActor]):
        self._actors = list(actors)
        self._step_counter = 0
        self._is_finished = False

    def is_finished(self) -> bool:
        return self._is_finished

    @property
    def n_actors(self) -> int:
        return len(self._actors)

    @property
    def actors(self) -> tuple[BaseActor]:
        return tuple(self._actors)

    @property
    def current_step(self) -> int:
        return self._step_counter

    def advance(self):
        if self.is_finished():
            raise Exception("Calling 'step' on finished environment")
        self._step_counter += 1
        name = f"step {self._step_counter}"
        with TracingNode(name) as node:
            result = self._advance()
            node.set_result(result)
            return result

    def run_until_end(self, max_steps: int = None):
        while not self.is_finished():
            if max_steps is not None:
                if max_steps <= 0:
                    return self._is_finished
                max_steps -= 1
            self.advance()
        return self._is_finished

    def set_finished(self):
        self._is_finished = True

    def everyone_observe(self, observation, origin=None):
        for actor in self.actors:
            actor.observe(observation, origin)

    # Methods to overload

    @abc.abstractmethod
    def _advance(self):
        raise NotImplementedError

    def copy(self):
        env = copy(self)
        env._actors = [actor.copy() for actor in self._actors]
        return env
