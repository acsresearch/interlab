from typing import Any

from matplotlib import pyplot as plt


class Monitor:

    def __init__(self):
        self.traces: dict[str, tuple[list[any], list[any]]] = {}

    def get(self, name):
        if name not in self.traces:
            self.traces[name] = ([], [])
        return self.traces[name]

    def trace(self, name, step, value):
        x, y = self.get(name)
        x.append(step)
        y.append(value)

    def increment(self, name, step, value=1):
        x, y = self.get(name)
        last = y[-1] if y else 0
        x.append(step)
        y.append(last + value)

    def line_chart(self, names: list[str], *, colors: list[str] | None = None, labels: list[str] | None = None, legend_loc: str = "upper left"):
        fig = plt.figure()
        plt.title("Payoffs")
        for i, name in enumerate(names):
            color = colors[i] if colors else None
            label = labels[i] if labels else None
            x, y = self.get(name)
            plt.plot(x, y, color=color, label=label)
        plt.legend(loc=legend_loc)
        return fig
