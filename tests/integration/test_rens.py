import unittest
from hips import ProblemSense, load_problem_clp
from hips.heuristics import RENS


class RENSTest(unittest.TestCase):

    def test_gr4x6(self):
        model = load_problem_clp("gr4x6")
        model.set_mip_sense(mip_sense=ProblemSense.MIN)
        rens = RENS(model)
        rens.compute(10)

    def test_genip054(self):
        # Load a problem
        mip = load_problem_clp("gen-ip054")
        # Instantiate heuristic with MIP
        rens = RENS(mip)
        # Start the computation
        rens.compute(max_iter=100)
        # Print the objective value
        print(rens.get_objective_value())
        # Print the solution
        print({var: rens.variable_solution(var) for var in mip.get_variables()})


if __name__ == '__main__':
    unittest.main()
