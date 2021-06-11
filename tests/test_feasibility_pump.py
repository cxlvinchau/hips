import unittest
from parameterized import parameterized_class

from hips.heuristics._feasibility_pump import FeasibilityPump
from hips.constants import VarTypes
from hips.solver import GurobiSolver, ClpSolver
from hips.models._lp_model import LPModel
from hips.models._mip_model import MIPModel
from hips.constants import LPSense
import numpy as np
from hips.models import HIPSArray


@parameterized_class("solver", [[solver] for solver in [GurobiSolver, ClpSolver]])
class FeasibilityPumpTest(unittest.TestCase):

    def setUp(self) -> None:
        """
        Prepares the needed models

        :param solver: A solver, e.g. GurobiSolver()
        :return: None
        """
        self.mip_model = MIPModel(self.solver(), binary_variables=[], integer_variables=[])
        self.fs = FeasibilityPump(self.mip_model)

    def test_trivial_example(self):
        # TODO Not exactly a unit test, but ok for now
        # Set up model
        x = self.mip_model.add_variable("x", var_type=VarTypes.INTEGER, lb=4, ub=10)
        y = self.mip_model.add_variable("y", var_type=VarTypes.BINARY)
        self.mip_model.set_objective(2 * x + y)
        self.mip_model.set_mip_sense(LPSense.MAX)
        # Run feasibility pump
        self.fs.compute(max_iter=10)
        # Assert
        #self.assertAlmostEqual(self.mip_model.lp_model.variable_solution(x), 10)
        #self.assertAlmostEqual(self.mip_model.lp_model.variable_solution(y), 8)

    def test_vector_example(self):
        x = self.mip_model.add_variable("x", var_type=VarTypes.BINARY, lb=4, ub=10, dim=50)
        y = self.mip_model.add_variable("y", var_type=VarTypes.BINARY, dim=60)
        self.mip_model.add_constraint(HIPSArray(np.identity(50)) * x + HIPSArray((50, 60)) * y <= 10)
        self.mip_model.set_objective(x + y)
        self.mip_model.set_mip_sense(LPSense.MIN)
        # Run feasibility pump
        self.fs.compute(max_iter=10)
        print(self.fs.get_objective_value())

    def test_disc_opt_exercise2_4_a(self):
        x1 = self.mip_model.add_variable("x1", var_type=VarTypes.INTEGER, lb=0, ub=8)
        x2 = self.mip_model.add_variable("x2", var_type=VarTypes.INTEGER, lb=0, ub=8)
        self.mip_model.add_constraint(2 * x1 + x2 <= 8)
        self.mip_model.add_constraint(-2 * x1 + 10 * x2 <= 25)
        self.mip_model.set_objective(x1 + x2)
        self.mip_model.set_mip_sense(LPSense.MAX)
        # Run feasibility pump
        self.fs.compute(max_iter=10)
        # Print results
        print("x1 = {}".format(self.fs.variable_solution(x1)))
        print("x2 = {}".format(self.fs.variable_solution(x2)))

    def test_random_example(self):
        return
        from random import Random
        r = Random(10)
        variables = []
        for i in range(10):
            type = VarTypes.CONTINUOUS if r.randint(1, 10) <= 6 else VarTypes.INTEGER
            lb = r.randint(-1000, 1000)
            ub = r.randint(lb + 1, lb + 2000)
            var = self.mip_model.add_variable("x{}".format(i), var_type=type, lb=lb, ub=ub)
            variables.append(var)
        for i in range(5):
            start = r.randint(0, len(variables) - 3)
            end = r.randint(len(variables) - 3, len(variables))
            lin_expr = variables[start]
            for j in range(start + 1, end):
                lin_expr = lin_expr + r.randint(-1000, 1000) * variables[j]
            if i == 4:
                self.mip_model.set_objective(lin_expr)
            else:
                self.mip_model.add_constraint(lin_expr <= r.randint(10, 1000))
        self.mip_model.set_mip_sense(LPSense.MAX)
        self.fs.compute(max_iter=100)


if __name__ == '__main__':
    unittest.main()
