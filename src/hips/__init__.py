from hips.models import HIPSArray
from hips.constants import ProblemSense, Comparator, VarTypes, VariableBound, NUMERICAL_TYPES, LPStatus, HeuristicStatus
from hips.problems import load_problem, load_problem_gurobi, load_problem_clp

CLP_AVAILABLE = False
GUROBI_AVAILABLE = False
try:
    from hips.solver import ClpSolver

    CLP_AVAILABLE = True
except:
    pass

try:
    from hips.solver import GurobiSolver

    GUROBI_AVAILABLE = True
except:
    pass
