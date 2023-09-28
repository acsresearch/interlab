from dataclasses import dataclass
from typing import Any

State = Any


@dataclass
class Situation:

    env: "Environment"
    player: int | None
    state: State

    def is_terminal(self):
        return self.player is None





from .environment import Environment  # noqa