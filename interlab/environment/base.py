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

    def __init__(
        self, actors: Sequence[BaseActor], parent_env: "BaseEnvironment" = None
    ):
        self._actors = list(actors)
        self._step_counter = 0
        self._result = None
        self._parent_env = parent_env

    def perform_action(self, action):
        if action.affordance.environment == self:
            return self._process_action(action)
        elif self._parent_env is None:
            raise Exception(f"Action for unknown environment: {action.environment}")
        else:
            return self._parent_env.perform_action(action)

    def _process_action(self, action):
        raise NotImplementedError()

    def is_finished(self) -> bool:
        return self._result is not None

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

    def step(self):
        if self.is_finished():
            raise Exception("Calling 'step' on finished environment")
        self._step_counter += 1
        name = f"step {self._step_counter}"
        with TracingNode(name):
            self._result = self._step()

    def run_until_end(self, max_steps: int = None, verbose=False):
        while not self.is_finished():
            if max_steps is not None:
                if max_steps <= 0:
                    return self._result
                max_steps -= 1
            if verbose:
                print("Step", self._step_counter)
            self.step()
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
    def _step(self):
        raise NotImplementedError

    def copy(self):
        env = copy(self)
        env._actors = [actor.copy() for actor in self._actors]
        return env


class DelayedEnvironment(BaseEnvironment, ABC):
    def __init__(
        self, actors: Sequence[BaseActor], parent_env: "BaseEnvironment" = None
    ):
        super().__init__(actors, parent_env)
        self.action_buffer = []

    def _process_action(self, action):
        self.action_buffer.append(action)

    def take_delayed_actions(self):
        buffer = self.action_buffer
        self.action_buffer = []
        return buffer
