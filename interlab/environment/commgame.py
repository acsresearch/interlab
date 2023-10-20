from typing import Sequence, Literal
from pydantic.dataclasses import dataclass, Field

from enum import Enum

from ..actor import ActorBase
from .base import BaseEnvironment


class CommunicateAndPlayGame(BaseEnvironment):
    comm_prompt = "Write a message that is sent to other players"
    play_prompt = "Secretly choose one of the following actions: {actions}"

    def __init__(
        self,
        actors: Sequence[ActorBase],
        n_rounds: int,
        action_names: Sequence[str],
    ):
        super().__init__(actors)

        self.n_rounds = n_rounds
        self.action_names = action_names

        action_enum = Enum(  # type: ignore[misc]
            "ActionEnum",
            [(value, value) for value in action_names],
            type=str,
        )

        @dataclass
        class PlayAction:
            action: action_enum

        @dataclass
        class CommunicationAction:
            message: str = Field(description="Message to other " + "players" if len(actors) > 2 else "player")

        self.play_action = PlayAction
        self.comm_action = CommunicationAction
        self.history = []

    def current_actor(self) -> None | ActorBase:
        if self.is_finished():
            return None
        return self.actors[self.current_actor_idx]

    @property
    def game_round(self):
        return len(self.history) + 1

    def _step(self) -> bool:
        observations = [actor.act(self.comm_prompt, expected_type=self.comm_action).data.message for actor in self.actors]

        for actor, event in zip(self.actors, observations):
            self.everyone_observe(
                f"Message in round {self.game_round}: " + event,
                origin=actor,
            )

        play_prompt = self.play_prompt.format(
            actions=",".join(self.action_names)
        )
        observations = [actor.act(play_prompt, expected_type=self.play_action).data.action for actor in self.actors]

        for actor, event in zip(self.actors, observations):
            self.everyone_observe(
                f"Action in round {self.game_round}: " + event,
                origin=actor,
            )
        if self.game_round > self.n_rounds:
            return self.history