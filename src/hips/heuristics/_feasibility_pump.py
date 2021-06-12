import math

from hips.heuristics._heuristic import Heuristic
from hips.models._lp_model import LPSense
from hips.models import MIPModel, HIPSArray
from hips import REL_TOLERANCE, ABS_TOLERANCE, is_close
from hips.heuristics import skip_when_clp_solver
from hips.constants import LPStatus
import numpy as np


class FeasibilityPump(Heuristic):
    """
    The feasibility pump is a heuristic for solving integer programs (MIPs) proposed by Fischetti et al. in 2005 (
    https://link.springer.com/article/10.1007/s10107-004-0570-3). The basic idea is to repeatedly solve the MIP's
    relaxation, i.e. the MIP without integer constraints, round the obtained relaxed solution to the nearest integer
    and then find a solution that minimizes the distance to that rounded point. The process is repeated until a
    feasible point to the original MIP is found or some other stopping criterion is satisfied. Further,
    small perturbations are used to combat cycling.

    This class implements the basic feasibility pump as described in the paper above.
    """

    def __init__(self, mip_model: MIPModel, T=0.5, seed=None):
        super().__init__(mip_model)
        self.T = T
        self.x_tilde_bin = dict()
        self.x_tilde_int = dict()
        self.positive_vars = {}
        self.negative_vars = {}
        self.added_constraints = []
        self._x = None
        self._var_counter = 0
        self._original_obj = self.relaxation.objective
        self._original_variables = self.relaxation.get_variables()
        self._obj_val = None
        self._history = []
        self._relaxation_optimal_value = None
        self._relaxation_sense = self.relaxation.lp_sense
        self._rng = np.random.default_rng(seed)

    @staticmethod
    def _round_fs(x):
        """
        Implements the rounding to the nearest integer solution.

        :param self:
        :param x:
        :return: Rounded value of x
        """
        return round(x)

    def _compute_relaxation(self):
        """
        This method computes the optimal solution of the relaxation or raises a warning if the relaxation is infeasible
        or unbounded. The optimal solution is stored in self.x.

        :return: None
        """
        self.logger.info("Computing relaxation")
        if self._original_obj is None:
            self._original_obj = self.relaxation.objective
        self.relaxation.optimize()
        if self.relaxation.get_status() != LPStatus.OPTIMAL:
            raise ValueError("MIP is infeasible")
        # Set optimal objective value of relaxation
        if self._relaxation_optimal_value is None:
            self._relaxation_optimal_value = self.relaxation.get_objective_value()
        # Store the optimal solution of the relaxation
        self._x = {x: self.relaxation.variable_solution(x) for x in self._original_variables}

    def _update_objective(self):
        """
        This method updates the objective function of the relaxation, according to the current rounded integer
        solution. Note that in the feasibility pump algorithm, we want to minimize the distance to a integer
        solution, by expressing the L1 distance as a linear expression and additional freshly added variables. This
        method introduces new variables and computes the linear expression accordingly.

        :return: None
        """
        # Create objective function for binary variables
        objective_bin = sum([HIPSArray(is_close(self.x_tilde_bin[var], np.zeros(var.dim)).astype(int)) * var for var in
                             self.x_tilde_bin])
        objective_bin += sum(
            -1 * [HIPSArray(is_close(self.x_tilde_bin[var], np.ones(var.dim)).astype(int)) * var for var in
                  self.x_tilde_bin])

        # Create variables and constraints for integer variables
        self.added_constraints = []
        for var in self.x_tilde_int:
            self.logger.info("Creating constraints and variables for {}".format(var.name))
            var_id = self._var_counter
            # Create slack variables
            var_pos = self.positive_vars.setdefault(var, self.relaxation.add_variable(
                "_aux_var{}+{}".format(var.name, var_id), lb=0, dim=var.dim))
            var_neg = self.negative_vars.setdefault(var, self.relaxation.add_variable(
                "_aux_var{}-{}".format(var.name, var_id), lb=0, dim=var.dim))

            # Create constraints
            # Express var as a combination positive, negative parts and x_tilde
            constr = (HIPSArray(np.identity(var_pos.dim)) * var + (-1) * HIPSArray(
                np.identity(var_pos.dim)) * var_pos + HIPSArray(np.identity(var_pos.dim)) * var_neg == self.x_tilde_int[
                          var])
            # Add constraints to relaxation
            self.relaxation.add_constraint(constr, name="_combination_constr{}".format(var_id))
            self.added_constraints.append("_combination_constr{}".format(var_id))

            # Increment the var counter
            self._var_counter += 1

        # Create objective function for integer variables
        # If x_tilde corresponds to the lower bound
        objective_int = sum(
            [HIPSArray(is_close(self.x_tilde_int[var], var.lb).astype(int)) * var for var in self.x_tilde_int])
        # if x_tilde corresponds to the upper bound
        objective_int += sum(
            [-1 * HIPSArray(is_close(self.x_tilde_int[var], var.ub).astype(int)) * var for var in self.x_tilde_int])

        for var in self.x_tilde_int:
            coef = HIPSArray(((var.lb < self.x_tilde_int[var]) & (self.x_tilde_int[var] < var.ub)).astype(int))
            objective_int += coef * self.positive_vars[var] + coef * self.negative_vars[var]

        # Changes the relaxation to minimization
        self.relaxation.set_lp_sense(LPSense.MIN)
        # Updates the objective function
        self.relaxation.set_objective(objective_bin + objective_int)
        # Logging
        self.logger.info("Updated objective to {}".format(self.relaxation.objective))

    def _remove_added_constraints(self):
        """
        Removes all the constraint from self.added_constraints and empties the list.

        :return: None
        """
        for constr_name in self.added_constraints:
            self.relaxation.remove_constraint(name=constr_name)
        self.added_constraints = []
        self.logger.info("Removed added constraints")

    @skip_when_clp_solver
    def _remove_added_variables(self):
        """
        Removes variables that have been added during the update of the objective function

        :return: None
        """
        for var in {**self.positive_vars, **self.negative_vars}.values():
            self.mip_model.lp_model.remove_variable(var)
        self.positive_vars = {}
        self.negative_vars = {}
        self.logger.info("Removed added variables")

    def _check_cycling(self, bin_sol, int_sol):
        """
        Checks whether the feasibility pump has cycled.

        :return: True if cycled, False otherwise
        """

        # TODO naive implementation for now
        for var in bin_sol:
            if not any(is_close(bin_sol[var], self.x_tilde_bin[var])):
                return False
        for var in int_sol:
            if not any(is_close(int_sol[var], self.x_tilde_int[var])):
                return False
        return True

    def _check_long_cycle(self, bin_sol, int_sol, length=3):
        # Check last three solutions and check if the same binary solution has been computed twice
        for x_tilde_bin, _ in self._history[-length:]:
            # Check if solution is equal to previous solution
            exist_long_cycle_iteration = True
            for var in bin_sol:
                if not any(is_close(bin_sol[var], x_tilde_bin[var])):
                    exist_long_cycle_iteration = False
                    break
            if exist_long_cycle_iteration:
                return True
        return False

    def _add_objective_constraint(self, alpha):
        """
        Adds a constraint that tries to ensure that we continue to find good solution w.r.t. to the original objective
        function. Note that this might lead to infeasible problems, depending on the choice of alpha. The higher alpha,
        the more we optimize towards the original objective function.

        :param alpha: Weighting factor between 0 and 1
        :return: None
        """
        if self.iteration > 2:
            current_optimal_value = self.get_objective_value()
            if self._relaxation_sense == LPSense.MIN:
                self.relaxation.add_constraint(self._original_obj <= (alpha*self._relaxation_optimal_value
                                               + (1-alpha) * current_optimal_value),
                                               name="_objective_constr_alpha_{}".format(alpha))
            else:
                self.relaxation.add_constraint(self._original_obj >= (alpha * self._relaxation_optimal_value
                                               + (1 - alpha) * current_optimal_value),
                                               name="_objective_constr_alpha_{}".format(alpha))
            self.added_constraints.append("_objective_constr_alpha_{}".format(alpha))

    def compute(self, max_iter=None, t=None, alpha=None):
        """
        Starts the computation of the feasibility pump.

        :param max_iter: The maximum number of iterations that should be performed. If the number of iterations is
                            reached, the computation terminated.
        :param t: Perturbation parameter.
        :param alpha: If alpha is set, the feasibility pump will try to optimize towards the objective function. The higher alpha,
                        the more we optimize towards the original objective function.
        :return: None
        """
        self.logger.info("Starting computation of feasibility pump")
        t = math.ceil(len(self.mip_model.binary_variables) / 2) if t is None else t
        self.iteration = 0
        while self.iteration < max_iter:
            self.logger.info("Iteration {}".format(self.iteration))
            # compute relaxation
            self._compute_relaxation()

            # Log objective value
            self.tracker.log("objective value", self.get_objective_value())

            # obtain solutions
            new_x_tilde_bin = {x: self._round_fs(self.relaxation.variable_solution(x)) for x in self.binary}
            new_x_tilde_int = {x: self._round_fs(self.relaxation.variable_solution(x)) for x in self.integer}

            # Check if the found solution is integer
            is_integer_solution = True
            for var in self.binary:
                if not all(is_close(self.relaxation.variable_solution(var), new_x_tilde_bin[var])):
                    is_integer_solution = False
                    break
            if is_integer_solution:
                for var in self.integer:
                    if not all(is_close(self.relaxation.variable_solution(var), new_x_tilde_int[var])):
                        is_integer_solution = False
                        break
            if is_integer_solution:
                self.logger.info("Stopping early")
                break

            # Check cycling
            if self.iteration > 0 and self._check_cycling(new_x_tilde_bin, new_x_tilde_int):
                self._perturb(t=t)
            elif self.iteration > 3 and self._check_long_cycle(new_x_tilde_bin, new_x_tilde_int):
                self.logger.info("Perform aggressive perturbation")
                # Aggressive perturbation
                for var in new_x_tilde_bin:
                    rho = self._rng.uniform(-0.3, 0.7)[0]
                    # Compute masks, indicating which components to flip
                    mask = (abs((self.relaxation.variable_solution(var) - self.x_tilde_bin[var]).to_numpy()) + max(rho, 0) >= 0.3).astype(int)
                    # Flip values
                    new_x_tilde_bin[var] = HIPSArray(abs(mask - new_x_tilde_bin[var].to_numpy()))
            else:
                # No cycling, update current solution
                self.x_tilde_bin = new_x_tilde_bin
                self.x_tilde_int = new_x_tilde_int
                self._history.append((new_x_tilde_bin, new_x_tilde_int))

            # Track feasibility objective
            if self.iteration > 0:
                self.tracker.log("feasibility objective", self.relaxation.get_objective_value())

            self.iteration += 1

            # Only remove variables, constraint and update the objective if a next iteration is started
            if self.iteration < max_iter:
                # Remove variables
                self._remove_added_variables()
                # Remove constraints
                self._remove_added_constraints()
                # Update objective function
                self._update_objective()
                # Add constraint to improve objective value if alpha is set
                if alpha is not None:
                    self._add_objective_constraint(alpha)

        self.logger.info("Finished computation in {} iteration(s)".format(self.iteration))

        # Set optimal value
        self._obj_val = self.relaxation.get_objective_value()

        # Restore original objective
        if self._original_obj:
            self.relaxation.set_objective(self._original_obj)

    def _perturb(self, t):
        """
        Perturbs the value of the solutions to prevent cycling.

        :param t: Perturbation parameter
        :return: None
        """

        # FIXME implement for integer variables (pretty non-trivial though)

        self.logger.info("Perturb to avoid cycling")
        # Enumerate binary variables
        binary_variables = list(enumerate(self.binary))
        # If there are no binary variables, then no flipping can be done
        if len(binary_variables) == 0:
            return
        # Map from index to binary variable
        var_to_index = dict(binary_variables)
        # bin_dist contains the distances for each variable component, var_index indicates the variables, comp_index the
        # index of the component within the variable
        bin_dist, var_index, comp_index = np.concatenate([np.array([abs(self.x_tilde_bin[variable] - self._x[variable]),
                                                                    np.ones(variable.dim) * idx,
                                                                    np.arange(0, variable.dim)]) for
                                                          idx, variable in binary_variables], axis=1)
        # Sort according to bin_dist
        arg_sorted = bin_dist.argsort()
        # Determine the number of components to flip
        tt = min(self._rng.integers(math.floor(t / 2), math.floor(1.5 * t), 1)[0], len(var_index))
        self.logger.info("Flipped {} values".format(tt))
        # Select the tt largest
        var_index = var_index.astype(int)[arg_sorted][-tt:]
        comp_index = comp_index.astype(int)[arg_sorted][-tt:]
        # Group indices together
        var_idx_to_indices = {}
        for v_idx, c_idx in zip(var_index, comp_index):
            l = var_idx_to_indices.setdefault(v_idx, [])
            l.append(c_idx)
        # Flip the values for every variable
        for v_idx, l in var_idx_to_indices.items():
            arr = np.zeros(self.x_tilde_bin[var_to_index[v_idx]].shape[0])
            arr[l] = 1
            # Flip the values
            self.x_tilde_bin[var_to_index[v_idx]] = HIPSArray(abs(arr - self.x_tilde_bin[var_to_index[v_idx]].to_numpy()))

    def variable_solution(self, var):
        return self._x[var]

    def get_objective_value(self) -> float:
        return self._original_obj.eval(self._x).reshape(-1).to_numpy()[0]
