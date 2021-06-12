import os

from hips.constants import LPSense
from hips.loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver
from hips.solver.branch_and_bound import BranchAndBound
from hips.heuristics import RENS

mip_model = MIPModel(GurobiSolver())
# Advanced
load_mps_advanced(mip_model, path=os.getcwd() + "/mps_files/flugpl.mps")
mip_model.set_mip_sense(LPSense.MIN)

import time

start = time.time()

bb = BranchAndBound(mip_model, incumbent_val=1201600)
bb.optimize()

print(bb.incumbent_val)
print("Time:")
print(time.time() - start)