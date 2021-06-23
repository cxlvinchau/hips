import os

from hips.constants import ProblemSense
from hips.loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver
from hips.heuristics import FeasibilityPump, TwoStageFeasibilityPump
import time

print("Start experiment")

feasible = []
times = []
for i in range(5):
    mip_model = MIPModel(GurobiSolver())
    # Advanced
    load_mps_advanced(mip_model, path=os.getcwd() + "/mps_files/10teams.mps")
    # print("Loaded model")
    mip_model.set_mip_sense(ProblemSense.MIN)
    start = time.time()

    fs = FeasibilityPump(mip_model, t=10)
    fs.compute(1000)

    end = time.time()
    # print(fs.cycle_its)
    # print([fs.cycle_its[i] - fs.cycle_its[i-1] for i in range(len(fs.cycle_its))])
    # print(fs.long_cycle_its)
    # print([fs.long_cycle_its[i] - fs.long_cycle_its[i-1] for i in range(len(fs.long_cycle_its))])

    # sol = {var: fs.variable_solution(var) for var in mip_model.lp_model.vars}
    # print(mip_model.is_feasible(sol))
    # print(f"time: {time.time() - start}")
    # fs.tracker.plot("feasibility objective")
    sol = {var: fs.variable_solution(var) for var in mip_model.lp_model.vars}
    feasible.append(mip_model.is_feasible(sol))

    times.append(end-start)
    print("Model {} solved.".format(i))

print(feasible)
print("Feasible solutions found: {}".format(sum(feasible)))

print(times)
print("Average time consumed: {}s".format(sum(times)/len(times)))

import numpy as np
feasible = np.array(feasible)
times = np.array(times)
feasible_times = times[feasible]
print("Average time consumed for feasible solutions: {}s".format(sum(feasible_times)/len(feasible_times)))