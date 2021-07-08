import unittest
from parameterized import parameterized_class

from hips import HIPSArray, VarTypes, ProblemSense
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver
from hips.heuristics import FractionalDiving


def build_model(mip_model):
    # Create variables
    x = mip_model.add_variable("x", VarTypes.INTEGER, lb=0, ub=float("inf"), dim=2)
    # Add constraints
    mip_model.add_constraint(HIPSArray([-3, 2]) * x <= 2)
    mip_model.add_constraint(HIPSArray([2, 2]) * x <= 7)
    # Set objective and problem sense
    mip_model.set_objective(HIPSArray([1, 2]) * x)
    mip_model.set_mip_sense(ProblemSense.MAX)


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
        mip_model = MIPModel(self.concrete_solver)
        build_model(mip_model)

        heur = FractionalDiving(mip_model)
        heur.compute()

    def test_example_without_rounding(self):
        mip_model = MIPModel(self.concrete_solver)
        build_model(mip_model)

        heur = FractionalDiving(mip_model)
        heur._round_trivially = lambda: False
        heur.compute()


if __name__ == '__main__':
    unittest.main()
