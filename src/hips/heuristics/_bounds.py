import numpy as np

from enum import Enum

from hips import HIPSArray
from hips.constants import LPStatus, VariableBound
from hips.heuristics._heuristic import Heuristic
from hips.loader.mps_loader import load_mps_primitive
from hips.models import MIPModel, Variable
from hips.solver import GurobiSolver


class Direction(Enum):
    DOWN = 0
    UP = 1
    CLOSEST = 2


class HeuristicBounds(Heuristic):
    """
    This heuristic is implemented after the scipopt primal heuristic 'heur_bounds.h'.
    The scipopt library describes this as a "heuristic which fixes all integer variables to a bound (lower/upper) and solves the remaining LP ".

    The heuristic can be found in the scipopt library documentation under the following link:
    hyperlink: `heur_bound.h File Reference <https://www.scipopt.org/doc/html/heur__bound_8h.php>`_.

    The 'CLOSEST' direction was added, to be able to fix the integer variable to the bound, closest to the initial relaxation LP solution.
    """

    def __init__(self, mip_model: MIPModel, direction: Direction):
        super().__init__(mip_model)
        self.direction = direction

    def compute(self, max_iter=None):
        if self.direction == Direction.DOWN or self.direction == Direction.UP:
            for bin_var in self.binary:
                fixed_value = 0 if self.direction == Direction.DOWN else 1
                self.relaxation.set_variable_bound(bin_var, VariableBound.LB, fixed_value)
                self.relaxation.set_variable_bound(bin_var, VariableBound.UB, fixed_value)
            for int_var in self.integer:
                fixed_value = int_var.lb if self.direction == Direction.DOWN else int_var.ub
                if fixed_value is None or np.isin(fixed_value.to_numpy(), [np.inf, np.NINF]).any():
                    raise Exception(
                        "Can't fix integer variable to infinity .Please specify bounds for the integer variables.")
                self.relaxation.set_variable_bound(int_var, VariableBound.LB, fixed_value)
                self.relaxation.set_variable_bound(int_var, VariableBound.UB, fixed_value)
        elif self.direction == Direction.CLOSEST:
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
