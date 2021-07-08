from hips.constants import VarTypes, Comparator, ProblemSense
from hips.models import LPModel
from hips.utils import is_close
import numpy as np
import math


class MIPModel:
    """Representation of a mixed-integer program

    Represents a mixed-integer program. In contrast to the :py:class:`LPModel <hips.models.lp_model.LPModel>`, this
    class allows for specification of the variable types, i.e. continuous, binary or integer. Under the hood, the
    :py:class:`LPModel <hips.models.lp_model.LPModel>` is used. By default, a maximization problem is solved.
    """

    def __init__(self, solver):
        """Constructor

        :param solver: A linear program solver
        """
        self.lp_model = LPModel(solver)
        self.integer_variables = []
        self.binary_variables = []
        self.variables = self.lp_model.vars

    def add_constraint(self, constraint):
        """
        Adds a linear constraint to the mixed-integer program.

        :param constraint: Constraint of type :py:class:`Constraint <hips.models.lp_model.Constraint>`
        """
        self.lp_model.add_constraint(constraint)

    def add_variable(self, name, var_type=VarTypes.CONTINUOUS, lb=0, ub=None, dim=1):
        """
        Adds a variable to the mixed-integer program.

        :param name: Name of the variable
        :param var_type: Type of the variable, either continuous, binary or integer. See :py:class:`VarTypes <hips.constants.VarTypes>`.
        :param lb: Lower bound of the variable, by default 0.
        :param ub: Upper bound of the variable, by default the variable is unbounded. Note that an integer variable has to be bounded from above.
        :param dim: dimension of the variable, by default 1
        :return: A variable, instance of :py:class:`Variable <hips.models.lp_model.Variable>`
        """
        # Set bounds for binary variables
        if var_type == VarTypes.BINARY:
            var = self.lp_model.add_variable(name, lb=0, ub=1, dim=dim)
            self.binary_variables.append(var)
        elif var_type == VarTypes.INTEGER:
            if ub is None:
                raise ValueError("Please set an upper bound on integer variable {}".format(name))
            var = self.lp_model.add_variable(name, lb=lb, ub=ub, dim=dim)
            self.integer_variables.append(var)
        else:
            var = self.lp_model.add_variable(name, lb=lb, ub=ub, dim=dim)
        return var

    def set_objective(self, objective):
        """
        Sets the objective function of the mixed-integer program.

        :param objective: A linear expression of type :py:class:`LinExpr <hips.models.lp_model.LinExpr>`
        """
        self.lp_model.set_objective(objective)

    def set_mip_sense(self, mip_sense: ProblemSense):
        """
        Sets the type of the mixed-integer program.

        :param mip_sense: Specifies the sense of the linear program, see :py:class:`ProblemSense <hips.constants.ProblemSense>`
        """
        self.lp_model.set_lp_sense(mip_sense)

    def __str__(self):
        return "\n".join([str(self.lp_model), str(self.binary_variables), str(self.integer_variables)])

    def is_feasible(self, variable_solutions):
        """
        Checks whether the given solution is feasible for the MIP

        :param variable_solutions: Dictionary mapping variables to solutions
        :return: ``True`` if solution is feasible else ``False``
        """
        # Check if binary variables are 0 and 1
        for variable in self.binary_variables:
            for value in np.unique(variable_solutions[variable].to_numpy()):
                if not is_close(value, 0.0) and not is_close(value, 1.0):
                    return False
        # Check if integer variables are integer
        for variable in self.integer_variables:
            for value in np.unique(variable_solutions[variable].to_numpy()):
                if not is_close(value, math.floor(value)) and not is_close(value, math.ceil(value)):
                    return False
        # Check if relaxation is feasible
        if not self.lp_model.is_feasible(variable_solutions):
            return False
        return True

    def trivially_roundable(self):
        """
        Checks if the all variables of the model are trivially roundable. If so, fix the variables to the rounded values
        and optimize, such that the corresponding objective value can be fetched.

        1. A variable :math:`x_j` is called trivially down-roundable, if all coefficients :math:`a_{ij}` of the corresponding column of the
        matrix :math:`A` are non negative, hence :math:`A_j \geq 0`.
        2. A variable :math:`x_j` is called trivially up-roundable, if all coefficients :math:`a_{ij}` of the corresponding column of the
        matrix :math:`A` are non positive, hence :math:`A_j \leq 0`.
        3. A variable is called trivially roundable, if it is trivially down-roundable or trivially up-roundable.

        :Source: Berthold_Primal_Heuristics_For_Mixed_Integer_Programs.pdf; Page 3, Definition 1.5;

        :return: A tuple containing the dictionaries trivially_down_roundable, trivially_up_roundable
                 trivially_down_roundable:      key: Variable, element: array(Boolean)
                 trivially_up_roundable:        key: Variable, element: array(Boolean)
        """
        trivially_up_roundable = {x: np.repeat(True, x.dim) for x in self.integer_variables + self.binary_variables}
        trivially_down_roundable = {x: np.repeat(True, x.dim) for x in self.integer_variables + self.binary_variables}
        for constraint in self.lp_model.constraints:
            for var in constraint.lhs.vars:
                if var not in self.integer_variables + self.binary_variables:
                    continue
                coefficients = constraint.lhs.coefficients
                if constraint.comparator == Comparator.LESS_EQUALS:
                    trivially_down_roundable[var] = [B1 and B2 for B1,B2 in zip(trivially_down_roundable[var], [all(coefficients[var].to_numpy()[:,i] >= 0) for i in range(var.dim)])]
                    trivially_up_roundable[var] = [B1 and B2 for B1,B2 in zip(trivially_up_roundable[var], [all(coefficients[var].to_numpy()[:,i] <= 0) for i in range(var.dim)])]
                elif constraint.comparator == Comparator.GREATER_EQUALS:
                    trivially_down_roundable[var] = [B1 and B2 for B1,B2 in zip(trivially_down_roundable[var], [all(coefficients[var].to_numpy()[:,i] <= 0) for i in range(var.dim)])]
                    trivially_up_roundable[var] = [B1 and B2 for B1,B2 in zip(trivially_up_roundable[var], [all(coefficients[var].to_numpy()[:,i] >= 0) for i in range(var.dim)])]
                else: # constraint.comparator == Comparator.EQUALS
                    trivially_down_roundable[var] = [B1 and B2 for B1,B2 in zip(trivially_down_roundable[var], [all(coefficients[var].to_numpy()[:,i] == 0) for i in range(var.dim)])]
                    trivially_up_roundable[var] = [B1 and B2 for B1,B2 in zip(trivially_up_roundable[var], [all(coefficients[var].to_numpy()[:,i] == 0) for i in range(var.dim)])]
        return trivially_down_roundable, trivially_up_roundable

    def get_variables(self):
        """Returns all variables of the problem

        :return: A list of variables. Elements are instances of :class:`Variable <hips.models.Variable>`
        """
        return self.lp_model.get_variables()

    def summary(self):
        """
        Prints a summary of the MIP
        """
        self.lp_model.summary()
        num_bin_variables = sum([var.dim for var in self.binary_variables])
        num_int_variables = sum([var.dim for var in self.integer_variables])
        print(f"#Binary variables: {num_bin_variables}")
        print(f"#Integer variables: {num_int_variables}")

