import unittest
from hips import load_problem_gurobi
from hips.heuristics import TwoStageFeasibilityPump


class TwoStageFeasibilityPumpTest(unittest.TestCase):

    def test_bppc8_02(self):
        mip = load_problem_gurobi("bppc8-02")
        fp = TwoStageFeasibilityPump(mip)
        fp.compute(max_iter=100)


if __name__ == '__main__':
    unittest.main()
