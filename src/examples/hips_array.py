from hips.models import LPModel, HIPSArray
from hips.solver import ClpSolver
import numpy as np

solver = ClpSolver()
model = LPModel(solver)
x, y = model.add_variable("x", dim=2), model.add_variable("y", dim=3)
constr = HIPSArray(np.identity(2)) * x + HIPSArray([[1,2,3], [2,0,4]]) * y <= 2
print("Constraint")
print(constr)
model.add_constraint(constr)
obj = x + y
model.set_objective(obj)
model.optimize()
print("Solution")
print(model.variable_solution(x))
print(model.variable_solution(y))