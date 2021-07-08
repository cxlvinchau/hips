import unittest
from hips import ProblemSense, load_problem_clp
from hips.heuristics import LineSearchDiving


class LineSearchDivingTest(unittest.TestCase):

    def test_gr4x6(self):
        # Load problem
        mip_model = load_problem_clp("gr4x6")

        # Instantiate diving heuristic
        diver = LineSearchDiving(mip_model)
        # Deactivate trivial rounding
        diver._round_trivially = lambda: False
        # Start computation
        diver.compute()


if __name__ == '__main__':
    unittest.main()
