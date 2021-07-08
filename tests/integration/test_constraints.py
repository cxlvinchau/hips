import unittest

from parameterized import parameterized_class

from hips import GurobiSolver, ClpSolver
from hips.models import LPModel, HIPSArray
from hips.solver import ClpSolver


@parameterized_class("solver", [[solver] for solver in [GurobiSolver, ClpSolver]])
class ConstraintTest(unittest.TestCase):

    def setUp(self) -> None:
        self.concrete_solver = self.solver()

    def test_valid_constraint(self):
        model = LPModel(self.concrete_solver)
        x, y = model.add_variable("x", dim=2), model.add_variable("y", dim=3)
        A = HIPSArray([[1, 1], [2, 0]])
        B = HIPSArray([[1, 2, 3], [1, 0, 1]])
        b = HIPSArray([10, 20])
        constr = A * x + B * y >= b

    def test_invalid_constraint(self):
        try:
            model = LPModel(self.concrete_solver)
            x, y = model.add_variable("x", dim=2), model.add_variable("y", dim=3)
            A = HIPSArray([[1, 1], [2, 0]])
            B = HIPSArray([[1, 2, 3], [1, 0, 1], [1, 0, 3]])
            b = HIPSArray([10, 20])
            constr = A * x + B * y >= b
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)



if __name__ == '__main__':
    unittest.main()
