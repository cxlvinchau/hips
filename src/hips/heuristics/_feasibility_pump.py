import math

from hips.heuristics._heuristic import Heuristic
from hips.models._lp_model import ProblemSense
from hips.models import MIPModel, HIPSArray, Variable
from hips.utils import is_close, all_close
from hips.heuristics import skip_when_clp_solver
from hips.constants import LPStatus, HeuristicStatus
import numpy as np


class FeasibilityPump(Heuristic):
    """Implementation of the original feasibility pump

    The feasibility pump is a heuristic for solving integer programs (MIPs) proposed by :cite:p:`Fischetti2005`.
    The basic idea is to repeatedly solve the MIP's relaxation, i.e. the MIP without integer constraints, round the
    obtained relaxed solution to the nearest integer and then find a solution that minimizes the distance to that rounded point.
    The process is repeated until a feasible point to the original MIP is found or some other stopping criterion is satisfied. Further,
    small perturbations are used to combat cycling.
    """

    def __init__(self, mip_model: MIPModel, t=None, alpha=None, seed=None):
        r"""Constructor

        :param mip_model: Mixed integer program model, instance of :class:`hips.models.MIPModel`
        :param t: Perturbation parameter, the greater the parameter the stronger the perturbation. By default ``None`` and
            the parameter is chosen to be n_binary_variables/2
        :param alpha: A value between 0 and 1 that determines how much the original objective should be taken into account.
            By default the original objective is ignored
        :param seed: Seed to enable reproducible results
        """
        super().__init__(mip_model)
        self.t = t
        self.alpha = alpha
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
        for var in [v for v in self.x_tilde_int if v not in self.positive_vars]:
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
        self.relaxation.set_lp_sense(ProblemSense.MIN)
        # Updates the objective function
        self.relaxation.set_objective(objective_bin + objective_int)

    def _remove_added_constraints(self):
        """
        Removes all the constraint from self.added_constraints and empties the list.

        :return: None
        """
        for constr_name in self.added_constraints:
            self.relaxation.remove_constraint(name=constr_name)
        self.added_constraints = []

    @skip_when_clp_solver
    def _remove_added_variables(self):
        """
        Removes variables that have been added during the update of the objective function

        :return: None
        """
        for var in list(self.positive_vars.values()) + list(self.negative_vars.values()):
            self.mip_model.lp_model.remove_variable(var)
        self.positive_vars = {}
        self.negative_vars = {}

    def _check_cycling(self, bin_sol, int_sol):
        """
        Checks whether the feasibility pump has cycled.

        :return: True if cycled, False otherwise
        """
        for var in bin_sol:
            if not all_close(bin_sol[var], self.x_tilde_bin[var]):
                return False
        for var in int_sol:
            if not all_close(int_sol[var], self.x_tilde_int[var]):
                return False
        return True

    def _check_long_cycle(self, bin_sol, int_sol, length=3):
        # Check last three solutions and check if the same binary solution has been computed twice
        for x_tilde_bin, _ in self._history[-length:]:
            # Check if solution is equal to previous solution
            exist_long_cycle_iteration = True
            for var in bin_sol:
                if not all_close(bin_sol[var], x_tilde_bin[var]):
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
        if self.iteration > 30:
            current_optimal_value = self.get_objective_value()
            if self._relaxation_sense == ProblemSense.MIN:
                self.relaxation.add_constraint(self._original_obj <= (alpha * self._relaxation_optimal_value
                                                                      + (1 - alpha) * current_optimal_value),
                                               name="_objective_constr_alpha_{}".format(alpha))
            else:
                self.relaxation.add_constraint(self._original_obj >= (alpha * self._relaxation_optimal_value
                                                                      + (1 - alpha) * current_optimal_value),
                                               name="_objective_constr_alpha_{}".format(alpha))
            self.added_constraints.append("_objective_constr_alpha_{}".format(alpha))

    def compute(self, max_iter=100):
        """
        Starts the computation of the feasibility pump.

        :param max_iter: The maximum number of iterations that should be performed. If the number of iterations is
                            reached, the computation terminated.
        :return: None
        """
        t = math.ceil(len(self.mip_model.binary_variables) / 2) if self.t is None else self.t
        self.iteration = 0
        while self.iteration < max_iter:
            # compute relaxation
            self._compute_relaxation()

            # Log objective value
            self.tracker.log("objective value", self.get_objective_value())

            # obtain solutions
            new_x_tilde_bin = {x: self._round_fs(self.relaxation.variable_solution(x)) for x in self.binary}
            new_x_tilde_int = {x: self._round_fs(self.relaxation.variable_solution(x)) for x in self.integer}

            # Check if the found solution is feasible for the mip
            if self.mip_model.is_feasible(
                    {var: self.relaxation.variable_solution(var) for var in self.relaxation.vars}):
                self.logger.info("Stopping early")
                break

            # Check cycling
            if self.iteration > 0 and self._check_cycling(new_x_tilde_bin, new_x_tilde_int):
                self._perturb_binary(t=t)
                self._perturb_integer()
                self._history.append((new_x_tilde_bin, new_x_tilde_int))
            elif self.iteration > 3 and self._check_long_cycle(new_x_tilde_bin, new_x_tilde_int):
                # Aggressive perturbation
                self._perturb_integer()
                for var in new_x_tilde_bin:
                    rho = self._rng.uniform(-0.3, 0.7)
                    # Compute masks, indicating which components to flip
                    mask = (abs((self.relaxation.variable_solution(var) - self.x_tilde_bin[var]).to_numpy()) + max(rho,
                                                                                                                   0) >= 0.5).astype(
                        int)
                    # Flip values
                    new_x_tilde_bin[var] = HIPSArray(abs(mask - new_x_tilde_bin[var].to_numpy()))
                    self.x_tilde_bin = new_x_tilde_bin
                    self.x_tilde_int = new_x_tilde_int
                    self._history.append((new_x_tilde_bin, new_x_tilde_int))
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
                if self.alpha is not None:
                    self._add_objective_constraint(self.alpha)

        self.logger.info("Finished computation in {} iteration(s)".format(self.iteration))

        # Set optimal value
        self._obj_val = self.relaxation.get_objective_value()
        # Remove variables
        self._remove_added_variables()
        # Remove constraints
        self._remove_added_constraints()

        # Restore original objective
        if self._original_obj:
            self.relaxation.set_objective(self._original_obj)

    def _perturb_binary(self, t):
        """
        Perturbs the value of binary variables to prevent cycling.

        :param t: Perturbation parameter
        :return: None
        """
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
        # self.logger.info("Flipped {} values".format(tt))
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
            self.x_tilde_bin[var_to_index[v_idx]] = HIPSArray(
                abs(arr - self.x_tilde_bin[var_to_index[v_idx]].to_numpy()))

    def _perturb_integer(self):
        """
        Perturbs integer variables to prevent cycling

        :param p: Probability of perturbing a non-integer variable
        :return:
        """
        for var in self.mip_model.integer_variables:
            solution = self.relaxation.variable_solution(var)
            mask = ~is_close(solution, HIPSArray(np.rint(solution.array)))
            if not np.any(mask):
                continue
            self.x_tilde_int[var].array[mask] += self._rng.choice([-1, 0, 1], len(mask[mask]))

    def variable_solution(self, var):
        return self._x[var]

    def get_objective_value(self) -> float:
        return self._original_obj.eval(self._x).reshape(-1).to_numpy()[0]

    def get_status(self):
        if self.mip_model.is_feasible({var: self.variable_solution(var) for var in self.relaxation.vars}):
            return HeuristicStatus.SOL_FOUND
        else:
            return HeuristicStatus.NO_SOL_FOUND


class TwoStageFeasibilityPump(Heuristic):
    r"""Implementation of feasibility pump with two stages

    This class implements a version of the feasibility pump that is applicable to general mixed integer programs, i.e.
    programs containing binary and integer variables, as proposed by :cite:p:`BERTACCO200763`. In contrast, the original
    feasibility pump :cite:`Fischetti2005` is only designed for mixed integer programs containing binary variables only. However, note that our
    implementation of the original feasibility pump is able to work with general mixed-integer programs.

    The basic idea of this feasibility pump is to handle binary and integer variables in two different stages. In the first stage,
    the integer variables are ignored, i.e. treated as if they were continuous, and only the binary variables are considered.
    The first stage is completed once a feasible solution w.r.t. the binary variables has been found or when the maximum iteration
    has been reached. Afterwards, in the second stage, the integer variables are considered. Note that the original feasibility
    pump can also handle integer variables, but might be less suited for this purpose.
    """

    def __init__(self, model: MIPModel, **kwargs):
        """Constructor

        :param model: Mixed integer program, instance of :class:`hips.models.MIPModel`
        :param kwargs: Additional arguments that are passed to the underlying original feasibility pump (see :class:`hips.heuristics.FeasibilityPump`).
        """
        super().__init__(model)
        self.feasibility_pump = FeasibilityPump(model, **kwargs)

    def compute(self, max_iter):
        """
        Executes the computation of the feasibility pump.

        :param max_iter: The maximum iteration in the two stages, respectively. This means that the total max iteration
        will be 2*max_iteration
        :return:
        """
        # First stage
        # In this stage we only consider the binary variables
        integer_variables = self.mip_model.integer_variables
        self.mip_model.integer_variables = []
        self.feasibility_pump.compute(max_iter)
        # Second stage
        # In this stage we add the integer variables to the problem
        self.mip_model.integer_variables = integer_variables
        self.feasibility_pump.compute(max_iter)

    def variable_solution(self, var: Variable):
        return self.feasibility_pump.variable_solution(var)

    def get_objective_value(self) -> float:
        return self.feasibility_pump.get_objective_value()

    def get_status(self):
        return self.feasibility_pump.get_status()
