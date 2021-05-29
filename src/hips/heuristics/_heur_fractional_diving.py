import math

import numpy as np

from hips import HIPSArray
from hips.constants import VariableBound
from hips.heuristics._heur_abstract_diving import AbstractDiving
from hips.models import MIPModel


class FractionalDivingHeuristic(AbstractDiving):
    """
    Implements a concrete diving heuristic, that bounds the variable x_j with lowest fractionality f(x_j) to the nearest
    integer. The idea is based on Berthold_Primal_Heuristics_For_Mixed_Integer_Programs.pdf; Page 17;
    """

    def __init__(self, mip_model: MIPModel, current_best_objective: float = None):
        super().__init__(mip_model, current_best_objective)
        self.revert_bounds = {}

    def _dive(self):
        """
        Compute the variable from the self.fractional_index_set with the lowest fractionality and bound it to the
        nearest integer.

        :return:
        """
        fractionality = {}
        for frac_var in self.fractional_index_set:
            variable_value = self._x[frac_var[0]].to_numpy()[frac_var[1]]
            fractionality[frac_var] = min(abs(variable_value-math.floor(variable_value)), abs(variable_value-math.ceil(variable_value)))
        lowest_frac_var_index = sorted(fractionality, key=fractionality.get)[0]
        lfv_value = self._x[lowest_frac_var_index[0]].to_numpy()[lowest_frac_var_index[1]]
        if abs(lfv_value-math.floor(lfv_value)) <= abs(lfv_value-math.ceil(lfv_value)):
            # Bound upper bound to floor of variable_value
            new_bound = np.copy(lowest_frac_var_index[0].ub.to_numpy())
            new_bound[lowest_frac_var_index[1]] = math.floor(lfv_value)
            old_bound = lowest_frac_var_index[0].ub
            self.relaxation.set_variable_bound(lowest_frac_var_index[0], VariableBound.UB, HIPSArray(new_bound))
            if not lowest_frac_var_index[0] in self.revert_bounds:
                self.revert_bounds[lowest_frac_var_index[0]] = (VariableBound.UB, old_bound)
        else:
            # Bound lower bound to ceil of variable_value
            new_bound = np.copy(lowest_frac_var_index[0].lb.to_numpy())
            new_bound[lowest_frac_var_index[1]] = math.ceil(lfv_value)
            old_bound = lowest_frac_var_index[0].ub
            self.relaxation.set_variable_bound(lowest_frac_var_index[0], VariableBound.LB, HIPSArray(new_bound))
            if not lowest_frac_var_index[0] in self.revert_bounds:
                self.revert_bounds[lowest_frac_var_index[0]] = (VariableBound.LB, old_bound)

    def _revert(self):
        """
        Reverts the bounds set by the _dive() method to the start state of the heuristic.

        :return:
        """
        for var, bound in self.revert_bounds.items():
            self.relaxation.set_variable_bound(var, bound[0], bound[1])
