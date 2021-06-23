from hips import ProblemSense, HIPSArray
from hips.solver import GurobiSolver, ClpSolver
from hips.models import LPModel

# Create solver
solver = ClpSolver()
# Create LP model
model = LPModel(solver)
# Create variables with lower bound 0
x_1, x_2 = model.add_variable("x_1", lb=0), model.add_variable("x_2", lb=0)
# Set sense
model.set_lp_sense(ProblemSense.MAX)
# Set objective
model.set_objective(2*x_1 + 4*x_2)
# Add constraints
model.add_constraint(x_1 + 2*x_2 <= 20)
model.add_constraint(3*x_1 - x_2 <= 10)
model.optimize()
print(f"Objective value: {model.get_objective_value()}")
print(f"x_1: {model.variable_solution(x_1)}")
print(f"x_2: {model.variable_solution(x_2)}")

# Create solver
solver = ClpSolver()
# Create LP model
model = LPModel(solver)
# Create 2 dim. variable with lower bound 0
x = model.add_variable("x", lb=0, dim=2)
# Set sense
model.set_lp_sense(ProblemSense.MAX)
# Set objective
model.set_objective(HIPSArray([2, 4]) * x)
# Add constraints
model.add_constraint(HIPSArray([[1, 2], [3, -1]]) * x <= HIPSArray([20.0, 10.0]))

model.optimize()
print(f"Objective value: {model.get_objective_value()}")
print(f"x: {model.variable_solution(x)}")