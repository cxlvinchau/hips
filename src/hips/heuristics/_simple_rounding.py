import numpy as np
from hips import LPStatus, HeuristicStatus
from hips.heuristics._heuristic import Heuristic
from hips.models import MIPModel, Variable, HIPSArray


class SimpleRounding(Heuristic):
    """
    Implements a simple rounding heuristic, that rounds each integer variable to the closest integer of the relaxation LP solution.
    """

    def __init__(self, mip_model: MIPModel):
        super().__init__(mip_model)
        self._x = {}

    def compute(self, max_iter=None):
        self.relaxation.optimize()
        if (self.relaxation.get_status() == LPStatus.INFEASIBLE):
            raise Exception("The specified MIP's relaxation has no feasible solution.")
        for var in self.binary + self.integer:
            var_value = self.relaxation.variable_solution(var).to_numpy()
            self._x[var] = HIPSArray(np.rint(var_value))
        if self.mip_model.is_feasible(self._x):
            self.logger.info("SimpleRounding found an integer feasible solution")
        else:
            self.logger.info("SimpleRounding did not find an integer feasible solution.")

    def variable_solution(self, var: Variable):
        return self._x[var]

    def get_objective_value(self) -> float:
        return self.relaxation.objective.eval(self._x).reshape(-1).to_numpy()[0]

    def get_status(self):
        lp_status = self.relaxation.get_status()
        if lp_status == LPStatus.ERROR:
            return HeuristicStatus.ERROR
        elif lp_status != LPStatus.OPTIMAL:
            return HeuristicStatus.NO_SOL_FOUND
        else:
            if self.mip_model.is_feasible(self._x):
                return HeuristicStatus.SOL_FOUND
            else:
                return HeuristicStatus.NO_SOL_FOUND




