from typing import Optional, Sequence, Tuple

import numpy as np

from interlab_zoo.algorithms.mcts import Mcts, Situation


class SimpleGameSituation(Situation):
    def __init__(self, n_players: int, n_actions: int, values: list[int]):
        assert len(values) <= n_players
        assert n_players < n_actions
        if n_players == len(values):
            player = None
        else:
            player = len(values)
        actions = [a for a in range(n_actions) if a not in values]
        super().__init__(player, actions)
        self.values = values
        self.n_players = n_players
        self.n_actions = n_actions

    def perform_action(self, action_idx: int) -> "Situation":
        assert self.current_player is not None
        values = self.values[:]
        values.append(self.actions[action_idx])
        return SimpleGameSituation(self.n_players, self.n_actions, values)


def simple_game_estimator(
    situation: SimpleGameSituation,
) -> tuple[Optional[Sequence[float]], Sequence[float]]:
    if situation.current_player is None:
        values = np.zeros(situation.n_players)
        values[np.argmax(situation.values)] = 1.0
        return None, values
    n_actions = len(situation.actions)
    return np.full(n_actions, 1.0 / n_actions), np.zeros(situation.n_players)


def test_simple_game_mcts():
    s = SimpleGameSituation(2, 4, [])
    mcts = Mcts(s, simple_game_estimator)
    mcts.search(2000)
    assert mcts.get_best_action() == 3