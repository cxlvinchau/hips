from typing import Union

import matplotlib.pyplot as plt
import numpy as np


class Tracker:

    def __init__(self, heuristic):
        self._heuristic = heuristic
        self._metrics = dict()
        self._heuristic_name = heuristic.__class__.__name__

    def log(self, metric: str, value: Union[int, float, np.float, np.float64], **kwargs):
        self._metrics.setdefault(metric, []).append({"iteration": self._heuristic.iteration, metric: value, **kwargs})

    def plot(self, metric: str, x: str = "iteration"):
        values = [value_dict[metric] for value_dict in self._metrics[metric]]
        x_values = [value_dict[x] for value_dict in self._metrics[metric]]
        plt.plot(x_values, values)
        plt.xlabel(x)
        plt.ylabel(metric)
        plt.show()