import unittest
from parameterized import parameterized_class

from hips import HIPSArray, VarTypes, ProblemSense, BoundDirection
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver
from hips.heuristics import HeuristicBounds


def build_model(mip_model):
    # Create variable
    x = mip_model.add_variable("x", VarTypes.INTEGER, lb=0, ub=2, dim=2)
    # Add constraints
    mip_model.add_constraint(HIPSArray([1, 2 / 3]) * x <= 2)
    mip_model.add_constraint(HIPSArray([1, 3]) * x <= 3)
    # Set objective function and problem sense
    mip_model.set_objective(HIPSArray([1, 1]) * x)
    mip_model.lp_model.set_lp_sense(ProblemSense.MAX)


@parameterized_class("solver", [[solver] for solver in [GurobiSolver, ClpSolver]])
class BoundsHeuristicTest(unittest.TestCase):

    def setUp(self) -> None:
        """
        Prepares the needed models

        :param solver: A solver, e.g. GurobiSolver()
        :return: None
        """
        self.concrete_solver = self.solver()

    def test_fixing_to_lower(self):
        mip_model = MIPModel(self.concrete_solver)
        build_model(mip_model)
        heur = HeuristicBounds(mip_model, BoundDirection.LOWER)
        heur.compute()

    def test_fixing_to_upper(self):
        mip_model = MIPModel(self.concrete_solver)
        build_model(mip_model)
        heur = HeuristicBounds(mip_model, BoundDirection.UPPER)
        heur.compute()

    def test_fixing_to_closest(self):
        mip_model = MIPModel(self.concrete_solver)
        build_model(mip_model)
        heur = HeuristicBounds(mip_model, BoundDirection.CLOSEST)
        heur.compute()


if __name__ == '__main__':
    unittest.main()
