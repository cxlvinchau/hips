from abc import ABC, abstractmethod

from hips.constants import ProblemSense, LPStatus, VariableBound
from hips.models._lp_model import Constraint, Variable, LinExpr
from hips.models import HIPSArray


class AbstractSolver(ABC):
    """Abstract class/interface for concrete solver, such as Gurobi or CLP. By default, it solves a maximization problem"""

    def __init__(self):
        self.lp_sense = ProblemSense.MAX
        self.objective = None

    @abstractmethod
    def add_constraint(self, constraint: Constraint, name=None):
        """
        Adds a constraint of type :class:`hips.models.Constraint`

        :param constraint: A constraint of type :class:`Constraint <hips.models.Constraint>`
        :param name: Name of the constraint. This argument is optional.
        """

    @abstractmethod
    def remove_constraint(self, name: str = None, constraint: Constraint = None):
        """
        Remove constraint based on its name or the constraint directly.

        :param name: Name of the constraint
        :param constraint: Constraint to be deleted
        """

    @abstractmethod
    def add_variable(self, var: Variable):
        """
        Adds a variable to the model. Use the var.id as a name in the concrete solver implementation to prevent duplicate names.

        :param var: Variable to be added. Instance of :class:`Variable <hips.models.Variable>`.
        """

    @abstractmethod
    def remove_variable(self, var: Variable):
        """
        Removes variable from model

        :param var: Variable to be removed from the LP. Instance of :class:`Variable <hips.models.Variable>`
        """

    @abstractmethod
    def set_variable_bound(self, var: Variable, bound: VariableBound, value: HIPSArray):
        """
        Sets the specified bound of variable var to the specified value.

        :param var: The variable to set the bound on. Instance of :class:`Variable <hips.models.Variable>`
        :param bound: Specifies if the lower (VariableBound.LB) or upper (VariableBound.UB) bound is set. Either
            :attr:`hips.VariableBound.LB` or :attr:`hips.VariableBound.UB`.
        :param value: The value to set as the new bound on the variable. Needs to be an instance of
            :class:`HIPSArray <hips.models.HIPSArrays>`.
        """

    def set_objective(self, objective: LinExpr):
        """
        Sets the linear objective function

        :param objective: Objective function. Needs to be an instance of :class:`hips.models.LinExpr`.
        """
        self.objective = objective

    def set_lp_sense(self, lp_sense: ProblemSense):
        """
        Sets the type of the LP, either LPSense.MAX or LPSense.MIN

        :param lp_sense: Either :class:`LPSense.MAX <hips.constants.LPSense>` or :class:`LPSense.MIN <hips.constants.LPSense>`
        """
        self.lp_sense = lp_sense

    @abstractmethod
    def variable_solution(self, var: Variable) -> HIPSArray:
        """
        Returns the optimal value for the given variable. Note that this method does not check whether the LP has
        an optimal solution, it is recommended to use :meth:`get_status` before calling this method.

        :param var: Variable for which the solution should be returned. Needs to be an instance of
            :class:`hips.models.Variable`
        :return: Value in the optimal solution
        """

    @abstractmethod
    def get_objective_value(self) -> float:
        """
        Returns the optimal objective value. Note that this method does not check whether the LP has
        an optimal solution, it is recommended to use :meth:`get_status` before calling this method.

        :return: Optimal objective value.
        """

    @abstractmethod
    def optimize(self):
        """
        Optimizes the linear program
        """

    @abstractmethod
    def get_status(self) -> LPStatus:
        """
        Returns the status of an LP, e.g. infeasible or optimal

        :return: Status of the linear program. :class:`hips.LPStatus` enum.
        """
