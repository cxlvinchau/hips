import os
import numpy as np

from hips.constants import ProblemSense
from hips.loader.mps_loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver


# HIPS
import time
from hips.loader.old_loader import load_mps
start = time.time()
mip_model = MIPModel(GurobiSolver())
# Advanced
load_mps_advanced(mip_model, path=os.getcwd() + "/mps_files/ej.mps")
mip_model.set_mip_sense(lp_sense=ProblemSense.MIN)
print(f"Number of binary variables: {len(mip_model.binary_variables)}")
print(f"Number of constraints: {len(mip_model.lp_model.constraints)}")
from hips.heuristics._feasibility_pump import FeasibilityPump
fs = FeasibilityPump(mip_model, seed=None)
fs.compute(1000, t=20)
print("Feasibility pump obj value: {}".format(fs.get_objective_value()))

end = time.time()
print("{} seconds".format(end-start))

sol = {x: fs.variable_solution(x) for x in mip_model.lp_model.vars}
print("Solution feasible: {}".format(mip_model.is_feasible(sol)))
fs.tracker.plot("objective value")
fs.tracker.plot("feasibility objective")