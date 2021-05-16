from hips.constants import LPSolver
from hips.solver._clp_solver import ClpSolver
from hips.solver._gurobi_solver import GurobiSolver
from hips.solver._abstract_solver import AbstractSolver
from hips.solver._scipy_solver import ScipySolver


def create_solver(lp_solver) -> AbstractSolver:
    if lp_solver == LPSolver.CLP:
        return ClpSolver()
    if lp_solver == LPSolver.GUROBI:
        return GurobiSolver()
    if lp_solver == LPSolver.SCIPY:
        return ScipySolver()
    return None
