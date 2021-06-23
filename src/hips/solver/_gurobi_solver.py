from hips.solver._abstract_solver import AbstractSolver
from hips.constants import Comparator, VariableBound
from hips.models._lp_model import Constraint, Variable, LinExpr, HIPSArray
import gurobipy as gb
from gurobipy import GRB
from hips.constants import LPStatus, ProblemSense
import numpy as np


class GurobiSolver(AbstractSolver):
    '''Realization of the LP model using Gurobi LP solver'''

    def __init__(self):
        super().__init__()
        self.status = LPStatus.UNKNOWN
        self.constraint_counter = 0
        env = gb.Env()
        env.setParam(GRB.Param.OutputFlag, 0)
        env.start()
        self.model = gb.Model(env=env)
        # Maps a variable to a gurobi variable
        self.var_to_gurobi_var = {}
        # Maps a HIPS constraint to a gurobi constraint
        self.constr_to_gurobi_constraint = {}
        # Maps names to hips constraints
        self.name_to_hips_constraint = {}

    def __to_gurobi_lin_expr(self, lin_expr):
        """Converts a HIPS linear expression to a Gurobi linear expression"""
        return sum(lin_expr.coefficients[var].to_numpy() @ self.var_to_gurobi_var[var.id] for var in lin_expr.vars)

    def __to_gurobi_constraint(self, constraint):
        """Converts a constraint to a Gurobi constraint
           Constraints have to be of form:
             constraint.lhs: LinearExpression
             constraint.comparator: Comparator
             constraint.rhs: Number"""
        if constraint.comparator == Comparator.LESS_EQUALS:
            return self.__to_gurobi_lin_expr(constraint.lhs) <= constraint.rhs.array.reshape(-1)
        elif constraint.comparator == Comparator.GREATER_EQUALS:
            return self.__to_gurobi_lin_expr(constraint.lhs) >= constraint.rhs.array.reshape(-1)
        else:
            return self.__to_gurobi_lin_expr(constraint.lhs) == constraint.rhs.array.reshape(-1)

    def add_constraint(self, constraint: Constraint, name=None):
        gurobi_constraint = self.__to_gurobi_constraint(constraint)
        gurobi_name = None
        if name is None:
            gurobi_name = "c{}".format(str(self.constraint_counter))
        else:
            gurobi_name = name
            self.name_to_hips_constraint[name] = constraint
        self.constraint_counter += 1
        self.constr_to_gurobi_constraint[constraint] = self.model.addConstr(gurobi_constraint, name=gurobi_name)
        self.model.update()

    def remove_constraint(self, name: str = None, constraint: Constraint = None):
        """This method assumes, that the user only removes constraints by name, that were also added with a name"""
        gurobi_constraint = None
        if name is not None:
            constraint = self.name_to_hips_constraint[name]
            del self.name_to_hips_constraint[name]
        gurobi_constraint = self.constr_to_gurobi_constraint[constraint]
        del self.constr_to_gurobi_constraint[constraint]
        self.model.remove(gurobi_constraint)
        self.model.update()

    def add_variable(self, var: Variable):
        lb = var.lb.to_numpy() if var.lb is not None else float("-inf")
        ub = var.ub.to_numpy() if var.ub is not None else float("inf")
        self.var_to_gurobi_var[var.id] = self.model.addMVar(var.dim, lb, ub, name="var{}".format(var.id))
        self.model.update()

    def remove_variable(self, var: Variable):
        self.model.remove(self.var_to_gurobi_var[var.id])
        del self.var_to_gurobi_var[var.id]
        self.model.update()

    def set_variable_bound(self, var: Variable, bound: VariableBound, value: HIPSArray):
        if bound == VariableBound.UB:
            self.var_to_gurobi_var[var.id].setAttr(GRB.Attr.UB, value.to_numpy())
        else:
            self.var_to_gurobi_var[var.id].setAttr(GRB.Attr.LB, value.to_numpy())

    def variable_solution(self, var: Variable) -> float:
        gurobivar = self.var_to_gurobi_var[var.id]
        return HIPSArray(gurobivar.x)

    def get_objective_value(self) -> float:
        return self.model.objVal

    def get_status(self) -> LPStatus:
        return self.status

    def optimize(self):
        objective = self.__to_gurobi_lin_expr(self.objective)
        sense = GRB.MAXIMIZE if self.lp_sense == ProblemSense.MAX else GRB.MINIMIZE
        self.model.setObjective(objective, sense)
        self.model.optimize()
        gurobi_status = self.model.status
        if gurobi_status == GRB.LOADED or gurobi_status == GRB.INPROGRESS:
            self.status = LPStatus.UNKNOWN
        elif gurobi_status == GRB.OPTIMAL:
            self.status = LPStatus.OPTIMAL
        elif gurobi_status == GRB.INFEASIBLE:
            self.status = LPStatus.INFEASIBLE
        elif gurobi_status == GRB.UNBOUNDED:
            self.status = LPStatus.UNBOUNDED
        elif gurobi_status == GRB.INF_OR_UNBD:
            self.model.setParam(GRB.Param.DualReductions, 0)
            self.model.optimize()
            reoptimize_status = self.model.status
            if reoptimize_status == GRB.INFEASIBLE:
                self.status = LPStatus.INFEASIBLE
            elif reoptimize_status == GRB.UNBOUNDED:
                self.status = LPStatus.UNBOUNDED
            else:
                self.status = LPStatus.ERROR
        else:
            self.status = LPStatus.ERROR

    def __str__(self):
        return str(self.model)
