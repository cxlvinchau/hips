import os

from hips import HIPSArray
from hips.constants import LPStatus, VarTypes, LPSense
from hips.loader import load_mps_advanced
from hips.models import MIPModel, Constraint, LPModel
from hips.solver import ClpSolver, GurobiSolver
from hips.utils import is_integer
from collections import deque
import numpy as np


class BranchAndBound:

    def __init__(self, model: MIPModel):
        self.model = model
        self.sense = model.lp_model.lp_sense
        self._incumbent = None
        self._incumbent_val = None

    def _optimize(self, node):
        node.init_node()
        node.optimize_relaxation()
        if node.status != LPStatus.OPTIMAL:
            pass
        elif node.is_integer() and (
                self._incumbent_val is None or self.sense.value * node.obj_val < self._incumbent_val):
            self._incumbent = node.solution
            self._incumbent_val = node.obj_val
        elif self._incumbent_val is None or self.sense.value * node.obj_val < self._incumbent_val:
            l_node, r_node = node.get_children()
            self._optimize(l_node)
            self._optimize(r_node)
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
            print(self.constraint)
            self.lp_model.remove_constraint(constraint=self.constraint)

    def is_integer(self):
        for var in self.model.integer_variables + self.model.binary_variables:
            if not all(is_integer(self.lp_model.variable_solution(var))):
                return False
        return True

    def get_children(self):
        for var in self.model.integer_variables + self.model.binary_variables:
            mask = is_integer(self.lp_model.variable_solution(var))
            if all(mask):
                continue
            idx = np.argwhere(~mask)[0]
            diag = np.zeros(var.dim)
            diag[idx] = 1
            diag = np.diag(diag)
            rhs = np.zeros(var.dim)
            rhs[idx] = np.floor(self.lp_model.variable_solution(var).array[idx])
            left_node = Node(self.model, parent=self, constraint=HIPSArray(diag) * var <= HIPSArray(rhs))
            rhs = np.zeros(var.dim)
            rhs[idx] = np.ceil(self.lp_model.variable_solution(var).array[idx])
            right_node = Node(self.model, parent=self, constraint=HIPSArray(diag) * var >= HIPSArray(rhs))
            return left_node, right_node


if __name__ == "__main__":
    mip_model = MIPModel(GurobiSolver())
    x1 = mip_model.add_variable("x1", var_type=VarTypes.INTEGER, lb=0, ub=8)
    x2 = mip_model.add_variable("x2", var_type=VarTypes.INTEGER, lb=0, ub=8)
    mip_model.add_constraint(2 * x1 + x2 <= 8)
    mip_model.add_constraint(-2 * x1 + 10 * x2 <= 25)
    mip_model.set_objective(x1 + x2)
    mip_model.set_mip_sense(LPSense.MAX)
    bb = BranchAndBound(mip_model)
    bb.optimize()
    print(bb._incumbent)
