import unittest
from parameterized import parameterized_class

from hips import HIPSArray, VarTypes, ProblemSense, load_problem_clp
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver, BranchAndBound
from hips.heuristics import FractionalDiving

@parameterized_class("solver", [[solver] for solver in [GurobiSolver, ClpSolver]])
class FractionalDivingTest(unittest.TestCase):

    def setUp(self) -> None:
        """
        Prepares the needed models

        :param solver: A solver, e.g. GurobiSolver()
        :return: None
        """
        self.concrete_solver = self.solver()

    def test_example(self):
        # Create MIP model
        model = MIPModel(self.concrete_solver)
        # Create variables with lower bound 0
        x_1 = model.add_variable("x_1", lb=0, ub=20, var_type=VarTypes.INTEGER)
        x_2 = model.add_variable("x_2", lb=0)
        # Set sense
        model.set_mip_sense(ProblemSense.MAX)
        # Set objective
        model.set_objective(2 * x_1 + 4 * x_2)
        # Add constraints
        model.add_constraint(x_1 + 2 * x_2 <= 20)
        model.add_constraint(3 * x_1 - x_2 <= 10)

        bb = BranchAndBound(model)
        bb.optimize()
        # Print solution
        bb.get_incumbent()
        # Print objective value
        bb.get_incumbent_val()

        self.assertAlmostEqual(bb.get_incumbent_val(), 40)
        self.assertTrue(model.is_feasible(bb.get_incumbent()))

    def test_gr4x6(self):
        model = load_problem_clp("gr4x6")
        model.set_mip_sense(mip_sense=ProblemSense.MIN)
        bb = BranchAndBound(model)
        bb.optimize()
        # Print solution
        sol = bb.get_incumbent()
        # Print objective value
        obj_val = bb.get_incumbent_val()

        self.assertAlmostEqual(obj_val, 202.349999999998)
        self.assertTrue(model.is_feasible(sol))



if __name__ == '__main__':
    unittest.main()
