from enum import Enum
import numpy as np

NUMERICAL_TYPES = tuple([float, int, np.float, np.float64])


class Comparator(Enum):
    LESS_EQUALS = 0
    EQUALS = 1
    GREATER_EQUALS = 2


class VarTypes(Enum):
    CONTINUOUS = 1
    BINARY = 2
    INTEGER = 3


class LPSolver(Enum):
    GUROBI = 1
    SCIPY = 2
    COINOR = CYLP = CLP = 3


class LPStatus(Enum):
    UNBOUNDED = 0
    INFEASIBLE = 1
    OPTIMAL = 2
    UNKNOWN = 3
    ERROR = 4


class LPSense(Enum):
    MAX = -1
    MIN = 1


class VariableBound:
    LB = 0
    UB = 1
