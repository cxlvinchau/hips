import warnings

from hips import HIPSArray
from hips.constants import LPStatus, VarTypes, ProblemSense
from hips.models import MIPModel, Constraint, LPModel
from hips.utils import is_integer
import numpy as np


class BranchAndBound:

    def __init__(self, model: MIPModel, incumbent=None, incumbent_val=None, max_nodes=None):
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
        self._optimize(Node(self.model))


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
