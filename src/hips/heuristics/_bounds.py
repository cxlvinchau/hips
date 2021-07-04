import numpy as np

from enum import Enum

from hips.constants import LPStatus, VariableBound, HeuristicStatus
from hips.heuristics._heuristic import Heuristic
from hips.loader.mps_loader import load_mps_primitive
from hips.models import MIPModel, Variable, HIPSArray
from hips.solver import GurobiSolver


class BoundDirection(Enum):
    LOWER = 0
    UPPER = 1
    CLOSEST = 2


class HeuristicBounds(Heuristic):
    """
    This heuristic is implemented after the scipopt primal heuristic 'heur_bounds.h'.
    The scipopt library describes this as a "heuristic which fixes all integer variables to a bound (lower/upper) and solves the remaining LP ".

    The heuristic can be found in the scipopt library documentation under the following link:
    hyperlink: `heur_bound.h <https://www.scipopt.org/doc/html/heur__bound_8h.php>`_.

    The 'CLOSEST' direction was added, to be able to fix the integer variable to the bound, closest to the initial relaxation LP solution.
    """

    def __init__(self, mip_model: MIPModel, direction: BoundDirection):
        super().__init__(mip_model)
        self.direction = direction

    def compute(self, max_iter=None):
        if self.direction == BoundDirection.LOWER or self.direction == BoundDirection.UPPER:
            for bin_var in self.binary:
                fixed_value = 0 if self.direction == BoundDirection.LOWER else 1
                self.relaxation.set_variable_bound(bin_var, VariableBound.LB, fixed_value)
                self.relaxation.set_variable_bound(bin_var, VariableBound.UB, fixed_value)
            for int_var in self.integer:
                fixed_value = int_var.lb if self.direction == BoundDirection.LOWER else int_var.ub
                if fixed_value is None or np.isin(fixed_value.to_numpy(), [np.inf, np.NINF]).any():
                    raise Exception(
                        "Can't fix integer variable to infinity .Please specify bounds for the integer variables.")
                self.relaxation.set_variable_bound(int_var, VariableBound.LB, fixed_value)
                self.relaxation.set_variable_bound(int_var, VariableBound.UB, fixed_value)
        elif self.direction == BoundDirection.CLOSEST:
            self.relaxation.optimize()
            for var in self.binary + self.integer:
                var_value = self.relaxation.variable_solution(var).to_numpy()
                fixed_value = HIPSArray(np.rint(var_value))
                self.relaxation.set_variable_bound(var, VariableBound.LB, fixed_value)
                self.relaxation.set_variable_bound(var, VariableBound.UB, fixed_value)
        else:
            raise Exception("No direction specified.")
        self.relaxation.optimize()

    def variable_solution(self, var: Variable):
        return self.relaxation.variable_solution(var)

    def get_objective_value(self) -> float:
        if self.relaxation.get_status() == LPStatus.INFEASIBLE:
            print("WARNING: The fixed variables led to an empty feasible region.")
            return float("NaN")
        return self.relaxation.get_objective_value()

    def get_status(self):
        lp_status = self.relaxation.get_status()
        if lp_status == LPStatus.ERROR:
            return HeuristicStatus.ERROR
        elif lp_status == LPStatus.OPTIMAL:
            return HeuristicStatus.SOL_FOUND
        else:
            return HeuristicStatus.NO_SOL_FOUND

