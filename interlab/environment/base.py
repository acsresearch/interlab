import abc
from copy import copy
from typing import Any, Sequence

from interlab.actor import BaseActor
from interlab.context import Context


class BaseEnvironment(abc.ABC):
    def __init__(self, actors: Sequence[BaseActor]):
        self._actors = list(actors)
        self._step_counter = 0
        self._result = None

    def is_finished(self) -> bool:
        return self._result is not None

    @property
    def result(self):
        if self._result is None:
            raise ValueError("Environment is not finished yet")
        return self._result

    @property
    def n_actors(self) -> int:
        return len(self._actors)

    @property
    def actors(self) -> list[BaseActor]:
        return self._actors

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
        with Context(name, meta=self.current_step_style()):
            self._result = self._step()

    def run_until_end(self, max_steps: int = None, verbose=False):
        if max_steps is not None:
            if self.is_finished():
                return self._result
            for _ in range(max_steps):
                if verbose:
                    print("Step", self._step_counter)
                self.step()
                if self.is_finished():
                    break
        else:
            while not self.is_finished():
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
