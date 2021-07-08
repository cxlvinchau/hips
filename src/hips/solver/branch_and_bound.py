import warnings

from hips.constants import LPStatus
from hips.models import MIPModel, Constraint, HIPSArray
from hips.utils import is_integer
import numpy as np


class BranchAndBound:
    r"""Implementation of a naive branch and bound algorithm.

    This class implements a naive branch and bound algorithm for solving mixed-integer programs. As the name suggests,
    the procedure consists of two main parts, the branching and the bounding. Note that the branch and bound algorithm
    delivers the optimal solution of the problem.

    W.l.o.g., suppose we want to solve a mixed-integer program with the feasible region :math:`Ax \leq b` where we require
    :math:`x_i \in \mathbb{Z}` for :math:`i \in I`. The branch and bound algorithm repeatedly solves the relaxation of the problem,
    i.e. the problem without the integer constraints. If the found solution :math:`\bar x` is feasible for the original problem, we are done.
    Otherwise, there exists a variable :math:`x_i` with :math:`i \in I` that is not integer. In the *branching step*, the procedure creates
    two subproblems with the constraints :math:`x_i \leq \lfloor \bar x_i \rfloor` and :math:`x_i \geq \lceil \bar x_i \rceil`, respectively.
    These subproblems are then solved with the branch and bound algorithm again. However, there is not always the need
    to branch. If the relaxation of a subproblem has a worse objective than the current best solution, also known as incumbent solution,
    then there is no need to explore this branch. This is the `bound` part of the procedure.

    More details can be found in :cite:`gritzmann2013grundlagen`.
    """

    def __init__(self, model: MIPModel, incumbent=None, incumbent_val=None, max_nodes=None):
        """Constructor

        :param model: Mixed-integer program to be optimized. Instance of :class:`hips.models.MIPModel`.
        :param incumbent: The best known solution of the problem. If specified, there can be a significant speed up depending
            on the quality of the provided solution. Has to be given as a :class:`dict` that maps the variables to a :class:`hips.models.HIPSArray`.
        :param incumbent_val: The objective value of the best known solution.
        :param max_nodes: The maximum number of nodes to visit. A small number of nodes might result in not finding any solution.
            For larger problems, the procedure might take very long if the number of nodes is large.
        """
        self.model = model
        self.sense = model.lp_model.lp_sense
        self.incumbent = incumbent
        self.incumbent_val = incumbent_val
        self.visited_nodes = 0
        self.max_nodes = max_nodes

    def _optimize(self, node, level=0):
        if self.max_nodes and self.visited_nodes > self.max_nodes:
            return
        self.visited_nodes += 1
        node.init_node()
        node.optimize_relaxation()
        if node.status != LPStatus.OPTIMAL:
            if level == 0:
                warnings.warn("MIP is infeasible")
        elif node.is_integer() and (
                self.incumbent_val is None or self.sense.value * node.obj_val < self.sense.value * self.incumbent_val):
            self.incumbent = node.solution
            self.incumbent_val = node.obj_val
        elif not node.is_integer() and (
                self.incumbent_val is None or self.sense.value * node.obj_val < self.sense.value * self.incumbent_val):
            l_node, r_node = node.get_children()
            self._optimize(l_node, level=level + 1)
            self._optimize(r_node, level=level + 1)
        node.backtrack()

    def optimize(self):
        """Optimizes the mixed-integer program.
        """
        self._optimize(Node(self.model))

    def get_incumbent(self):
        """Returns the incumbent

        This method returns the incumbent solution. If no solution exists, ``None`` is returned.

        :return: :class:`dict` mapping variables to :class:`hips.models.HIPSArray` or ``None``
        """
        return self.incumbent

    def get_incumbent_val(self):
        """Returns the objective value of the incumbent

        This method returns the objective value of the incumbent. If no solution exists, ``None`` is returned.

        :return: Objective value of incumbent or ``None``
        """
        return self.incumbent_val


class Node:

    def __init__(self, model: MIPModel, parent=None, constraint: Constraint = None):
        self.parent = parent
        self.constraint = constraint
        self.model = model
        self.status = LPStatus.UNKNOWN
        self.solution = None
        self.lp_model = model.lp_model
        self.obj_val = None

    def optimize_relaxation(self):
        self.lp_model.optimize()
        if self.lp_model.get_status() == LPStatus.OPTIMAL:
            self.solution = {var: self.lp_model.variable_solution(var) for var in self.lp_model.vars}
            self.obj_val = self.lp_model.get_objective_value()
        self.status = self.lp_model.get_status()

    def init_node(self):
        if self.constraint is not None:
            self.lp_model.add_constraint(self.constraint)

    def backtrack(self):
        if self.constraint is not None:
            self.lp_model.remove_constraint(constraint=self.constraint)

    def is_integer(self):
        for var in self.model.integer_variables + self.model.binary_variables:
            if not all(is_integer(self.solution[var])):
                return False
        return True

    def get_children(self):
        min_var, min_idx = None, None
        for var in self.model.integer_variables + self.model.binary_variables:
            mask = is_integer(self.solution[var])
            if all(mask):
                continue

            idx = np.argwhere(~mask)[0]
            min_var = var
            min_idx = idx
            break

        diag = np.zeros(min_var.dim)
        diag[min_idx] = 1
        diag = np.diag(diag)
        rhs = np.zeros(min_var.dim)
        rhs[min_idx] = np.floor(self.solution[min_var].array[min_idx])
        left_node = Node(self.model, parent=self, constraint=HIPSArray(diag) * min_var <= HIPSArray(rhs))
        rhs = np.zeros(min_var.dim)
        rhs[min_idx] = np.ceil(self.solution[min_var].array[min_idx])
        right_node = Node(self.model, parent=self, constraint=HIPSArray(diag) * min_var >= HIPSArray(rhs))
        return left_node, right_node
