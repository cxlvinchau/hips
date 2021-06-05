import os

from hips import HIPSArray
from hips.constants import VarTypes, LPSense
from hips.heuristics._line_search_diving import LineSearchDiving
from hips.loader import load_mps_advanced
from hips.models import LPModel, MIPModel
from hips.solver import GurobiSolver

mip_model = MIPModel(GurobiSolver())
# Advanced
load_mps_advanced(mip_model, path=os.getcwd() + "/mps_files/10teams.mps")
mip_model.set_mip_sense(lp_sense=LPSense.MIN)

heur = LineSearchDiving(mip_model)
heur.compute()
print([heur.variable_solution(var) for var in mip_model.binary_variables + mip_model.integer_variables])