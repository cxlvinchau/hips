import unittest
from hips.solver import PulpSolver
from hips.models import Variable


class TestPulpSolver(unittest.TestCase):

    def setUp(self) -> None:
        self.solver = PulpSolver()
        self.vars = [Variable(str(i), id=i) for i in range(10)]

    def test_add_variable(self):
        for var in self.vars:
            self.solver.add_variable(var)

    def test_add_constr(self):
        self.solver.add_variable(self.vars[0])
        self.solver.add_variable(self.vars[1])
        self.solver.add_constraint(self.vars[0] + self.vars[1] <= 10)

    def test_set_objective(self):
        self.solver.add_variable(self.vars[0])
        self.solver.add_variable(self.vars[1])
        self.solver.set_objective(self.vars[0] + self.vars[1])


if __name__ == '__main__':
    unittest.main()
