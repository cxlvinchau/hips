from typing import Union

import matplotlib.pyplot as plt
import numpy as np


class Tracker:
    """
    Utility class to track heuristics
    """

    def __init__(self, heuristic):
        """Constructor

        :param heuristic: The heuristic to be tracked
        """
        self._heuristic = heuristic
        self._metrics = dict()
        self._heuristic_name = heuristic.__class__.__name__

    def log(self, metric: str, value: Union[int, float, np.float, np.float64], **kwargs):
        """Logs a given metric and additional arguments

        :param metric: The metric whose value should be tracked
        :param value: Value of the metric
        :param kwargs: Additional metrics that should be tracked
        """
        self._metrics.setdefault(metric, []).append({"iteration": self._heuristic.iteration, metric: value, **kwargs})

    def plot(self, metric: str, x: str = "iteration"):
        """Plots a given metric

        :param metric: Metric that should be plotted
        :param x: x value, by default the iteration is used, any specified metric in the :func:`log` method also works.
        """
        values = [value_dict[metric] for value_dict in self._metrics[metric]]
        x_values = [value_dict[x] for value_dict in self._metrics[metric]]
        plt.plot(x_values, values, marker='o', markersize=5)
        plt.xlabel(x)
        plt.ylabel(metric)
        plt.show()