from gurobipy import GRB

from hips import HIPSArray
from hips.constants import VarTypes, LPSense
from hips.heuristics import FractionalDivingHeuristic
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
mip_model.set_mip_sense(LPSense.MAX)

heur = FractionalDivingHeuristic(mip_model)
heur.compute()
heur.tracker.plot("objective value")
