import abc
from abc import ABC
from copy import copy
from typing import Sequence

from treetrace import TracingNode
from ..actor import BaseActor


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
        self._has_result = False
        self._result = None

    def is_finished(self) -> bool:
        return self._has_result

    def set_result(self, result):
        if self._has_result:
            raise Exception("Environment already has an result")
        self._has_result = True
        self._result = result

    @property
    def result(self):
        return self._result

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
            raise Exception("Calling 'advance' on finished environment")
        self._step_counter += 1
        name = f"step {self._step_counter}"
        with TracingNode(name):
            return self._advance()

    def run_until_end(self, max_steps: int = None, verbose=False):
        while not self.is_finished():
            if max_steps is not None:
                if max_steps <= 0:
                    return self._result
                max_steps -= 1
            if verbose:
                print("Step", self._step_counter)
            self.advance()
        return self._result

    def add_actor(self, actor):
        assert actor not in self._actors
        self._actors.append(actor)

    def remove_actor(self, actor):
        assert actor in self._actors
        self._actors.remove(actor)

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
