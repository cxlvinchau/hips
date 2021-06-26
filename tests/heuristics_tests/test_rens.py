import unittest

from hips import ProblemSense
from hips.heuristics import RENS
from hips.loader import load_mps_advanced
from hips.models import MIPModel
from hips.solver import GurobiSolver, ClpSolver


class RENSTest(unittest.TestCase):

    def test_clp(self):
        model = MIPModel(ClpSolver())
        load_mps_advanced(model, "../../src/hips/problems/mps_files/gr4x6.mps")
        model.set_mip_sense(lp_sense=ProblemSense.MIN)
        rens = RENS(model)
        rens.compute(10)
        print(rens.get_objective_value())
        #print({var: rens.variable_solution(var) for var in model.variables})

    def test_gurobi(self):
        model = MIPModel(GurobiSolver())
        load_mps_advanced(model, "../../src/hips/problems/mps_files/gr4x6.mps")
        model.set_mip_sense(lp_sense=ProblemSense.MIN)
        rens = RENS(model)
        rens.compute(10)
        print(rens.get_objective_value())
        #print({var: rens.variable_solution(var) for var in model.variables})


if __name__ == '__main__':
    unittest.main()
