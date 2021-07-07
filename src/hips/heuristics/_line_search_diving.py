from ._abstract_diving import AbstractDiving
from ..models import MIPModel, HIPSArray
import numpy as np


class LineSearchDiving(AbstractDiving):
    """Implementation of line search diving heuristic

    This class implements the line search diving heuristic as presented by :cite:`Hendel2011`. As the name suggests, this
    heuristic follows the general structure of a diving heuristic, i.e. bounds are introduced or variables are fixed to
    explore a branch of a branch and bound tree. In this implementation, the selected variable in each step is fixed to a value.

    The choice of the variable that is fixed is made as follows. Suppose :math:`x^R` is the solution found at the root
    node :math:`R` in the branch and bound algorithm. Let :math:`N` be an arbitrary node within the branch and bound tree
    (i.e. not the root node) and :math:`x^N` the corresponding solution. At :math:`N` line search diving considers the line
    between :math:`x^N` and :math:`x^R` and conceptually moves towards :math:`x^R` and checks which variable becomes integer first.
    This variable is then selected and fixed.
    """

    def __init__(self, mip_model: MIPModel, current_best_objective: float = None, seed=0):
        super().__init__(mip_model, current_best_objective)
        self.root_node_solution = None
        self.q = None
        self.rng = np.random.default_rng(seed=seed)
        self.added_constraints = []

    def dive(self):
        if self.root_node_solution is None:
            self.root_node_solution = self._x
        # Compute distance ratio between current node and root node
        q = dict()
        for var, idx in self.fractional_index_set:
            current_val, root_val = self._x[var].array[idx], self.root_node_solution[var].array[idx]
            if current_val < root_val:
                q[(var, idx)] = (current_val - np.floor(current_val)) / (root_val - current_val)
            elif current_val > root_val:
                q[(var, idx)] = (np.ceil(current_val) - current_val) / (current_val - root_val)
        if len(q) == 0:
            # Randomly fix variable if there are no difference between root and current solution
            var, idx = self.rng.choice(list(self.fractional_index_set), replace=False, size=1)[0]
            diagonal = np.zeros(var.dim)
            diagonal[idx] = 1
            rhs = np.zeros(var.dim)
            rhs[idx] = np.rint(self._x[var].array[idx])
            constr = HIPSArray(np.diag(diagonal)) * var == HIPSArray(rhs)
            self.relaxation.add_constraint(constr)
            self.added_constraints.append(constr)
        else:
            var, idx = min(q, key=q.get)
            current_val, root_val = self._x[var].array[idx], self.root_node_solution[var].array[idx]
            if current_val < root_val:
                diagonal = np.zeros(var.dim)
                diagonal[idx] = 1
                rhs = np.zeros(var.dim)
                rhs[idx] = np.floor(self._x[var].array[idx])
                constr = HIPSArray(np.diag(diagonal)) * var == HIPSArray(rhs)
                self.relaxation.add_constraint(constr)
                self.added_constraints.append(constr)
            else:
                diagonal = np.zeros(var.dim)
                diagonal[idx] = 1
                rhs = np.zeros(var.dim)
                rhs[idx] = np.ceil(self._x[var].array[idx])
                constr = HIPSArray(np.diag(diagonal)) * var == HIPSArray(rhs)
                self.relaxation.add_constraint(constr)
                self.added_constraints.append(constr)

    def revert(self):
        for constr in self.added_constraints:
            self.relaxation.remove_constraint(constraint=constr)
