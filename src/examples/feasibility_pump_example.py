import os

from hips.constants import LPSense
from hips.loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver
from hips.heuristics import FeasibilityPump
import time

print("Start experiment")

mip_model = MIPModel(GurobiSolver())
# Advanced
load_mps_advanced(mip_model, path=os.getcwd() + "/mps_files/10teams.mps")
print("Loaded model")
mip_model.set_mip_sense(LPSense.MIN)

start = time.time()
fs = FeasibilityPump(mip_model)
fs.compute(1000, t=10)

sol = {var: fs.variable_solution(var) for var in mip_model.lp_model.vars}
print(mip_model.is_feasible(sol))
print(f"time: {time.time() - start}")
fs.tracker.plot("feasibility objective")