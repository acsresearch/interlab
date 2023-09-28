import abc
from typing import Any, Sequence, Type

from interlab.actor import ActorBase
from interlab.context import Context

Action = Any


class EnvironmentBase(abc.ABC):

    def __init__(self, actors: Sequence[ActorBase], initial_actor_idx=None):
        assert len(self.actors) > 0
        self.actors = actors
        self.current_actor_idx = initial_actor_idx or 0
        self.step = 0

    @property
    def n_actors(self):
        return len(self.actors)

    @property
    def current_actor(self):
        if self.current_actor_idx is None:
            return None
        return self.current_actor[self.current_actor_idx]

    def is_terminated(self):
        return self.current_actor_idx is None

    def create_prompt(self) -> (any, Type[Any] | None):
        return None, None

    @abc.abstractmethod
    def post_process_step(self, event) -> int | None:
        raise NotImplementedError

    def run_step(self):
            current_actor = self.current_actor
            if current_actor is None:
                raise Exception("Running step in terminated environment")
            with Context(f"{self.__class__.__name__}  step: {self.step}, actor: {current_actor.name}", meta=self.current_actor.style):
                prompt, expected_type = self.create_prompt()
                event = current_actor.act(prompt=prompt, expected_type=expected_type)
                self.current_actor_idx = self.post_process_step(event)
                self.step += 1

    def observe_all(self, observation: Any, origin):
        for actor in self.actors:
            actor.observe(observation, origin)

    def run_steps(self, max_steps: int):
        for _ in range(max_steps):
            if self.is_terminated():
                break
            self.run_step()


class RoundRobinEnv(EnvironmentBase):

    def __init__(self, actors: Sequence[ActorBase]):
        super().__init__(actors)
        self.round_events = [None] * self.n_actors
        self.round = 0

    def check_early_end(self, event) -> bool:
        return False

    def process_end_of_round(self, early_end: bool) -> bool:
        raise NotImplementedError

    def post_process_step(self, event) -> int | None:
        self.round_events[self.current_actor_idx] = event
        if self.check_early_end(event):
            return None
        next_player_idx = self.current_actor_idx + 1
        if next_player_idx == self.n_actors:
            if self.process_end_of_round(False):
                return None
            else:
                self.round += 1
                return 0
        else:
            return next_player_idx

