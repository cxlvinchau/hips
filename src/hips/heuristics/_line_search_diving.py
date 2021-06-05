from ._heur_abstract_diving import AbstractDiving
from .. import HIPSArray
from ..models import MIPModel
import numpy as np


class LineSearchDiving(AbstractDiving):
    """
    This class implements the diving heuristic called line search diving.
    """

    def __init__(self, mip_model: MIPModel, current_best_objective: float = None, seed=0):
        super().__init__(mip_model, current_best_objective)
        self.root_node_solution = None
        self.q = None
        self.rng = np.random.default_rng(seed=seed)

    def _dive(self):
        if self.root_node_solution is None:
            self.root_node_solution = self._x
        # Compute distance ratio between current node and root node
        q = dict()
        for var, idx in self.fractional_index_set:
            current_val, root_val = self._x[var].array[idx], self.root_node_solution[var].array[idx]
            if current_val < root_val:
                q[(var, idx)] = (current_val - np.floor(current_val))/(root_val - current_val)
            elif current_val > root_val:
                q[(var, idx)] = (np.ceil(current_val) - current_val)/(current_val - root_val)
        if len(q) == 0:
            # Randomly fix variable if there are no difference between root and current solution
            var, idx = self.rng.choice(list(self.fractional_index_set), replace=False, size=1)[0]
            diagonal = np.zeros(var.dim)
            diagonal[idx] = 1
            rhs = np.zeros(var.dim)
            rhs[idx] = np.rint(self._x[var].array[idx])
            self.relaxation.add_constraint(HIPSArray(np.diag(diagonal)) * var == HIPSArray(rhs))
        else:
            var, idx = min(q, key=q.get)
            current_val, root_val = self._x[var].array[idx], self.root_node_solution[var].array[idx]
            if current_val < root_val:
                diagonal = np.zeros(var.dim)
                diagonal[idx] = 1
                rhs = np.zeros(var.dim)
                rhs[idx] = np.floor(self._x[var].array[idx])
                self.relaxation.add_constraint(HIPSArray(np.diag(diagonal)) * var >= HIPSArray(rhs))
            else:
                diagonal = np.zeros(var.dim)
                diagonal[idx] = 1
                rhs = np.zeros(var.dim)
                rhs[idx] = np.ceil(self._x[var].array[idx])
                self.relaxation.add_constraint(HIPSArray(np.diag(diagonal)) * var <= HIPSArray(rhs))


    def _revert(self):
        pass
