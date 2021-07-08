import unittest

from hips.models import LPModel
from hips.models import Variable
from hips.solver import GurobiSolver


class LPTest(unittest.TestCase):

    def test_add_remove_variable(self):
        model = LPModel(GurobiSolver())
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

    def test_add_remove_constraint(self):
        model = LPModel(GurobiSolver())
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


if __name__ == '__main__':
    unittest.main()
