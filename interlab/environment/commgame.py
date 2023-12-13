from enum import Enum
from typing import Literal, Sequence

import matplotlib.pyplot as plt
import numpy as np
from pydantic.dataclasses import Field, dataclass

from ..actor import ActorBase
from .base import BaseEnvironment
from .monitor import Monitor


class CommunicateAndPlayGame(BaseEnvironment):
    comm_prompt = "Write a message that is sent to other players"
    play_prompt = "Secretly choose one of the following actions: {actions}"

    def __init__(
        self,
        actors: Sequence[ActorBase],
        n_rounds: int,
        action_names: Sequence[str],
        payoff_matrix: np.ndarray | None,
    ):
        super().__init__(actors)

        if payoff_matrix is not None:
            assert len(payoff_matrix.shape) == self.n_actors + 1
            for i in range(self.n_actors):
                assert payoff_matrix.shape[i] == len(action_names)
            assert payoff_matrix.shape[-1] == self.n_actors

        self.n_rounds = n_rounds
        self.action_names = action_names
        self.payoff_matrix = payoff_matrix

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
            message: str = Field(
                description="Message to other " + "players"
                if len(actors) > 2
                else "player"
            )

        self.play_action = PlayAction
        self.comm_action = CommunicationAction
        self.history = []
        self.action_monitor = Monitor(self)
        self.payoff_monitor = Monitor(self)

    def copy(self):
        env = super().copy()
        env.history = self.history[:]
        env.action_monitor = self.action_monitor.copy(new_env=env)
        env.payoff_monitor = self.payoff_monitor.copy(new_env=env)
        return env

    @property
    def game_round(self):
        return len(self.history) + 1

    def _step(self):
        observations = [
            actor.act(self.comm_prompt, expected_type=self.comm_action).data.message
            for actor in self.actors
        ]

        for actor, event in zip(self.actors, observations):
            self.everyone_observe(
                f"Message in round {self.game_round}: " + event,
                origin=actor,
            )

        play_prompt = self.play_prompt.format(actions=",".join(self.action_names))
        observations = [
            actor.act(play_prompt, expected_type=self.play_action).data.action
            for actor in self.actors
        ]

        if self.payoff_matrix is not None:
            payoffs = self.payoff_matrix[
                tuple(self.action_names.index(a) for a in observations)
            ]
        else:
            payoffs = None

        for i, (actor, event) in enumerate(zip(self.actors, observations)):
            self.action_monitor.trace(f"{actor.name}-{event}", 1)
            if payoffs is not None:
                self.payoff_monitor.trace(actor.name, payoffs[i])
            self.everyone_observe(
                f"Action in round {self.game_round}: " + event,
                origin=actor,
            )
        self.history.append(observations)

        if self.game_round > self.n_rounds:
            return self.history

    def payoff_chart(self, cumsum=False):
        colors = [actor.style["color"] for actor in self.actors]
        labels = [actor.name for actor in self.actors]
        return self.payoff_monitor.line_chart(
            colors=colors, labels=labels, cumsum=cumsum
        )
