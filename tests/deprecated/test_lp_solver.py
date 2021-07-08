import unittest

from hips.constants import LPStatus
from hips.models._lp_model import LPModel
from hips.models._lp_model import Variable
from hips.solver._clp_solver import ClpSolver
from hips.solver._gurobi_solver import GurobiSolver


def fill_model_standard_problem(model):
    x, y, z = model.add_variable("x"), model.add_variable("y"), model.add_variable("z")
    constraint = x + y + z <= 10
    constraint2 = x + y + z <= 20
    constraint3 = 1 * x <= 5
    model.add_constraint(constraint)
    model.add_constraint(constraint2)
    model.add_constraint(constraint3)
    model.add_constraint(1 * x >= 0)
    model.add_constraint(1 * y >= 0)
    model.add_constraint(1 * z >= 0)
    model.set_objective(10 * x + y + z)
    return [x, y, z]

def fill_model_infeasible_problem(model):
    x = model.add_variable("x")
    y = model.add_variable("y")
    model.add_constraint(1*x >= 2)
    model.add_constraint(1*x <= 1)
    model.add_constraint(1*y <= 10)
    model.set_objective(10.0*x + y)
    return x


class LPTest(unittest.TestCase):

    def test_t(self):
        import os
        print(os.getcwd())

    def test_add_remove_variable(self ): #model: LPModel
        solver = GurobiSolver()
        model = LPModel(solver)
        test_var_name = "test_var_name"
        test_dims = [1, 7, 10]
        for test_dim in test_dims:
            """TEST1: Add a single variable with name"""
            test_var = model.add_variable(test_var_name, dim=test_dim)
            self.assertTrue(test_var in model.vars, "TEST1 failed: The variable was not added to the model.")
            self.assertTrue(test_var.name == test_var_name,
                            "TEST1 failed: The variable does not have the expected variable name.")
            """TEST2: Remove that variable"""
            model.remove_variable(test_var)
            self.assertTrue(test_var not in model.vars, "TEST2 failed: The variable was not remove from the model.")
            """TEST3: Add two variables with the same name"""
            vars_size = len(model.vars)
            test_var = model.add_variable(test_var_name, dim=test_dim)
            self.assertEqual(len(model.vars), vars_size+1, "TEST3 failed: The variable was not added to the model even once.")
            try:
                model.add_variable(test_var_name, dim=test_dim)
                self.fail("TEST3 failed: No exception was thrown, when adding a variable with duplicate name.")
            except:
                self.assertEqual(len(model.vars), vars_size+1,
                                 "TEST3 failed: The variable was added to the model more than once.")
            model.remove_variable(test_var)
            """TEST4: Remove non-existing variable"""
            test_var = Variable(name=test_var_name, id=42069)
            vars_size = len(model.vars)
            try:
                model.remove_variable(test_var)
                self.fail("TEST4 failed: No exception was thrown, when removing a non-existing variable.")
            except:
                self.assertEqual(len(model.vars), vars_size, "TEST4 failed: The number of variables decreased," +
                                                            " even though no variable should have been removed.")

    def test_add_remove_constraint(self): #, model: LPModel
        solver = GurobiSolver()
        model = LPModel(solver)
        test_dims = [1, 7, 10]
        for test_dim in test_dims:
            test_constraint_name = "test_constraint_name"
            test_var= model.add_variable("test_var_x", dim=test_dim)
            test_constraint = test_var <= 42069
            """TEST1: Add a constraint with name"""
            model.add_constraint(test_constraint, name=test_constraint_name)
            self.assertTrue(test_constraint in model.constraints,
                            "TEST1 failed: The constraint was not added to the model.")
            """TEST2: Remove that constraint by constraint"""
            model.remove_constraint(constraint=test_constraint)
            self.assertTrue(test_constraint not in model.constraints,
                            "TEST2 failed: The constraint was not removed from the model.")
            """TEST3: Remove that constraint by name"""
            model.add_constraint(test_constraint, name=test_constraint_name)
            self.assertTrue(test_constraint in model.constraints,
                            """TEST3 failed: The constraint was not added to the model.""")
            model.remove_constraint(name=test_constraint_name)
            self.assertTrue(test_constraint not in model.constraints,
                            "TEST3 failed: The constraint was not removed from the model.")
            """TEST4: Add and remove constraint without name"""
            model.add_constraint(test_constraint)
            self.assertTrue(test_constraint in model.constraints,
                            "TEST4 failed: The constraint was not added to the model.")
            model.remove_constraint(constraint=test_constraint)
            self.assertTrue(test_constraint not in model.constraints,
                            "TEST4 failed: The constraint was not removed from the model.")
            """TEST5: Add two constraints with the same name"""
            constraints_size = len(model.constraints)
            model.add_constraint(test_constraint, name=test_constraint_name)
            self.assertTrue(test_constraint in model.constraints,
                            "TEST5 failed: The constraint was not added to the model even once.")
            self.assertEqual(len(model.constraints), constraints_size+1, "TEST5: The model contains too few variables")
            try:
                model.add_constraint(test_constraint, name=test_constraint_name)
                self.fail("TEST5 failed: No exception was thrown, when adding a constraint with duplicate name to the model")
            except:
                self.assertEqual(len(model.constraints), constraints_size + 1,
                                 "TEST5: The model does not contain the correct amount of constraint")
            model.remove_constraint(constraint=test_constraint)
            """TEST6: Remove non-existing constraint"""
            self.assertTrue(test_constraint not in model.constraints,
                            "TEST6 failed: The constraint was existing in the model beforehand.")
            try:
                model.remove_constraint(constraint=test_constraint, name=test_constraint_name)
                self.fail("TEST6 failed: No exception was thrown, when removing a non-existing constraint from the model")
            except:
                self.assertTrue(test_constraint not in model.constraints,
                                "TEST6 failed: The constraint exists in the model after removing it")
            """TEST7: Add a constraint with non-existing variables"""
            test_var2 = Variable(name="test_var_name", id=42069, dim=test_dim)
            test_constraint = test_var2 <= 42069
            try:
                model.add_constraint(test_constraint)
                self.fail("TEST7 failed: No exception was thrown, when adding a constraint with a non existing variable")
            except:
                self.assertTrue(test_constraint not in model.constraints,
                                "TEST7 failed: The constraint was added to the model," +
                                " even though it contains a non-existing variable")
            """TEST CLEANUP"""
            model.remove_variable(test_var)

    def test_set_objective(self, model: LPModel):
        pass

    def test_clp_scipy(self):

        solver = ClpSolver()
        model = LPModel(solver)
        fill_model_standard_problem(model)
        model.optimize()
        res2 = model.get_objective_value()

        message = "Scipy LP solution differs from CoinOr LP solution"
        self.assertAlmostEqual(res1, res2, None, message, 0.001)

    def test_infeasible(self):

        solver = ClpSolver()
        model = LPModel(solver)
        fill_model_infeasible_problem(model)
        model.optimize()
        status = model.get_status()
        self.assertEqual(status, LPStatus.INFEASIBLE, "Clp model returned unexpected status")

        solver = GurobiSolver()
        model = LPModel(solver)
        fill_model_infeasible_problem(model)
        model.optimize()
        status = model.get_status()
        self.assertEqual(status, LPStatus.INFEASIBLE, "Gurobi model returned unexpected status")


if __name__ == '__main__':
    concrete_solvers = [GurobiSolver(), ClpSolver()]
    for concrete_solver in concrete_solvers:
        test_model = LPModel(concrete_solver)
        LPTest.test_add_remove_variable(test_model)
        LPTest.test_add_remove_constraint(test_model)
        LPTest.test_set_objective(test_model)
    unittest.main()
