from typing import Sequence, Literal
from pydantic.dataclasses import dataclass, Field

import numpy as np
from enum import Enum

from interlab.actor import ActorBase
from .environment import RoundRobinEnv


class Phase(Enum):
    COMMUNICATION = 0
    PLAY = 1


@dataclass
class CommunicationAction:
    message: str = Field(description="Message to other players")


class RepeatedMatrixGame(RoundRobinEnv):
    comm_prompt = "Write a message that is sent to other players"
    action_prompt = "Secretly choose one of the following actions: {actions}"

    def __init__(
        self,
        actors: Sequence[ActorBase],
        n_rounds: int,
        payoffs: np.ndarray,
        action_names: Sequence[str],
        prompts: Sequence[str],
    ):
        super().__init__(actors)

        assert len(payoffs.shape) == self.n_actors + 1
        for n in payoffs.shape[:-1]:
            assert n == len(action_names)
        assert payoffs[-1] == self.n_actors

        assert len(prompts) == self.n_actors

        self.n_rounds = n_rounds
        self.payoffs = payoffs
        self.action_names = action_names
        self.prompts = prompts

        self.phase = Phase.COMMUNICATION
        self.game_round = 1

        action_enum = Enum(  # type: ignore[misc]
            "ActionEnum",
            [(value, value) for value in action_names],
            type=str,
        )

        @dataclass
        class PlayAction:
            action: action_enum

        self.play_action = PlayAction

    def create_prompt(self):
        prompt = self.prompts[self.current_actor_idx]
        if self.phase == Phase.COMMUNICATION:
            return f"{prompt}\n\n{self.comm_prompt}", CommunicationAction
        else:
            action_prompt = self.action_prompt.format(
                actions=",".join(self.action_names)
            )
            return f"{prompt}\n\n{action_prompt}", self.play_action

    def process_end_of_round(self, early_end: bool) -> bool:
        if self.phase == Phase.COMMUNICATION:
            for event, actor in zip(self.round_events, self.actors):
                self.observe_all(
                    f"Message in round {self.game_round}: " + event.data.message,
                    origin=actor,
                )
            self.phase = Phase.PLAY
        else:
            for event, actor in zip(self.round_events, self.actors):
                self.observe_all(
                    f"Action in round {self.game_round}: " + event.data.action,
                    origin=actor,
                )
            self.phase = Phase.COMMUNICATION
            self.game_round += 1
            if self.game_round >= self.n_rounds:
                return True
        return False
