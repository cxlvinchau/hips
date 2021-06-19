import warnings

from hips import HIPSArray
from hips.heuristics._heuristic import Heuristic
from hips.models import MIPModel, Variable
import numpy as np

from hips.solver.branch_and_bound import BranchAndBound


class RENS(Heuristic):

    def __init__(self, mip_model: MIPModel):
        super().__init__(mip_model)
        self.mip_solver = BranchAndBound(self.mip_model)
        self.added_constraints = []

    def compute(self, max_iter=None):
        """
        Execute the computation of RENS

        :param max_iter: The maximum number of nodes that are visited in the Branch and Bound search.
        :return:
        """
        # Compute relaxation
        self.relaxation.optimize()
        solution = {var: self.relaxation.variable_solution(var) for var in self.integer + self.binary}
        for var, sol in solution.items():
            constr = var <= HIPSArray(np.ceil(sol.array))
            self.added_constraints.append(constr)
            self.mip_model.add_constraint(constr)
            constr = var >= HIPSArray(np.floor(sol.array))
            self.added_constraints.append(constr)
            self.mip_model.add_constraint(constr)
        self.mip_solver.max_nodes=max_iter
        self.mip_solver.optimize()
        if self.mip_solver.incumbent is None:
            warnings.warn("RENS could not find a feasible solution")

    def variable_solution(self, var: Variable):
        return self.relaxation.variable_solution(var)

    def get_objective_value(self) -> float:
        return self.relaxation.get_objective_value()
