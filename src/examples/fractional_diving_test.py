import os

from hips import HIPSArray
from hips.constants import ProblemSense, VarTypes
from hips.heuristics import FractionalDivingHeuristic
from hips.loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver

mip_model = MIPModel(GurobiSolver())
x = mip_model.add_variable("x", VarTypes.INTEGER, lb=0, ub=float("inf"), dim=2)
constr1 = HIPSArray([-3,2])*x <= 2
constr2 = HIPSArray([2,2])*x <= 7
mip_model.add_constraint(constr1)
mip_model.add_constraint(constr2)
obj_func = HIPSArray([1,2])*x
mip_model.set_objective(obj_func)
# mip_model = MIPModel(GurobiSolver())
# load_mps_advanced(mip_model, path=os.getcwd() + "/mps_files/flugpl.mps")
# mip_model.set_mip_sense(LPSense.MIN)
# for var in mip_model.lp_model.vars:
#     print(str(var.ub.to_numpy()) + " " + str(var.lb.to_numpy()))
# print("----")
heur = FractionalDivingHeuristic(mip_model)
heur.compute()
# for var in mip_model.lp_model.vars:
#     print(str(var.ub.to_numpy()) + " " + str(var.lb.to_numpy()))
heur.tracker.plot("objective value")
