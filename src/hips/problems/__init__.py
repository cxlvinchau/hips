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


TEN_TEAMS = None
"""
10 Teams example obtained from MIPLIB 2017 (https://miplib.zib.de/instance_details_10teams.html)
"""

if _solver_name is not None:
    # TEN TEAMS example (https://miplib.zib.de/instance_details_10teams.html)
    solver = _get_solver()
    TEN_TEAMS = MIPModel(solver)
    load_mps_advanced(TEN_TEAMS, os.path.join(dir_path, "mps_files", "10teams.mps"))
