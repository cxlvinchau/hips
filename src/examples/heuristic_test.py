import os

from hips.constants import LPSense
from hips.heuristics import FractionalDivingHeuristic, LineSearchDiving, RENS, FeasibilityPump
from hips.loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver

mip_model = MIPModel(GurobiSolver())
# Advanced
load_mps_advanced(mip_model, path=os.getcwd() + "/mps_files/data.mps")
mip_model.set_mip_sense(LPSense.MIN)

heuristic = RENS(mip_model)
heuristic.compute(max_iter=200)

print(heuristic.get_objective_value())
print(f"Feasible: {mip_model.is_feasible({var: heuristic.variable_solution(var) for var in mip_model.lp_model.vars})}")