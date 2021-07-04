import warnings

try:
    from hips.solver._gurobi_solver import GurobiSolver
except ImportError:
    warnings.warn("Gurobi does not seem to be installed")

try:
    from hips.solver._clp_solver import ClpSolver
except ImportError:
    warnings.warn("CyLP does not seem to be installed")

__all__ = ["GurobiSolver", "ClpSolver"]

from hips.solver.branch_and_bound import BranchAndBound