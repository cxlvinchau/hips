import abc
import logging
logging.basicConfig(level=logging.INFO)
from hips.models import Variable, MIPModel
from hips.utils.tracking import Tracker


class Heuristic(metaclass=abc.ABCMeta):
    """Abstract heuristic class

    Abstract heuristic class that implements basis structures for heuristics. Particularly, the different
    attributes should be used, so that the heuristic is fully integrated into HIPS.

    :ivar mip_model: The mixed-integer program model. Instance of :class:`hips.models.MIPModel`
    :ivar relaxation: The relaxation of the mixed integer program. Instance of :class:`hips.models.LPModel`
    :ivar binary: Binary variables
    :ivar integer: Integer variables
    :ivar iteration: Iteration of the heuristic. Initialized with 0 and should be updated once a single iteration of the
        heuristic is completed
    """

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
        """
        Compute the optimal solution with the heuristic algorithm

        :param max_iter: Maximum iteration. Once the maximum iteration is reached, the computation is stopped.
        """
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

        :return: Value of the objective function
        """

    @abc.abstractmethod
    def get_status(self):
        """
        Returns the status of the heuristic, either that a solution was found, no solution was found or that the heuristic
        encountered an error

        :return: Status of the heuristic. Enum of :class:`HeuristicStatus <hips.constants.HeuristicStatus>`
        """