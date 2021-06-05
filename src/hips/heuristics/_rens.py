import warnings

from hips import HIPSArray
from hips.heuristics._heuristic import Heuristic
from hips.models import MIPModel, Variable
import numpy as np

from hips.solver.branch_and_bound import BranchAndBound


class RENS(Heuristic):

    def __init__(self, mip_model: MIPModel):
        super().__init__(mip_model)
        self.mip_solver = None

    def compute(self, max_iter):
        # Compute relaxation
        self.relaxation.optimize()
        solution = {var: self.relaxation.variable_solution(var) for var in self.integer + self.binary}
        for var, sol in solution.items():
            self.mip_model.add_constraint(var <= HIPSArray(np.ceil(sol.array)))
            self.mip_model.add_constraint(var >= HIPSArray(np.floor(sol.array)))
        self.mip_solver = BranchAndBound(self.mip_model)
        self.mip_solver.optimize()
        if self.mip_solver._incumbent is None:
            warnings.warn("RENS could not find a feasible solution")

    def variable_solution(self, var: Variable):
        return self.relaxation.variable_solution(var)

    def get_objective_value(self) -> float:
        return self.relaxation.get_objective_value()
