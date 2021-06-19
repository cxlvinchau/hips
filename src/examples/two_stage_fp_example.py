from hips.loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver
from hips.heuristics import TwoStageFeasibilityPump, FeasibilityPump

model = MIPModel(GurobiSolver())
load_mps_advanced(model, path="mps_files/noswot.mps")
fp = TwoStageFeasibilityPump(model)
fp.compute(1000)
sol = {var: fp.variable_solution(var) for var in model.variables}
print(sol)
print(f"Feasible: {model.is_feasible(sol)}")
#fp.tracker.plot("feasibility objective")
#fp.tracker.plot("objective value")