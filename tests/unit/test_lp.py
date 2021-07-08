import unittest

from parameterized import parameterized_class

from hips import GurobiSolver, ProblemSense, HIPSArray, ClpSolver, LPStatus, load_problem_gurobi
from hips.models import LPModel

import numpy as np


@parameterized_class("solver", [[solver] for solver in [GurobiSolver, ClpSolver]])
class LPModelTest(unittest.TestCase):

    def setUp(self) -> None:
        """
        Prepares the needed models
        """
        self.concrete_solver = self.solver()
        self.model = LPModel(self.concrete_solver)

    def test_simple_model(self):
        # Create variables
        x_1, x_2 = self.model.add_variable("x_1", lb=0), self.model.add_variable("x_2", lb=0)
        # Set sense
        self.model.set_lp_sense(ProblemSense.MAX)
        # Set objective
        self.model.set_objective(2 * x_1 + 4 * x_2)
        # Add constraints
        self.model.add_constraint(x_1 + 2 * x_2 <= 20)
        self.model.add_constraint(3 * x_1 - x_2 <= 10)
        # Optimize the program
        self.model.optimize()

        # Assert objective value
        self.assertAlmostEqual(self.model.get_objective_value(), 40)
        # Assert solution feasible
        self.assertTrue(self.model.is_feasible({var: self.model.variable_solution(var) for var in self.model.get_variables()}))

    def test_vector_model(self):
        # Create 2 dim. variable with lower bound 0
        x = self.model.add_variable("x", lb=0, dim=2)
        # Set sense
        self.model.set_lp_sense(ProblemSense.MAX)
        # Set objective
        self.model.set_objective(HIPSArray([2.0, 4.0]) * x)
        # Add constraint
        self.model.add_constraint(HIPSArray([[1.0, 2.0], [3.0, -1.0]]) * x <= HIPSArray([20.0, 10.0]))
        # Optimize
        self.model.optimize()

        # Assert objective value
        self.assertAlmostEqual(self.model.get_objective_value(), 40)
        # Assert solution feasible
        self.assertTrue(self.model.is_feasible({var: self.model.variable_solution(var) for var in self.model.get_variables()}))

    def test_add_and_remove_constraints(self):
        for idx, dim in enumerate([1, 100, 200]):
            # Add constr
            x = self.model.add_variable(f"x{dim}", dim=dim)
            constr = HIPSArray(np.identity(dim)) * x <= HIPSArray(np.ones(dim))
            self.model.add_constraint(constr)
            self.assertEqual(len(self.model.constraints), 1)
            # Remove constr
            self.model.remove_constraint(constraint=constr)
            self.assertEqual(len(self.model.constraints), 0)

    def test_unbounded_model(self):
        x = self.model.add_variable("x", dim=2)
        self.model.set_objective(HIPSArray([1, 1]) * x)
        self.model.set_lp_sense(ProblemSense.MAX)
        self.model.optimize()

        self.assertEqual(self.model.get_status(), LPStatus.UNBOUNDED)

    def test_infeasible_model(self):
        x = self.model.add_variable("x", dim=2)
        self.model.set_objective(HIPSArray([1, 1]) * x)
        self.model.set_lp_sense(ProblemSense.MAX)
        self.model.add_constraint(x <= -1)
        self.model.optimize()

        self.assertEqual(self.model.get_status(), LPStatus.INFEASIBLE)


if __name__ == '__main__':

    unittest.main()
