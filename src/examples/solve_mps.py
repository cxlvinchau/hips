import os
import numpy as np

from hips.constants import LPSense
from hips.loader.mps_loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver


# HIPS
import time
from hips.loader.old_loader import load_mps
start = time.time()
mip_model = MIPModel(ClpSolver())
# Advanced
load_mps_advanced(mip_model, rel_path=os.getcwd() + "/mps_files/10teams.mps")
mip_model.set_mip_sense(lp_sense=LPSense.MIN)
hash_val = []
for constr in mip_model.lp_model.constraints:
    hash_val.append(hash(constr))
print(f"Number of binary variables: {len(mip_model.binary_variables)}")
print(f"Number of constraints: {len(mip_model.lp_model.constraints)}")
from hips.heuristics._heur_feasibility_pump import FeasibilityPump
fs = FeasibilityPump(mip_model, seed=None)
fs.compute(10, t=20)
print("Feasibility pump obj value: {}".format(fs.get_objective_value()))

end = time.time()
print("{} seconds".format(end-start))

binary_variables = mip_model.binary_variables
print(f"Unique values: {np.unique([fs.variable_solution(x).to_numpy() for x in binary_variables])}")
print(binary_variables[0].dim)
sol = {x: fs.variable_solution(x) for x in mip_model.lp_model.vars}
print("Solution feasiblez: {}".format(mip_model.is_feasible(sol)))
fs.tracker.plot("feasibility objective")
fs.tracker.plot("objective value")