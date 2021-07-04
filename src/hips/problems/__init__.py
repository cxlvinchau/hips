import os

from hips import ProblemSense
from hips.models import MIPModel

dir_path = os.path.dirname(os.path.realpath(__file__))
from hips.loader import load_mps

_solver_name = None
try:
    import gurobipy

    _solver_name = "GUROBI"
except:
    pass

if _solver_name is None:
    try:
        import cylp

        _solver_name = "CLP"
    except:
        pass


def _get_solver():
    if _solver_name == "GUROBI":
        from hips.solver import GurobiSolver
        return GurobiSolver()
    elif _solver_name == "CLP":
        from hips.solver import ClpSolver
        return ClpSolver()


def load_problem_clp(problem_name):
    from hips.solver import ClpSolver
    problem = MIPModel(ClpSolver())
    problem.set_mip_sense(ProblemSense.MIN)
    load_mps(problem, os.path.join(dir_path, "mps_files", f"{problem_name}.mps"))
    return problem


def load_problem_gurobi(problem_name):
    from hips.solver import GurobiSolver
    problem = MIPModel(GurobiSolver())
    problem.set_mip_sense(ProblemSense.MIN)
    load_mps(problem, os.path.join(dir_path, "mps_files", f"{problem_name}.mps"))
    return problem


def load_problem(problem_name):
    """Loads a mixed-integer program that comes with HIPS.

    This method returns a mixed-integer program, given a problem name. HIPS already comes with a small set of mixed-integer
    programs. These problems were obtained from the MIPLIB 2017 :cite:`miplib2017`. The following problems can be loaded:

    - ``10teams`` (https://miplib.zib.de/instance_details_10teams.html)
    - ``bppc8-02`` (http://miplib2017.zib.de/instance_details_bppc8-02.html)
    - ``flugpl`` (http://miplib2017.zib.de/instance_details_flugpl.html)
    - ``gen-ip054`` (https://miplib2017.zib.de/instance_details_gen-ip054.html)
    - ``gr4x6`` (https://miplib.zib.de/instance_details_gr4x6.html)

    The listed problems were obtained from the MIPLIB 2017 (https://miplib.zib.de/index.html). We would like to thank
    the authors and people involved for their contribution and would like to emphasize that they are not linked to or involved in HIPS,
    nor do they endorse HIPS.

    The examples are licensed under Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) (https://creativecommons.org/licenses/by-sa/4.0/.)

    :param problem_name: Name of the problem. Please have a look at the list above to see which problems can be loaded
    :return: An instance of :class:`hips.models.MIPModel`
    """
    if _solver_name == "GUROBI":
        return load_problem_gurobi(problem_name)
    elif _solver_name == "CLP":
        return load_problem_clp(problem_name)