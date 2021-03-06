from hips import GUROBI_AVAILABLE, CLP_AVAILABLE


def skip_when_clp_solver(func):
    """
    Decorator to be used in heuristics when certain steps need to be skipped for ClpSolver because of compatibility
    reasons
    :param func: The function to be decorated
    :return: function
    """

    def wrapper(*args, **kwargs):
        if CLP_AVAILABLE:
            from hips.solver import ClpSolver
            if isinstance(args[0].relaxation.concrete_solver, ClpSolver):
                return
            else:
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return wrapper


from hips.heuristics._feasibility_pump import FeasibilityPump, TwoStageFeasibilityPump
from hips.heuristics._bounds import HeuristicBounds
from hips.heuristics._abstract_diving import AbstractDiving
from hips.heuristics._fractional_diving import FractionalDiving
from hips.heuristics._line_search_diving import LineSearchDiving
from hips.heuristics._rens import RENS
from hips.heuristics._simple_rounding import SimpleRounding
