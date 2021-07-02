from hips.constants import Comparator, VarTypes, LPStatus, ProblemSense, NUMERICAL_TYPES, VariableBound
import numpy as np


class LPModel:
    """Representation of a linear program

    This class implements a representation of a linear program. It provides a simple interface to create, update and
    optimize linear programs.
    """

    def __init__(self, lp_solver):
        """Constructor

        :param lp_solver: A concrete implementation of linear program solver. ``lp_solver`` has to be an instance of
            :class:`hips.solver.GurobiSolver` or :class:`hips.solver.ClpSolver`
        """
        self.status = LPStatus.UNKNOWN
        self.constraint_counter = 0
        self.constraint_names = dict()
        self.constraints = list()
        self.vars = set()
        self.id_counter = 0
        self.objective = None
        self.lp_sense = ProblemSense.MAX
        self.objective_value = None
        self.concrete_solver = lp_solver

    def add_constraint(self, constraint, name=None):
        """Adds a constraint to the linear program

        This method adds the given constraint to the linear program.

        :param constraint: A constraint, an instance of :class:`hips.models.Constraint`
        :param name: Name of the constraint. This argument is optional.
        """
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
        """Removes a constraint

        This method removes a constraint. Either the constraint is given or its name.

        :param name: Name of the constraint
        :param constraint: A constraint, an instance of :class:`hips.models.Constraint
        """
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
        """Adds a variable to the linear program

        This method adds a variable to the linear program. Variables can be high-dimensional and can have lower and higher
        bounds. For more details, please see :class:`hips.models.Variable`.

        :param name: Name of the variable
        :param lb: Lower bound of the variable. By default the lower bound is :math:`0`. To set the bound to :math:`-\infty`
            set ``lb`` to ``None``. ``lb`` has to be an instance of :class:`hips.models.HIPSArray` if the variable has a dimension greater than :math:`1`
        :param ub: Upper bound of the variable. By default the upper bound is :math:`\infty`. ``ub`` has to be an instance
            of :class:`hips.models.HIPSArray` if the variable has a dimension greater than :math:`1`
        :param dim: Dimension of the variable. By default the variable has dimension :math:`1`
        :return: A variable, an instance of :class:`hips.models.Variable`
        """
        if name in [v.name for v in self.vars]:
            raise Exception("Cannot add two variables with the same name")
        var = Variable(name, id=self.id_counter, lb=lb, ub=ub, dim=dim)
        self.id_counter += 1
        self.vars.add(var)
        # Add variable to concrete solver
        self.concrete_solver.add_variable(var)
        return var

    def remove_variable(self, var):
        """Removes a given variable

        This method removes a given variable from the linear program.

        :param var: Variable to be removed. Instance of :class:`hips.models.Variable`
        """
        if var not in self.vars:
            raise Exception("Cannot remove a non existing variable")
        self.vars.remove(var)
        # Remove variable from concrete solver
        self.concrete_solver.remove_variable(var)

    def set_variable_bound(self, var, bound: VariableBound, value):
        """Sets/updates the bound of a variable

        This method sets/updates the bound of the given variable.

        :param var: Variable whose bound should be set/updated. Instance of :class:`hips.models.Variable`
        :param bound: Species whether the lower or upper bound should be set/updated.
        :param value: Value of the bound. Instance of :class:`hips.models.HIPSArray`
        """
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
        """Sets the objective of the linear program

        This method sets the objective function of the linear program.

        :param objective: Objective function of the linear program. Instance of :class:`hips.models.LinExpr`
        """
        if type(objective) == Variable:
            objective = LinExpr(vars={objective}, coefficients={objective: objective.coefficient})
        if type(objective) != LinExpr:
            raise Exception("Illegal objective. Objective has to be of type LinExp")
        else:
            self.objective = objective
            # Set objective in concrete solver
            self.concrete_solver.set_objective(objective)

    def set_lp_sense(self, lp_sense: ProblemSense):
        """Sets the sense of the linear program

        This method specifies the sense of the linear program, i.e. whether the program should be minimized or maximized.

        :param lp_sense: The sense of the linear program. Enum of :class:`hips.constants.ProblemSense`
        """
        if lp_sense not in [ProblemSense.MAX, ProblemSense.MIN]:
            raise Exception("Illegal LP type")
        else:
            self.lp_sense = lp_sense
            # Set lp type in concrete solver
            self.concrete_solver.set_lp_sense(lp_sense)

    def __str__(self):
        return "Objective:\n" + str(self.objective) + "\nConstraints:\n" + "\n".join([str(c) for c in self.constraints])

    def variable_solution(self, var):
        """
        Returns the optimal value for the given variable. Note that this method does not check whether the LP has
        an optimal solution, it is recommended to use :meth:`get_status` before calling this method.

        :param var: Variable for which the solution should be returned. Needs to be an instance of
            :class:`hips.models.Variable`
        :return: Value in the optimal solution
        """
        return self.concrete_solver.variable_solution(var)

    def get_objective_value(self):
        """
        Returns the optimal objective value. Note that this method does not check whether the LP has
        an optimal solution, it is recommended to use :meth:`get_status` before calling this method.

        :return: Optimal objective value.
        """
        return self.concrete_solver.get_objective_value()

    def optimize(self):
        """Optimizes the linear program

        This method optimizes the linear program with the linear program solver specified in the constructor.
        """
        self.concrete_solver.optimize()

    def get_variables(self):
        """Returns the variables of the linear program

        :return: Variables of the linear program, given as list of :class:`hips.models.Variable`
        """
        return self.vars

    def get_status(self):
        """Returns the status of the linear program

        This method returns the status of the linear program. E.g. a linear program might be infeasible, unbounded or
        optimal.

        :return: Status of the linear program
        """
        return self.concrete_solver.get_status()

    def is_feasible(self, variable_solutions: dict):
        """Checks whether a given solution is feasible for the linear program

        :param variable_solutions: A :class:`dict` object that maps variables to their solution. The keys of this dictionary
            are instances of :class:`hips.models.Variable` and the keys are instances of :class:`hips.models.HIPSArray`
        :return: ``True`` if the solution is feasible, otherwise ``False``
        """
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
    """Representation a linear constraint

    This class implements a representation of a linear constraint of a linear program. Typically, a constraint is not
    created with the constructor but rather implicitly.
    """

    def __init__(self, lhs, comparator, rhs):
        """Constructor

        :param lhs: Left-hand side of the constraint. Has to be an instance of :class:`hips.models.LinExpr`
        :param comparator: A comparator, i.e. less equal, equal or greater equal (see :class:`hips.Comparator`)
        :param rhs: Right-hand side of the constraint. Has to be an instance of :class:`hips.models.LinExpr`
        """
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
                   + hash(np.sum(self.rhs.to_numpy().reshape(-1))) + self.comparator.value)

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
                if self.lhs.coefficients[var].to_numpy().shape != other.lhs.coefficients[var].to_numpy().shape:
                    return False
                if not np.allclose(self.lhs.coefficients[var].to_numpy(), other.lhs.coefficients[var].to_numpy(), rtol=1e-05, atol=1e-08):
                    return False
            # Compare rhs
            return np.allclose(self.rhs.to_numpy(), other.rhs.to_numpy(), rtol=1e-05, atol=1e-08)
        return False

    def eval(self, variable_solutions: dict, eps=0.0002):
        """Evaluate constraint

        This method evaluates whether constraint is satisfied under the given solution

        :param variable_solutions: ions: A :class:`dict` object that maps variables to their solution. The keys of this dictionary
            are instances of :class:`hips.models.Variable` and the keys are instances of :class:`hips.models.HIPSArray`
        :param eps: Absolute error tolerance. This is only relevant for inequality constraints
        :return: ``True`` if the constraint is satisfied, otherwise ``False``
        """
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
    """Representation of a linear expression

    This class implements a representation of a linear expression. Suppose we have variables :math:`x_0, \dots, x_n` and
    coefficients :math:`a_0, \dots, a_n` with dimensions :math:`d_0, \dots, d_n`. Then a linear expression of the form
    :math:`{a_0}^T x_0 + \dots + {a_n}^T x_n` can be represented with this class. For more details, please refer to
    :class:`hips.models.Variable`.

    Typically, a linear expression is not created explicitly with a constructor, but rather implicitly.
    """

    def __init__(self, vars=set(), coefficients=dict()):
        """Constructor

        :param vars: Variables in the linear expression. A set of instances of :class:`hips.models.Variable`
        :param coefficients: A :class:`dict` object that maps variables to coefficients. The keys have to be instances of
            :class:`hips.models.Variable` and values instances of :class:`hips.models.HIPSArray`
        """
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

    def __sub__(self, other):
        return self.__add__(-1 * other)

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
        """Evaluates the linear expression

        This method evaluates the linear expression with the given variable assignment

        :param variable_solutions: A :class:`dict` object that maps variables to their solution. The keys of this dictionary
            are instances of :class:`hips.models.Variable` and the keys are instances of :class:`hips.models.HIPSArray`
        :return: The value of this linear expression. Instance of :class:`hips.models.HIPSArray`
        """
        result = 0
        for var in self.vars:
            solution = variable_solutions[var]
            result += self.coefficients[var].to_numpy().dot(solution.to_numpy())
        return HIPSArray(result)


class Variable:
    """Representation of a variable

    This class implements a representation of a variable in the context of linear programming. A variable has an assigned
    name. A variable has a type, i.e. continuous, integer or binary (see :class:`hips.VarTypes`). Furthermore, a variable
    has a lower and upper bound, i.e. the minimum and maximum value a variable may attain. Lastly, each variable has a dimension.
    If a variable :math:`x` has dimension :math:`n`, then it can be thought of as a column vector containing :math:`1`-dimensional
    variables :math:`x_j` with :math:`j \in \{1, \dots, n\}`.

    Note that it is not recommended to explicitly construct a variable via the constructor. Instead use the method
    :py:meth:`hips.models.LPModel.add_variable` provided by :class:`hips.models.LPModel`.

    :Example:
        >>> from hips.models import LPModel
        >>> from hips.solver import GurobiSolver
        >>> model = LPModel(GurobiSolver())
        >>> # Creating variables x and y
        >>> x, y = model.add_variable("x", dim=10), model.add_variable("y")
    """

    def __init__(self, name, id=0, var_type=VarTypes.CONTINUOUS, lb=0, ub=None, dim=1):
        """Constructor

        :param name: Name of the variable
        :param id: Id of the variable. By default the ``id`` is 0
        :param var_type: Type of the variable, either continuous, integer or binary (see :class:`hips.VarTypes`)
        :param lb: Lower bound of the variable. Has to be of type :class:`hips.models.HIPSArray`
        :param ub: Upper bound of the variable. Has to be of type :class:`hips.models.HIPSArray`
        :param dim: Dimension of the variable. By default the dimension is :math:`1`
        """
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
                coefficients[self] = HIPSArray(np.identity(self.dim))
            else:
                coefficients[self] = HIPSArray(np.identity(self.dim))
                coefficients[other] = HIPSArray(np.identity(other.dim))
            return LinExpr(set([self, other]), coefficients)
        return NotImplemented

    def __sub__(self, other):
        return self.__add__(-1 * other)

    def __mul__(self, other):
        if isinstance(other, NUMERICAL_TYPES):
            return LinExpr(set([self]), {self: other * HIPSArray(np.identity(self.dim))})
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, NUMERICAL_TYPES):
            return LinExpr(set([self]), {self: other * HIPSArray(np.identity(self.dim))})
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
    """Wrapper class for numpy array

    This class acts as a wrapper for a numpy array. The wrapping is necessary for overriding the different Python operators.
    The underlying array can be accessed with the ``array`` attribute. For more details, please consult the
    `numpy documentation <https://numpy.org/doc/stable/contents.html>`_.


    :Example:
        >>> import numpy as np
        >>> from hips.models import HIPSArray
        >>> # Creating a 2x2 HIPSArray with ones
        >>> HIPSArray((2, 2))
        HIPSArray([[1. 1.]
         [1. 1.]])
        >>> # Creating a 3x3 identity matrix
        >>> HIPSArray(np.identity(3))
        HIPSArray([[1. 0. 0.]
         [0. 1. 0.]
         [0. 0. 1.]])
    """

    def __init__(self, arg):
        """
        Constructor

        :param arg: Either an array-like object or a :class:`tuple`. In the former case the created :class:`hips.models.HIPSArray`
            object's array will correspond the argument. In the latter case, the instance contains an array with ones with specified
            shape
        """
        if type(arg) in [list, np.ndarray]:
            array = arg
            self.array = np.array(array)
        elif type(arg) in [tuple]:
            self.array = np.ones(arg)
        if len(self.array.shape) > 2:
            raise ValueError("HIPSArray with illegal shape {}".format(self.array.shape))
        self.shape = self.array.shape

    def __getitem__(self, item):
        return self.array.__getitem__(item)

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
        """Returns the underlying numpy array

        :return: Underlying numpy array
        """
        return self.array

    def reshape(self, shape):
        """Reshapes the array

        :param shape: Shape given as tuple. For details, please consult the
            `numpy documentation <https://numpy.org/doc/stable/reference/generated/numpy.reshape.html>`_
        :return: An instance of :class:`hips.models.HIPSArray` with the specified shape and same data
        """
        return HIPSArray(self.array.reshape(shape))
