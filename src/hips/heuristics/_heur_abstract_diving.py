import abc
import math

from hips.utils import is_close
from hips.constants import LPStatus
from hips.heuristics._heuristic import Heuristic
from hips.models import Variable, MIPModel


class AbstractDiving(Heuristic, metaclass=abc.ABCMeta):
    """
    Implements an abstract version of diving heuristics. It consists of a general framework for
    branch-and-bound-tree traversal and stopping criteria. The branching criteria should be implemented in a
    corresponding subclass. This implementation roughly follows the algorithm seen in
    Berthold_Primal_Heuristics_For_Mixed_Integer_Programs.pdf; Page 17, "Algorithm 1: A General Diving heuristic";
    """

    def __init__(self, mip_model: MIPModel, current_best_objective: float = None):
        super().__init__(mip_model)
        self.current_best_objectve = current_best_objective
        self.discovered_solution = None
        self.fractional_index_set = {}

    def compute(self, max_iter=None):
        iter = 0
        current_lp_solution = None
        self.relaxation.optimize()
        if self.relaxation.get_status() == LPStatus.INFEASIBLE:
            return
        if self.mip_model.is_feasible({x: self.variable_solution(x) for x in self.relaxation.vars}) or self.round_trivially():
            self.discovered_solution = self.get_objective_value()
            return
        current_lp_solution = self.get_objective_value()
        while iter <= max_iter:
            if self.current_best_objective is not None:
                if current_lp_solution < self.current_best_objectve:
                    break
            iter += 1
            self.compute_fractional_index_set()
            self.dive()
            self.relaxation.optimize()
            if self.relaxation.get_status() == LPStatus.INFEASIBLE:
                break
            else:
                current_lp_solution = self.get_objective_value()
            if self.mip_model.is_feasible({x: self.variable_solution(x) for x in self.relaxation.vars}) or self.round_trivially():
                self.discovered_solution = self.get_objective_value()
                break
        self.revert()

    def _round_trivially(self):
        """
        Checks if the all variables of the model are trivially roundable. If so, fix the variables to the rounded values
        and optimize, such that the corresponding objective value can be fetched.

        1. A variable x_j is called trivially down-roundable, if all coefficients a_ij of the corresponding column of the
        matrix A are non negative, hence A_j >= 0.
        2. A variable x_j is called trivially up-roundable, if all coefficients a_ij of the corresponding column of the
        matrix A are non positive, hence A_j <= 0.
        3. A variable is called trivially roundable, if it is trivially down-roundable or trivially up-roundable.
        - Source: Berthold_Primal_Heuristics_For_Mixed_Integer_Programs.pdf; Page 3, Definition 1.5;

        :return: True, if every variable of the model can be rounded trivially; False, else
        """
        #TODO implement me
        return False

    def _compute_fractional_index_set(self):
        """
        Computes the set of variables, which have a fractional value in the current relaxed (LP) solution.
        The set is stored in self.fractional_index_set and follows the scheme:
        {(variable1, dim_index1), (variable1, dim_index2), ..., (variableN, dim_indexN)},
        where variableI indexes the variable and dim_indexI refers to the position in the multidimensional variable variableI.

        :return:
        """
        fractional_index_set = {}
        for int_var in self.mip_model.integer_variables + self.mip_model.binary_variables:
            variable_value = self.variable_solution(int_var)
            for i in range(int_var.dim):
                variable_index_value = variable_value.to_numpy()[i]
                if not is_close(variable_index_value, math.floor(variable_index_value)) and not is_close(variable_index_value, math.ceil(variable_index_value)):
                    fractional_index_set += {(int_var, i)}
        self.fractional_index_set = fractional_index_set


    @abc.abstractmethod
    def _dive(self):
        """
        Dive down the B&B tree. Specific diving heuristics have to override this method according to the
        heuristics branching approach.

        :return:
        """
        pass

    @abc.abstractmethod
    def _revert(self):
        """
        This method is used to revert any changes (fixing or bounding variables), that the heurisitc may have applied
        to the model while diving down one B&B tree branch.

        :return:
        """
        pass

    def variable_solution(self, var: Variable):
        return self.relaxation.variable_solution(var)

    def get_objective_value(self) -> float:
        return self.relaxation.get_objective_value()

