from scipy.optimize import linprog
import numpy as np

from hips.constants import LPStatus, Comparator, LPSense
from hips.solver._abstract_solver import AbstractSolver
from hips.models._lp_model import Constraint, Variable, LinExpr


class ScipySolver(AbstractSolver):
    """Realization of the LP model using the SciPy LP solver"""

    def __init__(self):
        super().__init__()
        self.A = None
        self.b = None
        self.c = None
        self.constraints = list()
        self.vars = list()
        self.objective = None
        self.lp_sense = None
        self.variable_values = None
        self.status = None
        self.objective_value = None

    def add_constraint(self, constraint: Constraint, name=None):
        self.constraints.append(constraint)

    def remove_constraint(self, name: str = None, constraint: Constraint = None):
        self.constraints.remove(constraint)

    def add_variable(self, var: Variable):
        if var.lb is not None:
            self.add_constraint(var >= var.lb)
        if var.ub is not None:
            self.add_constraint(var <= var.ub)
        self.vars.append(var)

    def remove_variable(self, var: Variable):
        self.vars.remove(var)

    def set_objective(self, objective : LinExpr):
        self.objective = objective

    def set_lp_sense(self, lp_sense : LPSense):
        self.lp_sense = lp_sense

    def variable_solution(self, var : Variable) -> float:
        return self.variable_values[self.vars.index(var, 0, var.id + 1)]

    def get_objective_value(self) -> float:
        return self.objective_value

    def get_status(self) -> LPStatus:
        return self.status

    # For testing purposes
    def convert_to_scipy(self):
        self.b = []
        self.A = []
        for constraint in self.constraints:
            a = np.zeros(len(self.vars))
            beta = constraint.rhs
            for var in self.vars:
                a[self.vars.index(var, 0, var.id + 1)] = constraint.lhs.coefficients.get(var, 0)
            if constraint.comparator == Comparator.GREATER_EQUALS:
                a = np.array([-1*aj for aj in a])
                beta = -1*beta
            elif constraint.comparator == Comparator.EQUALS:
                self.A.append(np.array([-1*aj for aj in a]))
                self.b.append(-1*constraint.rhs)

            self.A.append(a)
            self.b.append(beta)

        self.c = np.zeros(len(self.vars))
        for var in self.vars:
            self.c[self.vars.index(var, 0, var.id + 1)] = self.objective.coefficients.setdefault(var,0)

        self.A = np.array(self.A)
        self.c = np.array(self.lp_sense.value * self.c)
        self.b = np.array(self.b)

    def optimize(self):
        self.convert_to_scipy()
        res = linprog(self.c,A_ub=self.A,b_ub = self.b,method="revised simplex")
        if res.status == 0:
            self.status = LPStatus.OPTIMAL
            self.variable_values = res.x
            self.objective_value = self.lp_sense.value * res.fun
        elif res.status == 2:
            self.status = LPStatus.INFEASIBLE
        elif res.status == 3:
            self.status = LPStatus.UNBOUNDED
        else:
            self.status = LPStatus.UNKNOWN
