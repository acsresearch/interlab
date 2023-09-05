import abc
from typing import Optional


class Situation(abc.ABC):
    def __init__(self, current_player: Optional[int], actions: Optional[list]):
        self.current_player = current_player
        self.actions = actions

    def action_to_description(self, action):
        return str(action)

    def description(self):
        return "situation", None

    @abc.abstractmethod
    def perform_action(self, action_idx: int) -> "Situation":
        raise NotImplementedError
