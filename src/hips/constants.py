from enum import Enum
import numpy as np

NUMERICAL_TYPES = tuple([float, int, np.float, np.float64])


class Comparator(Enum):
    """
    Enum for less equals, equals and greater equals.
    """
    LESS_EQUALS = 0
    """Less equals (<=)"""
    EQUALS = 1
    """Equals (=)"""
    GREATER_EQUALS = 2
    """Greater equals (>=)"""


class VarTypes(Enum):
    """
    Enum for variable types, i.e. continuous, binary or integer.
    """
    CONTINUOUS = 1
    """Continuous"""
    BINARY = 2
    """Binary"""
    INTEGER = 3
    """Integer"""


class LPStatus(Enum):
    """
    Enum for status of linear program, i.e. unbounded, infeasible, optimal, unknown or error
    """
    UNBOUNDED = 0
    """Problem is unbounded"""
    INFEASIBLE = 1
    """Problem is infeasible"""
    OPTIMAL = 2
    """Problem has been solved and an optimal solution has been found"""
    UNKNOWN = 3
    """The status of the problem is unknown"""
    ERROR = 4
    """An error occurred"""


class ProblemSense(Enum):
    """
    Enum for sense of the problem, i.e. max or min
    """
    MAX = -1
    """Maximization"""
    MIN = 1
    "Minimization"


class VariableBound:
    """
    Enum for variable bound, i.e. lower bound or upper bound.
    """
    LB = 0
    """Lower bound"""
    UB = 1
    """Upper bound"""


class HeuristicStatus(Enum):
    """
    Enum for status of heuristic
    """
    SOL_FOUND = 0
    """Solution found"""
    NO_SOL_FOUND = 1
    """No solution found"""
    ERROR = 2
    """Error"""
