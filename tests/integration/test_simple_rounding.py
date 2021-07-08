import unittest
from parameterized import parameterized_class

from hips.heuristics import SimpleRounding
from hips.heuristics._feasibility_pump import FeasibilityPump
from hips.constants import VarTypes
from hips.solver import GurobiSolver, ClpSolver
from hips.models._lp_model import LPModel
from hips.models._mip_model import MIPModel
from hips.constants import ProblemSense
import numpy as np
from hips.models import HIPSArray


@parameterized_class("solver", [[solver] for solver in [GurobiSolver, ClpSolver]])
class SimpleRoundingTest(unittest.TestCase):

    def setUp(self) -> None:
        """
        Prepares the needed models

        :param solver: A solver, e.g. GurobiSolver()
        :return: None
        """
        self.concrete_solver = self.solver()

    def test_example_1(self):
        # Create model with GurobiSolver
        mip_model = MIPModel(self.concrete_solver)
        # Create variable
        x = mip_model.add_variable("x", VarTypes.INTEGER, lb=0, ub=float("inf"), dim=2)
        # Add constraints
        mip_model.add_constraint(HIPSArray([1, 2 / 3]) * x <= 2)
        mip_model.add_constraint(HIPSArray([1, 1.5]) * x <= 3)
        # Specify objective and set problem sense
        mip_model.set_objective(HIPSArray([1, 1]) * x)
        mip_model.lp_model.set_lp_sense(ProblemSense.MAX)

        # Run the heuristic and output the solution
        heur = SimpleRounding(mip_model)
        heur.compute()


if __name__ == '__main__':
    unittest.main()
