from hips.solver._clp_solver import ClpSolver


def skip_when_clp_solver(func):
    """
    Decorator to be used in heuristics when certain steps need to be skipped for ClpSolver because of compatibility
    reasons
    :param func: The function to be decorated
    :return: function
    """
    def wrapper(*args, **kwargs):
        if isinstance(args[0].relaxation.concrete_solver, ClpSolver):
            return
        else:
            func(*args, **kwargs)

    return wrapper

from hips.heuristics._heur_feasibility_pump import FeasibilityPump
from hips.heuristics._heur_bounds import HeuristicBounds
from hips.heuristics._heur_abstract_diving import AbstractDiving
from hips.heuristics._heur_fractional_diving import FractionalDivingHeuristic
from hips.heuristics._line_search_diving import LineSearchDiving

__all__ = ["FeasibilityPump", "HeuristicBounds", "AbstractDiving", "FractionalDivingHeuristic"]