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
        self.current_best_objective = current_best_objective
        self.discovered_solution = None
        self.fractional_index_set = set()

    def compute(self, max_iter=100):
        current_lp_solution = None
        self.relaxation.optimize()
        # --- LOGGING ---
        self.tracker.log("objective value", self.get_objective_value())
        # --- ------- ---
        if self.relaxation.get_status() == LPStatus.INFEASIBLE:
            return
        if self.mip_model.is_feasible({x: self.variable_solution(x) for x in self.relaxation.vars}) or self._round_trivially():
            self.discovered_solution = self.get_objective_value()
            return
        current_lp_solution = self.get_objective_value()
        while self.iteration <= max_iter:
            if self.current_best_objective is not None:
                if current_lp_solution < self.current_best_objectve:
                    break
            self.iteration += 1
            self._compute_fractional_index_set()
            self._dive()
            self.relaxation.optimize()
            # --- LOGGING ---
            self.tracker.log("objective value", self.get_objective_value())
            # --- ------- ---
            if self.relaxation.get_status() == LPStatus.INFEASIBLE:
                break
            else:
                current_lp_solution = self.get_objective_value()
            if self.mip_model.is_feasible({x: self.variable_solution(x) for x in self.relaxation.vars}) or self._round_trivially():
                self.discovered_solution = self.get_objective_value()
                break
        self._revert()

    def _compute_fractional_index_set(self):
        """
        Computes the set of variables, which have a fractional value in the current relaxed (LP) solution.
        The set is stored in self.fractional_index_set and follows the scheme:
        {(variable1, dim_index1), (variable1, dim_index2), ..., (variableN, dim_indexN)},
        where variableI indexes the variable and dim_indexI refers to the position in the multidimensional variable variableI.

        :return:
        """
        fractional_index_set = set()
        for int_var in self.integer + self.binary:
            variable_value = self.variable_solution(int_var)
            for i in range(int_var.dim):
                variable_index_value = variable_value.to_numpy()[i]
                if not is_close(variable_index_value, math.floor(variable_index_value)) and not is_close(variable_index_value, math.ceil(variable_index_value)):
                    fractional_index_set.add((int_var, i))
        self.fractional_index_set = fractional_index_set

    def _round_trivially(self):
        """
        Checks if the current solution of the relaxation is trivially roundable according to
        :func:`mip_model._trivially_roundable <hips.models._mip_model.MIPModel._trivially_roundable>`.
        If so, it sets the discovered solution to the corresponding objective value of the rounded solution.

        :return: True, if current relaxation solution is trivially roundable, else False
        """
        trivially_down_roundable, trivially_up_roundable = self.mip_model._trivially_roundable()
        objective_function = self.relaxation.objective
        trivially_rounded_solution = 0
        for frac_var in self.fractional_index_set:
            pass

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
        return self.discovered_solution
