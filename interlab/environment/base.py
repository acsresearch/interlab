from typing import Sequence, Any
import abc

from interlab.actor import ActorBase
from interlab.context import Context


class BaseEnvironment(abc.ABC):

    def __init__(self, actors: Sequence[ActorBase]):
        self.actors = actors
        self.step_counter = 0
        self.result = None

    def is_finished(self) -> bool:
        return self.result is not None

    @property
    def n_actors(self) -> int:
        return len(self.actors)

    def step(self):
        if self.is_finished():
            raise Exception("Calling 'step' on finished environment")
        self.step_counter += 1
        name = f"step {self.step_counter}"
        actor = self.current_actor()
        if actor is not None:
            name += f"; {actor.name}"
        with Context(name, meta=self.current_step_style()):
            self.result = self._step()

    def run_until_end(self, max_steps: int = None):
        if max_steps is not None:
            if self.is_finished():
                return self.result
            for _ in range(max_steps):
                self.step()
                if self.is_finished():
                    break
        else:
            while not self.is_finished():
                self.step()
        return self.result

    def everyone_observe(self, observation, origin=None):
        for actor in self.actors:
            actor.observe(observation, origin)

    @abc.abstractmethod()
    def _step(self):
        raise NotImplementedError

    def current_actor(self) -> None | ActorBase:
        return None

    def current_step_style(self) -> None | dict[str, Any]:
        actor = self.current_actor()
        if actor is not None:
            return actor.style
