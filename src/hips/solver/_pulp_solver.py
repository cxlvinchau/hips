import pulp as pl

from hips.constants import LPStatus, ProblemSense
from hips.models._lp_model import Variable, LinExpr, Constraint
from hips.solver._abstract_solver import AbstractSolver
from hips.constants import Comparator, LPStatus


class PulpSolver(AbstractSolver):
    """
    Wraps the solver provided by pulp (see https://github.com/coin-or/pulp). pulp itself is a wrapper for various
    linear program solvers, such as GLPK, CLP, Gurobi, Cplex, MOSEK, XPRESS, etc. However, pulp does not support the
    removal of variables or constraints, making it rather inefficient. We advise you to use our
    :class:`GurobiSolver <hips.solver.gurobi_solver.GurobiSolver>`, since the removal of constraints and variables is
    supported there, possibly leading to a performance gain.
    """

    def __init__(self, problem_name="LP", solver=None):
        self.model = pl.LpProblem(problem_name, pl.LpMaximize)
        self._var_to_pulp_var = dict()
        self.status = LPStatus.UNKNOWN
        self.solver = solver
        self.lp_sense = ProblemSense.MAX
        self.objective = None
        self._constr_to_name = dict()
        self._constr_counter = 0

    def __to_pulp_constr(self, constr: Constraint):
        expr = self.__to_pulp_expr(constr.lhs)
        if constr.comparator == Comparator.LESS_EQUALS:
            return expr <= constr.rhs
        elif constr.comparator == Comparator.GREATER_EQUALS:
            return expr >= constr.rhs
        else:
            return expr == constr.rhs

    def __to_pulp_expr(self, expr: LinExpr):
        return pl.lpSum([expr.coefficients[var] * self._var_to_pulp_var[var.id] for var in expr.vars])

    def add_constraint(self, constraint: Constraint, name=None):
        if not name:
            self._constr_counter += 1
        # Get name
        name = name if name else "_constr{}".format(self._constr_counter)
        constr = self.__to_pulp_constr(constraint)
        # Map constraint to name
        self._constr_to_name[constraint] = name
        self.model.addConstraint(constr, name)

    def remove_constraint(self, name: str = None, constraint: Constraint = None):
        """
        Currently not supported

        :param name:
        :param constraint:
        :return:
        """
        # TODO
        pass

    def add_variable(self, var: Variable):
        self._var_to_pulp_var[var.id] = pl.LpVariable("var{}".format(var.id), var.lb, var.ub)

    def remove_variable(self, var: Variable):
        """
        Currently not supported

        :param var:
        :return:
        """
        # TODO
        pass

    def set_objective(self, objective: LinExpr):
        self.objective = objective
        obj = self.__to_pulp_expr(objective)
        self.model.setObjective(obj)

    def set_lp_sense(self, lp_sense: ProblemSense):
        if lp_sense != self.lp_sense:
            self.lp_sense = lp_sense
            self.objective = -1 * self.objective
            self.set_objective(self.objective)

    def variable_solution(self, var: Variable) -> float:
        return pl.value(self._var_to_pulp_var[var.id])

    def get_objective_value(self) -> float:
        return pl.value(self.objective)

    def optimize(self):
        res = self.model.solve(solver=self.solver)
        if res == "Optimal":
            self.status = LPStatus.OPTIMAL
        elif res == "Not Solved":
            self.status = LPStatus.UNKNOWN
        elif res == "Infeasible":
            self.status = LPStatus.INFEASIBLE
        elif res == "Unbounded":
            self.status = LPStatus.UNBOUNDED
        else:
            self.status = LPStatus.UNKNOWN

    def get_status(self) -> LPStatus:
        return self.status
