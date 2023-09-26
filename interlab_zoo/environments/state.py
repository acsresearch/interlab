from dataclasses import dataclass


@dataclass
class State:

    env: "Environment"
    player: int | None
    payload: any

    def is_terminal(self):
        return self.player is None




from .environment import Environment  # noqa