import abc
import logging
logging.basicConfig(level=logging.INFO)
from hips.models import Variable, MIPModel
from hips.utils.tracking import Tracker


class Heuristic(metaclass=abc.ABCMeta):

    def __init__(self, mip_model: MIPModel):
        self.logger = logging.getLogger("heuristics")
        self.mip_model = mip_model
        self.relaxation = mip_model.lp_model
        self.binary = mip_model.binary_variables
        self.integer = mip_model.integer_variables
        self.iteration = 0
        self.tracker = Tracker(self)

    @abc.abstractmethod
    def compute(self, max_iter=None):
        """Compute the optimal solution with the heuristic algorithm."""
        pass

    @abc.abstractmethod
    def variable_solution(self, var: Variable):
        """
        Return the solution found by the heuristic

        :param var: Variable
        :return: Optimal solution
        """

    @abc.abstractmethod
    def get_objective_value(self) -> float:
        """
        Return objective value determined by the heuristic

        :return: optimal value
        """