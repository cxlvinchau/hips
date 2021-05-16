from hips.constants import VarTypes
from hips.models import LPModel
from hips.utils import is_close
import numpy as np
import math


class MIPModel:
    """
    Represents a mixed-integer program. In contrast to the :py:class:`LPModel <hips.models.lp_model.LPModel>`, this
    class allows for specification of the variable types, i.e. continuous, binary or integer. Under the hood, the
    :py:class:`LPModel <hips.models.lp_model.LPModel>` is used.
    """

    def __init__(self, solver, binary_variables=[], integer_variables=[]):
        self.lp_model = LPModel(solver)
        self.integer_variables = integer_variables
        self.binary_variables = binary_variables

    def add_constraint(self, constraint):
        """
        Adds a linear constraint to the mixed-integer program.

        :param constraint: Constraint of type :py:class:`Constraint <hips.models.lp_model.Constraint>`
        :return: None
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
        :return: :py:class:`Variable <hips.models.lp_model.Variable>`
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
        :return: None
        """
        self.lp_model.set_objective(objective)

    def set_mip_sense(self, lp_sense):
        """
        Sets the type of the mixed-integer program.

        :param lp_sense: :py:class:`LPSense <hips.constants.LPSense>`
        :return: None
        """
        self.lp_model.set_lp_sense(lp_sense)

    def __str__(self):
        return "\n".join([str(self.lp_model), str(self.binary_variables), str(self.integer_variables)])

    def is_feasible(self, variable_solutions):
        """
        Checks whether the given solution is feasible for the MIP

        :param variable_solutions: Dictionary mapping variables to solutions
        :return: True if solution is feasible else False
        """
        # Check if relaxation is feasible
        if not self.lp_model.is_feasible(variable_solutions):
            return False
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
        return True


