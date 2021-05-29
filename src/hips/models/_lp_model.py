from hips.constants import Comparator, VarTypes, LPStatus, LPSense, NUMERICAL_TYPES, VariableBound
import numpy as np


class LPModel:
    """Representation of a linear program"""

    def __init__(self, lp_solver):
        self.status = LPStatus.UNKNOWN
        self.constraint_counter = 0
        self.constraint_names = dict()
        self.constraints = list()
        self.vars = set()
        self.id_counter = 0
        self.objective = None
        self.lp_sense = LPSense.MAX
        self.objective_value = None
        self.concrete_solver = lp_solver

    def add_constraint(self, constraint, name=None):
        """Adds a constraint to the linear program"""
        if name in self.constraint_names.keys():
            raise Exception("Cannot add two constraints with the same name.")
        if not (constraint.vars - self.vars):
            self.constraints.append(constraint)
            if name is None:
                self.constraint_names.update({("c" + str(self.constraint_counter)): constraint})
            else:
                self.constraint_names.update({name: constraint})
            self.constraint_counter += 1
            # Add constraint to concrete solver
            self.concrete_solver.add_constraint(constraint, name=name)
            return constraint
        else:
            raise Exception("Illegal constraint")

    def remove_constraint(self, name=None, constraint=None):
        if name is None and constraint is None:
            raise Exception("Neither name nor constraint were specified for removal.")
        # Case name = None, fetch name by constraint
        internal_name = name
        if internal_name is None:
            for na, co in self.constraint_names.items():
                if co == constraint:
                    internal_name = na
                    break
        # Case constraint = None, fetch constraint by name
        if constraint is None:
            constraint = self.constraint_names[internal_name]
        # Update internal structures
        self.constraints.remove(constraint)
        del self.constraint_names[internal_name]
        # Remove constraint from concrete solver
        self.concrete_solver.remove_constraint(name=name, constraint=constraint)

    def add_variable(self, name, lb=0, ub=None, dim=1):
        """Adds a variable to the linear program"""
        if name in [v.name for v in self.vars]:
            raise Exception("Cannot add two variables with the same name")
        var = Variable(name, id=self.id_counter, lb=lb, ub=ub, dim=dim)
        self.id_counter += 1
        self.vars.add(var)
        # Add variable to concrete solver
        self.concrete_solver.add_variable(var)
        return var

    def remove_variable(self, var):
        if var not in self.vars:
            raise Exception("Cannot remove a non existing variable")
        self.vars.remove(var)
        # Remove variable from concrete solver
        self.concrete_solver.remove_variable(var)

    def set_variable_bound(self, var, bound: VariableBound, value):
        if isinstance(value, NUMERICAL_TYPES):
            value = value * HIPSArray(np.ones(var.dim))
        if not isinstance(value, HIPSArray):
            value = HIPSArray(value)
        if not var.dim == value.shape[0]:
            raise Exception("The specified bound does not have the same dimension as the specified variable.")
        if bound == VariableBound.UB:
            var.ub = value
        elif bound == VariableBound.LB:
            var.lb = value
        else:
            return
        self.concrete_solver.set_variable_bound(var, bound, value)

    def set_objective(self, objective):
        """Sets the objective of the linear program"""
        if type(objective) == Variable:
            objective = LinExpr(vars={objective}, coefficients={objective: objective.coefficient})
        if type(objective) != LinExpr:
            raise Exception("Illegal objective. Objective has to be of type LinExp")
        else:
            self.objective = objective
            # Set objective in concrete solver
            self.concrete_solver.set_objective(objective)

    def set_lp_sense(self, lp_sense: LPSense):
        """Sets the type of the linear program, i.e. minimization or maximization. Use LPSense.MAX or LPSense.MIN"""
        if lp_sense not in [LPSense.MAX, LPSense.MIN]:
            raise Exception("Illegal LP type")
        else:
            self.lp_sense = lp_sense
            # Set lp type in concrete solver
            self.concrete_solver.set_lp_sense(lp_sense)

    def __str__(self):
        return "Objective:\n" + str(self.objective) + "\nConstraints:\n" + "\n".join([str(c) for c in self.constraints])

    def variable_solution(self, var):
        """Returns the optimal value for the given variable"""
        return self.concrete_solver.variable_solution(var)

    def get_objective_value(self):
        """Returns the optimal value of the linear program"""
        return self.concrete_solver.get_objective_value()

    def optimize(self):
        """Optimizes the linear program"""
        self.concrete_solver.optimize()

    def get_variables(self):
        return self.vars

    def get_status(self):
        return self.concrete_solver.get_status()

    def is_feasible(self, variable_solutions: dict):
        for constr in self.constraints:
            if not all(constr.eval(variable_solutions)):
                return False
        for variable in variable_solutions:
            if variable.lb is not None and any(variable_solutions[variable] < variable.lb):
                return False
            if variable.ub is not None and any(variable_solutions[variable] > variable.ub):
                return False
        return True


class Constraint:
    """Represents a linear constraint of an LP"""

    def __init__(self, lhs, comparator, rhs):
        self.MAP = {Comparator.LESS_EQUALS: "<=", Comparator.EQUALS: "=", Comparator.GREATER_EQUALS: ">="}
        if type(lhs) != LinExpr and type(lhs) != Variable:
            raise TypeError("lhs is not a linear expression or variable")
        if not isinstance(rhs, NUMERICAL_TYPES) and type(rhs) != HIPSArray:
            raise TypeError("rhs is not of type float or int")
        if comparator not in [Comparator.LESS_EQUALS, Comparator.EQUALS, Comparator.GREATER_EQUALS]:
            raise TypeError("Unknown type")
        if type(lhs) == Variable:
            self.lhs = LinExpr(lhs, {lhs: HIPSArray(np.ones((lhs.dim, 1)))})
        else:
            self.lhs = lhs
        if isinstance(rhs, NUMERICAL_TYPES):
            self.rhs = rhs * HIPSArray(np.ones((lhs.dim, 1)))
        elif type(rhs) == HIPSArray:
            self.rhs = HIPSArray(rhs.to_numpy().reshape(self.lhs.dim, 1))
        self.vars = set(lhs.vars)
        self.comparator = comparator

    def __str__(self):
        return str("{} {} {}".format(str(self.lhs), str(self.MAP[self.comparator]), str(self.rhs)))

    def __hash__(self):
        return int(sum([np.sum(arr.to_numpy().reshape(-1)) for arr in self.lhs.coefficients.values()]) *
                   + np.sum(self.rhs.to_numpy().reshape(-1)) + self.comparator.value)

    def __eq__(self, other):
        if isinstance(other, Constraint):
            # Compare comparator
            if other.comparator != self.comparator:
                return False
            # Compare lhs
            if len(other.lhs.coefficients) != len(self.lhs.coefficients):
                return False
            for var in self.lhs.coefficients:
                if var not in other.lhs.coefficients:
                    return False
                if not np.array_equal(self.lhs.coefficients[var], other.lhs.coefficients[var]):
                    return False
            # Compare rhs
            return np.array_equal(self.rhs, other.rhs)
        return False

    def eval(self, variable_solutions: dict, eps=0.0002):
        from hips.utils import is_close
        eval_lhs = self.lhs.eval(variable_solutions)
        if self.comparator == Comparator.LESS_EQUALS:
            return eval_lhs.reshape(-1) <= (self.rhs + eps).reshape(-1)
        if self.comparator == Comparator.GREATER_EQUALS:
            return eval_lhs.reshape(-1) >= (self.rhs - eps).reshape(-1)
        if self.comparator == Comparator.EQUALS:
            return is_close(eval_lhs.reshape(-1), self.rhs.reshape(-1))
        raise ValueError("Could not evaluate constraint")


class LinExpr:
    """Represents a linear expression, used as lhs of a constraint"""

    def __init__(self, vars=set(), coefficients=dict()):
        self.vars = vars
        self.coefficients = coefficients
        # Check if dimension match
        self.dim = min([e.shape[0] for e in coefficients.values()])
        if self.dim != max([e.shape[0] for e in coefficients.values()]):
            raise ValueError("Dimensions do not match")

    def __add__(self, other):
        if type(other) == LinExpr:
            new_var = self.vars | other.vars
            new_coefficients = dict(self.coefficients)
            new_coefficients.update(other.coefficients)
            for var in self.vars & other.vars:
                new_coefficients[var] = self.coefficients[var] + other.coefficients[var]
            return LinExpr(new_var, new_coefficients)
        elif type(other) == Variable:
            return self + LinExpr(set([other]), {other: HIPSArray((1, other.dim))})
        elif type(other) == int or type(other) == float:
            if (other == 0):
                return self
        else:
            raise Exception("Not a variable or linear expression")

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if type(other) == int or type(other) == float:
            new_coefficients = dict(self.coefficients)
            for k in new_coefficients:
                new_coefficients[k] *= other
            return LinExpr(set(self.vars), new_coefficients)
        else:
            raise Exception("Illegal multiplication with LinExp")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        return " + ".join([(str(self.coefficients[var]) + " * " + str(var)) for var in self.vars])

    def __eq__(self, other):
        if isinstance(other, NUMERICAL_TYPES) or type(other) == HIPSArray:
            return Constraint(self, Comparator.EQUALS, other)
        else:
            raise Exception("Illegal equality operator used on LinExp")

    def __ge__(self, other):
        if isinstance(other, NUMERICAL_TYPES) or type(other) == HIPSArray:
            return Constraint(self, Comparator.GREATER_EQUALS, other)
        else:
            raise Exception("Illegal equality operator used on LinExp")

    def __le__(self, other):
        if isinstance(other, NUMERICAL_TYPES) or type(other) == HIPSArray:
            return Constraint(self, Comparator.LESS_EQUALS, other)
        else:
            raise Exception("Illegal equality operator used on LinExp")

    def eval(self, variable_solutions: dict):
        result = 0
        for var in self.vars:
            solution = variable_solutions[var]
            result += self.coefficients[var].to_numpy().dot(solution.to_numpy())
        return HIPSArray(result)


class Variable:
    """Represents a variable in an LP"""

    def __init__(self, name, id=0, var_type=VarTypes.CONTINUOUS, lb=0, ub=None, dim=1):
        """By default the variable is continuous and 1-dimensional"""
        self.name = name
        self.coefficient = HIPSArray((1, dim))
        self.id = id
        self.var_type = var_type
        self.dim = dim
        # Set lower and upper bound
        if isinstance(lb, NUMERICAL_TYPES):
            self.lb = lb * HIPSArray(np.ones(self.dim))
        elif (isinstance(lb, HIPSArray) and lb.shape[0] == self.dim) or lb is None:
            self.lb = lb
        else:
            raise ValueError("Invalid lower bound {}".format(lb))
        if isinstance(ub, NUMERICAL_TYPES):
            self.ub = ub * HIPSArray(np.ones(self.dim))
        elif (isinstance(ub, HIPSArray) and ub.shape[0] == self.dim) or ub is None:
            self.ub = ub
        else:
            raise ValueError("Invalid upper bound {}".format(ub))

    def __add__(self, other):
        if type(other) == LinExpr:
            return other + self
        elif type(other) == Variable:
            coefficients = dict()
            if self == other:
                coefficients[self] = HIPSArray((1, self.dim))
            else:
                coefficients[self] = HIPSArray((1, self.dim))
                coefficients[other] = HIPSArray((1, other.dim))
            return LinExpr(set([self, other]), coefficients)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, NUMERICAL_TYPES):
            return LinExpr(set([self]), {self: other * HIPSArray((1, self.dim))})
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, NUMERICAL_TYPES):
            return LinExpr(set([self]), {self: other * HIPSArray((1, self.dim))})
        return NotImplemented

    def __str__(self):
        if self.dim > 1:
            return self.name + "[{}]".format(self.dim)
        return self.name

    def __repr__(self):
        return "Variable({})".format(self.name)

    def __eq__(self, other):
        if type(other) == Variable:
            return self.name == other.name and self.id == other.id
        if type(other) == int:
            return LinExpr(set([self]), {self: HIPSArray(np.identity(self.dim))}) == other
        return False

    def __ge__(self, other):
        if isinstance(other, NUMERICAL_TYPES) or isinstance(other, HIPSArray):
            return LinExpr(set([self]), {self: HIPSArray(np.identity(self.dim))}) >= other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, NUMERICAL_TYPES) or isinstance(other, HIPSArray):
            return LinExpr(set([self]), {self: HIPSArray(np.identity(self.dim))}) <= other
        return NotImplemented

    def __hash__(self):
        return hash(self.name)


class HIPSArray:
    """
    Wrapper class for numpy array
    """

    def __init__(self, arg):
        if type(arg) in [list, np.ndarray]:
            array = arg
            self.array = np.array(array)
        elif type(arg) in [tuple]:
            self.array = np.ones(arg)
        if len(self.array.shape) > 2:
            raise ValueError("HIPSArray with illegal shape {}".format(self.array.shape))
        self.shape = self.array.shape

    def __abs__(self):
        return abs(self.array)

    def __add__(self, other):
        if type(other) == HIPSArray:
            return HIPSArray(self.array + other.array)
        if isinstance(other, NUMERICAL_TYPES):
            return HIPSArray(self.array + other)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, NUMERICAL_TYPES):
            return HIPSArray(self.array * other)
        elif type(other) == Variable:
            if self.shape[-1] != other.dim:
                raise ValueError(
                    ("HIPSArray shape {}, and Variable dimension {} do not match").format(self.shape, other.dim))
            return LinExpr(set([other]), {other: HIPSArray(self.array.reshape(-1, other.dim))})
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, NUMERICAL_TYPES):
            return HIPSArray(self.array * other)
        return NotImplemented

    def __sub__(self, other):
        return self + (-1 * other)

    def __str__(self):
        return str(self.array)

    def __repr__(self):
        return "HIPSArray({})".format(self.array)

    def __round__(self, n=None):
        return HIPSArray(np.around(self.array, decimals=n if n else 0))

    def __le__(self, other):
        if isinstance(other, HIPSArray):
            return self.array <= other.array
        return self.array <= other

    def __ge__(self, other):
        if isinstance(other, HIPSArray):
            return self.array >= other.array
        return self.array >= other

    def __lt__(self, other):
        if isinstance(other, HIPSArray):
            return self.array < other.array
        return self.array < other

    def __gt__(self, other):
        if isinstance(other, HIPSArray):
            return self.array > other.array
        return self.array > other

    def __eq__(self, other):
        if isinstance(other, HIPSArray):
            return self.array == other.array
        return self.array == other

    def to_numpy(self):
        return self.array

    def to_np(self):
        return self.to_numpy()

    def reshape(self, shape):
        return HIPSArray(self.array.reshape(shape))
