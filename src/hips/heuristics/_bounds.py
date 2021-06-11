import numpy as np

from hips.constants import LPStatus
from hips.heuristics._heuristic import Heuristic
from hips.loader.mps_loader import load_mps_primitive
from hips.models import MIPModel, Variable
from hips.solver import GurobiSolver


class HeuristicBounds(Heuristic):
    """
    This heuristic is implemented after the scipopt primal heuristic 'heur_bounds.h'.
    The scipopt library describes this as a "heuristic which fixes all integer variables to a bound (lower/upper) and solves the remaining LP ".

    The heuristic can be found in the scipopt library documentation under the following link:
    hyperlink: `heur_bound.h File Reference <https://www.scipopt.org/doc/html/heur__bound_8h.php>`_.
    """

    def __init__(self, mip_model: MIPModel, lower: bool):
        super().__init__(mip_model)
        self.lower = lower

    def compute(self, max_iter=None):
        for bin_var in self.binary:
            fix_constraint = bin_var == (0 if self.lower else 1)
            self.mip_model.add_constraint(fix_constraint)
        for int_var in self.integer:
            bound_to_fix = int_var.lb if self.lower else int_var.ub
            if bound_to_fix is None or np.isin(bound_to_fix.to_numpy(), [np.inf, np.NINF]):
                raise Exception("Can't fix integer variable to infinity .Please specify bounds for the integer variables.")
            fix_constraint = int_var == bound_to_fix
            self.mip_model.add_constraint(fix_constraint)
        self.relaxation.optimize()

    def variable_solution(self, var: Variable):
        return self.relaxation.variable_solution(var)

    def get_objective_value(self) -> float:
        if self.relaxation.get_status() == LPStatus.INFEASIBLE:
            print("WARNING: The fixed variables led to an empty feasible region.")
            return float("NaN")
        return self.relaxation.get_objective_value()