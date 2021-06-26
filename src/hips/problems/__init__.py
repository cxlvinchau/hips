import os

from hips.models import MIPModel

dir_path = os.path.dirname(os.path.realpath(__file__))
from hips.loader import load_mps_advanced

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


problem_list = []

TEN_TEAMS = None
FLUGPL = None
GR4X6 = None

if _solver_name is not None:
    # TODO Add new problems here

    # TEN TEAMS problem (https://miplib.zib.de/instance_details_10teams.html)
    solver = _get_solver()
    TEN_TEAMS = MIPModel(solver)
    load_mps_advanced(TEN_TEAMS, os.path.join(dir_path, "mps_files", "10teams.mps"))
    problem_list.append(TEN_TEAMS)

    # FLUGPL problem (http://miplib2017.zib.de/instance_details_flugpl.html)
    solver = _get_solver()
    FLUGPL = MIPModel(solver)
    load_mps_advanced(FLUGPL, os.path.join(dir_path, "mps_files", "flugpl.mps"))
    problem_list.append(FLUGPL)

    # gr4x6 problem (https://miplib.zib.de/instance_details_gr4x6.html)
    solver = _get_solver()
    GR4X6 = MIPModel(solver)
    load_mps_advanced(GR4X6, os.path.join(dir_path, "mps_files", "gr4x6.mps"))
    problem_list.append(GR4X6)


def load_problem_clp(problem_name):
    from hips.solver import ClpSolver
    problem = MIPModel(ClpSolver())
    load_mps_advanced(problem, os.path.join(dir_path, "mps_files", f"{problem_name}.mps"))
    return problem


def load_problem_clp(problem_name):
    from hips.solver import GurobiSolver
    problem = MIPModel(GurobiSolver())
    load_mps_advanced(problem, os.path.join(dir_path, "mps_files", f"{problem_name}.mps"))
    return problem
