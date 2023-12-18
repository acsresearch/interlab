from typing import Any

import numpy as np
from matplotlib import pyplot as plt

from .base import BaseEnvironment


class Monitor:
    def __init__(self, env: BaseEnvironment):
        self.env = env
        self.traces: dict[str, tuple[list[any], list[any]]] = {}

    def copy(self, new_env=None):
        monitor = Monitor(new_env or self.env)
        for key, value in self.traces.items():
            monitor.traces[key] = (value[0][:], value[1][:])
        return monitor

    def get(self, name):
        if name not in self.traces:
            self.traces[name] = ([], [])
        return self.traces[name]

    def trace(self, name, value):
        x, y = self.get(name)
        x.append(self.env.current_step)
        y.append(value)

    def line_chart(
        self,
        *,
        names: list[str] | None = None,
        colors: list[str] | None = None,
        labels: list[str] | None = None,
        legend_loc: str = "upper left",
        cumsum: bool = False,
    ):
        fig = plt.figure()
        plt.title("Payoffs")

        if names is None:
            names = list(self.traces)

        for i, name in enumerate(names):
            color = colors[i] if colors else None
            label = labels[i] if labels else None
            x, y = self.get(name)
            if cumsum:
                y = np.array(y).cumsum()
            plt.plot(x, y, color=color, label=label)
        plt.legend(loc=legend_loc)
        return fig
