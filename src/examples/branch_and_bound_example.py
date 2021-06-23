import os

from hips.constants import ProblemSense
from hips.loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver
from hips.solver.branch_and_bound import BranchAndBound
from hips.heuristics import FeasibilityPump

mip_model = MIPModel(GurobiSolver())
# Advanced
load_mps_advanced(mip_model, path=os.getcwd() + "/mps_files/pure-binary/acc-tight2.mps")
mip_model.set_mip_sense(ProblemSense.MIN)

import time

start = time.time()

incumbent_val = None
incumbent = None

fs = FeasibilityPump(mip_model, t=10)
fs.compute(1000)
sol = {var: fs.variable_solution(var) for var in mip_model.variables}
incumbent_val = fs.get_objective_value()
incumbent = sol
feasible = mip_model.is_feasible(sol)

bb = BranchAndBound(mip_model, incumbent_val=incumbent_val, incumbent=incumbent)
bb.optimize()

print(bb.incumbent_val)
print("Time:")
print(time.time() - start)