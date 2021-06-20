import warnings

from hips import HIPSArray
from hips.heuristics._heuristic import Heuristic
from hips.models import MIPModel, Variable
import numpy as np

from hips.solver.branch_and_bound import BranchAndBound


class RENS(Heuristic):
    r"""Implementation of the relaxation enforced neighbourhood search (RENS)

    This class implements the relaxation enforced neighborhood search, or short RENS, introduced by :cite:p:`Berthold2013`.
    This heuristic can be used to heuristically solve mixed-integer programs with binary and integer variables. The idea is
    to solve the relaxation of the problem and use the solution of the relaxed solution to introduce new bounds.

    W.l.o.g. suppose the feasible region of a relaxation of a problem is given by :math:`Ax \leq b` and let :math:`x^*` be
    the optimal solution of the problem. RENS adds the constraints :math:`{x \leq \lceil x^* \rceil}` and :math:`{x \geq \lfloor x^* \rfloor}`
    to the original problem and solves it using a mixed-integer program solver. Note that the computed solution, if it exists,
    gives us the best solution that can be obtained from rounding the solution of the relaxation.

    In this implementation a naive branch and bound algorithm is used as exact mixed-integer program solver.
    """

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
