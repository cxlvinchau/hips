import warnings

from cylp.cy import CyClpSimplex
from cylp.py.modeling.CyLPModel import CyLPArray

from hips.solver._abstract_solver import AbstractSolver
from hips.constants import Comparator
from hips.constants import LPStatus, LPSense
from hips.models import HIPSArray


class ClpSolver(AbstractSolver):
    """
    Implements the IConcreteSolver class and wraps CyLP. Note that the ClpSolver may require
    special attention when it comes to removing variables because the implementation of CyLP is not particularly stable.
    See open GitHub issues: https://github.com/coin-or/CyLP/issues.
    """

    def __init__(self):
        super().__init__()
        self.status = LPStatus.UNKNOWN
        self.constraint_counter = 0
        self.model = CyClpSimplex()
        # Maps a variable to a Clp variable
        self.var_to_clp_var = {}
        # Maps a HIPS constraint to a Clp constraint
        self.constr_to_clp_constr = {}
        # Maps a CLP constraint to a name
        self.clp_constr_to_name = {}
        # Maps vars to the number of constraints it is contained in
        self.var_to_nconstr = {}
        # Maps constr to variables
        self.constr_to_vars = {}

    def _to_clp_lin_expr(self, lin_expr):
        """
        Converts a HIPS linear expression to a CLP linear expression
        """
        return sum(CyLPArray(lin_expr.coefficients[var].to_numpy()) * self.var_to_clp_var[var.id] for var in lin_expr.vars)

    def _to_clp_constr(self, constraint):
        """
        Converts a constraint to a CLP constraint
        """
        if constraint.comparator == Comparator.GREATER_EQUALS:
            return self._to_clp_lin_expr(constraint.lhs) >= CyLPArray(constraint.rhs.array)
        elif constraint.comparator == Comparator.EQUALS:
            return self._to_clp_lin_expr(constraint.lhs) == CyLPArray(constraint.rhs.array)
        else:
            return self._to_clp_lin_expr(constraint.lhs) <= CyLPArray(constraint.rhs.array)

    def add_variable(self, var):
        self.var_to_clp_var[var.id] = self.model.addVariable("var{}".format(var.id), var.dim)
        if var.lb is not None:
            self.model.addConstraint(self.var_to_clp_var[var.id] >= CyLPArray(var.lb.array))
        if var.ub is not None:
            self.model.addConstraint(self.var_to_clp_var[var.id] <= CyLPArray(var.ub.array))
        self.var_to_nconstr[var.id] = 0

    def add_constraint(self, constraint, name=None):
        # Compute clp constraint
        constr = self._to_clp_constr(constraint)
        # Map LP constraint to corresponding clp constraint
        self.constr_to_clp_constr[constraint] = constr
        # Generate name for constraint
        self.clp_constr_to_name[constr] = ("c" + str(self.constraint_counter)) if name is None else name
        # Memorize which variables are present in the given constraint
        self.constr_to_vars[self.clp_constr_to_name[constr]] = constraint.vars
        for var in constraint.vars:
            self.var_to_nconstr[var.id] += 1
        # Add constraint to CLP model
        self.model.addConstraint(constr, name=self.clp_constr_to_name[constr])
        self.constraint_counter += 1

    def variable_solution(self, var):
        clp_var = self.var_to_clp_var[var.id]
        return HIPSArray(self.model.primalVariableSolution[clp_var.name])

    def optimize(self):
        # Set objective function with corresponding sense
        self.model.objective = self.lp_sense.value * self._to_clp_lin_expr(self.objective)
        self.model.primal()
        clp_status = self.model.getStatusCode()
        if clp_status == -1:
            self.status = LPStatus.UNKNOWN
        elif clp_status == 0:
            self.status = LPStatus.OPTIMAL
        elif clp_status == 1:
            self.status = LPStatus.INFEASIBLE
        elif clp_status == 2:
            self.status = LPStatus.UNBOUNDED
        else:
            self.status = LPStatus.ERROR

    def remove_constraint(self, name=None, constraint=None):
        try:
            name = name if name else self.clp_constr_to_name[self._to_clp_constr(constraint)]
            variables = self.constr_to_vars[name]
            if not variables.intersection(set(self.var_to_clp_var.keys())):
                for var in variables:
                    self.var_to_nconstr[var.id] -= 1
                self.model.removeConstraint(name)
        except:
            warnings.warn("Constraint {} could not be removed".format(name))

    def get_status(self):
        return self.status

    def get_objective_value(self):
        return self.model.objectiveValue * self.lp_sense.value

    def remove_variable(self, var):
        if var.id not in self.var_to_clp_var:
            return
        if self.var_to_nconstr[var.id] == 0:
            del self.var_to_clp_var[var.id]
            del self.var_to_nconstr[var.id]
            return
        clp_var = self.var_to_clp_var[var.id]
        self.model.removeVariable(clp_var.name)
        del self.var_to_clp_var[var.id]
