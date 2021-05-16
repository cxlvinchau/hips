import unittest

import gurobipy as gb
from gurobipy import GRB

from hips.solver._gurobi_solver import GurobiSolver
from hips.models._lp_model import Variable


def create_gurobi_model_standard_problem() -> gb.Model:
    """Creates a gurobi model for the standard problem. Only use gurobipy methods to ensure independence of our program code."""
    model = gb.Model()
    x, y, z = model.addVar(vtype=GRB.CONTINUOUS, name="x"), model.addVar(vtype=GRB.CONTINUOUS, name="y"), model.addVar(vtype=GRB.CONTINUOUS, name="z")
    constraint1 = x + y + z <= 10
    constraint2 = x + y + z <= 20
    constraint3 = 1 * x <= 5
    model.addConstr(constraint1, "constr1")
    model.addConstr(constraint2, "constr2")
    model.addConstr(constraint3, "constr3")
    model.addConstr(1 * x >= 0)
    model.addConstr(1 * y >= 0)
    model.addConstr(1 * z >= 0)
    model.setObjective(10 * x + y + z)
    return model

class GurobiSolverTest(unittest.TestCase):

    def test_add_remove_variable(self):
        gurobi_solver = GurobiSolver()
        gurobi_solver.model = create_gurobi_model_standard_problem()
        test_var = Variable("t", id=10)
        """Test adding a variable and immediately removing it"""
        gurobi_solver.add_variable(test_var)
        self.assertNotEqual(gurobi_solver.model.getVarByName("var"+str(test_var.id)+"[0]"), None, "The variable could not be added to the model.")
        gurobi_solver.remove_variable(test_var)
        self.assertEqual(gurobi_solver.model.getVarByName("var"+str(test_var.id)+"[0]"), None, "The variable could not be removed from the model.")
        gurobi_solver.model = create_gurobi_model_standard_problem()

    def test_add_remove_constraint(self):
        gurobi_solver = GurobiSolver()
        gurobi_solver.model = create_gurobi_model_standard_problem()
        test_x, test_y = Variable("test_x", id=10), Variable("test_y", id=20)
        gurobi_solver.add_variable(test_x)
        gurobi_solver.add_variable(test_y)
        test_constraint = test_x + test_y <= 100
        test_name = "test_constraint"
        """Test adding the constraint"""
        gurobi_solver.add_constraint(constraint=test_constraint, name=test_name)
        self.assertNotEqual(gurobi_solver.model.getConstrByName(test_name), None, "The constraint was not added to the gurobi model")
        """Test removing the constraint"""
        gurobi_solver.remove_constraint(name=test_name)

    if __name__ == '__main__':
        test_add_remove_variable()
        test_add_remove_constraint()





