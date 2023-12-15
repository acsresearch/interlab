import abc
from copy import copy
from typing import Any, Sequence

from interlab.actor import BaseActor
from interlab.tracing import TracingNode


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

    If environment has a distinguished "actor" each step, you may override "current_actor",
    to get coloring of tracing for the step from this actor.

    You may also override "current_step_style" to set style for step tracing.
    """

    def __init__(self, actors: Sequence[BaseActor]):
        self._actors = list(actors)
        self._step_counter = 0
        self._result = None

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
    def current_step_id(self) -> int:
        return self._step_counter

    def step(self):
        if self.is_finished():
            raise Exception("Calling 'step' on finished environment")
        self._step_counter += 1
        name = f"step {self._step_counter}"
        actor = self.current_actor()
        if actor is not None:
            name += f"; {actor.name}"
        with TracingNode(name, meta=self.current_step_style()):
            self._result = self._step()

    def run_until_end(self, max_steps: int = None, verbose=False):
        while not self.is_finished():
            if max_steps is not None:
                if max_steps <= 0:
                    self._result
                max_steps -= 1
            if verbose:
                print("Step", self._step_counter)
            self.step()
        return self._result

    def everyone_observe(self, observation, origin=None):
        for actor in self.actors:
            actor.observe(observation, origin)

    # Methods to overload

    @abc.abstractmethod
    def _step(self):
        raise NotImplementedError

    def current_actor(self) -> None | BaseActor:
        return None

    def current_step_style(self) -> None | dict[str, Any]:
        actor = self.current_actor()
        if actor is not None:
            return actor.style

    def copy(self):
        env = copy(self)
        env._actors = [actor.copy() for actor in self._actors]
        return env
