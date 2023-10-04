from typing import Sequence

import numpy as np
from git import Actor

import matplotlib.pyplot as plt


def plot_matrix_game_payoffs(history: Sequence[Sequence[str]], actors: Sequence[Actor], action_names: str, payoffs_matrix: np.ndarray):
    if not history:
        return None
    n_players = len(history[0])
    payoffs = [np.zeros(n_players)]
    for actions in history:
        indices = tuple(action_names.index(action) for action in actions)
        payoffs.append(payoffs_matrix[indices])
    payoffs = np.array(payoffs)
    cum_payoffs = payoffs.cumsum(axis=0)

    fig = plt.figure()
    for i, actor in enumerate(actors):
        plt.plot(cum_payoffs[:, i], color=actor.style["color"], label=actor.name)

    plt.legend(loc="upper left")
    return fig