import os

from hips import HIPSArray
from hips.constants import VarTypes, ProblemSense
from hips.heuristics._line_search_diving import LineSearchDiving
from hips.heuristics._rens import RENS
from hips.loader import load_mps_advanced
from hips.models import LPModel, MIPModel
from hips.solver import GurobiSolver
import numpy as np

#mip_model = MIPModel(GurobiSolver())
# Advanced
#load_mps_advanced(mip_model, path=os.getcwd() + "/mps_files/flugpl.mps")
#mip_model.set_mip_sense(lp_sense=LPSense.MIN)


mip_model = MIPModel(GurobiSolver())
x = mip_model.add_variable("x", VarTypes.INTEGER, lb=0, ub=float("inf"), dim=2)
constr1 = HIPSArray([-3,2])*x <= 2
constr2 = HIPSArray([2,2])*x <= 7
mip_model.add_constraint(constr1)
mip_model.add_constraint(constr2)
obj_func = HIPSArray([1,2])*x
mip_model.set_objective(obj_func)
mip_model.set_mip_sense(ProblemSense.MAX)

heur = RENS(mip_model)
heur.compute(100)
print(heur.mip_solver.incumbent)