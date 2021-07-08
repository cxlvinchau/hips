import unittest

from hips.constants import ProblemSense, VarTypes, VariableBound
from hips.models import MIPModel
from hips.solver._clp_solver import ClpSolver
from hips.models._lp_model import Variable


class ClpSolverTest(unittest.TestCase):

    def setUp(self):
        self.solver = ClpSolver()
        self.mip_model = MIPModel(self.solver)

    def test_add_variable(self):
        return
        variables = [Variable("x{}".format(i), id=i) for i in range(1000)]
        for var in variables:
            self.solver.add_variable(var)
        self.assertEqual(len(self.solver.model.variables), 1000, "Variables not added correctly")
        for var in variables:
            self.assertIn(var.id, self.solver.var_to_clp_var, "Variable not contained in dict")

    def test_remove_variable(self):
        return
        variables = [Variable("x{}".format(i), id=i) for i in range(1000)]
        for var in variables:
            self.solver.add_variable(var)
        for var in variables[:500]:
            self.solver.remove_variable(var)
        self.assertEqual(len(self.solver.var_to_clp_var), 500, "Variables not removed correctly")
        for var in variables[:500]:
            self.assertNotIn(var.id, self.solver.var_to_clp_var, "Variable not removed from dict")

    def test_optimize(self):
        x = Variable("x", id=0)
        y = Variable("y", id=1)
        self.solver.add_variable(x)
        self.solver.add_variable(y)
        self.solver.add_constraint(x + y <= 10)
        self.solver.set_lp_sense(ProblemSense.MAX)
        self.solver.set_objective(1 * x + y)
        self.solver.optimize()
        print(self.solver.get_objective_value())

    def test_remove_variable_and_constraint(self):
        return
        variables = [Variable("x_{}".format(i), id=i) for i in range(100)]
        for var in variables:
            self.solver.add_variable(var)
        self.solver.add_constraint(sum([1*var for var in variables[10:40]]) <= 10, name="constr1")
        self.solver.remove_constraint(name="constr1")
        for var in variables[10:40]:
            self.solver.remove_variable(var)

    def test_disc_opt_exercise2_4_a(self):
        x1 = self.mip_model.add_variable("x1", var_type=VarTypes.INTEGER, lb=0, ub=8)
        x2 = self.mip_model.add_variable("x2", var_type=VarTypes.INTEGER, lb=0, ub=8)
        self.mip_model.add_constraint(2 * x1 + x2 <= 8)
        self.mip_model.add_constraint(-2 * x1 + 10 * x2 <= 25)
        self.mip_model.set_objective(x1 + x2)
        self.mip_model.set_mip_sense(ProblemSense.MAX)
        self.mip_model.lp_model.optimize()
        print(self.mip_model.lp_model.get_objective_value())

    def test_set_variable_bounds(self):
        x = self.mip_model.add_variable("x", lb=0, ub=10, dim=2)
        self.solver.set_variable_bound(x, VariableBound.UB, 5)
        self.solver.set_variable_bound(x, VariableBound.LB, 4)
        self.mip_model.set_objective(x)
        self.solver.optimize()
        print(self.mip_model.lp_model.get_objective_value())

if __name__ == '__main__':
    unittest.main()
