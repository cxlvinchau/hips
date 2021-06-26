import os

from hips.models import MIPModel

dir_path = os.path.dirname(os.path.realpath(__file__))
from hips.loader import load_mps

_solver_name = None
try:
    import gurobipy

    _solver_name = "GUROBI"
except:
    pass

if _solver_name is None:
    try:
        import cylp

        _solver_name = "CLP"
    except:
        pass


def _get_solver():
    if _solver_name == "GUROBI":
        from hips.solver import GurobiSolver
        return GurobiSolver()
    elif _solver_name == "CLP":
        from hips.solver import ClpSolver
        return ClpSolver()


def load_problem_clp(problem_name):
    from hips.solver import ClpSolver
    problem = MIPModel(ClpSolver())
    load_mps(problem, os.path.join(dir_path, "mps_files", f"{problem_name}.mps"))
    return problem


def load_problem_gurobi(problem_name):
    from hips.solver import GurobiSolver
    problem = MIPModel(GurobiSolver())
    load_mps(problem, os.path.join(dir_path, "mps_files", f"{problem_name}.mps"))
    return problem


def load_problem(problem_name):
    if _solver_name == "GUROBI":
        return load_problem_gurobi(problem_name)
    elif _solver_name == "CLP":
        return load_problem_clp(problem_name)