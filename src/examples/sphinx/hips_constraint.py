from hips.models import LPModel, HIPSArray
from hips.solver import ClpSolver

model = LPModel(ClpSolver())
x, y = model.add_variable("x", dim=2), model.add_variable("y", dim=3)
A = HIPSArray([[1, 1], [2, 0]])
B = HIPSArray([[1, 2, 3], [1, 0, 1]])
b = HIPSArray([10, 20])
constr = A * x + B * y >= b

import numpy as np

a = HIPSArray(np.identity(4))
print(a)
a = HIPSArray(np.zeros((2, 3)))
print(a)
a = HIPSArray(np.array([1, 2, 3]))
print(a)
