import warnings

try:
    from hips.solver._gurobi_solver import GurobiSolver
except ImportError:
    warnings.warn("Gurobi does not seem to be installed")

try:
    from hips.solver._clp_solver import ClpSolver
except ImportError:
    warnings.warn("CyLP does not seem to be installed")

try:
    from hips.solver._pulp_solver import PulpSolver
except ImportError:
    warnings.warn("Pulp does not seem to be installed")

from hips.solver._scipy_solver import ScipySolver

__all__ = ["GurobiSolver", "ClpSolver", "PulpSolver"]