import abc


class DistanceFunction(metaclass=abc.ABCMeta):

    def __init__(self,model,x,x_tilde):
        self.model = model
        self.x = x
        self.x_tilde = x_tilde

    @abc.abstractmethod
    def update_model(self):
        pass


class L1(DistanceFunction):
    '''Given an MIP model, this class creates constraints, variables and a linear objective function to express the
    L1 distance from x to point'''

    def __init__(self,model,x,x_tilde):
        super().__init__(model,x,x_tilde)

    def update_model(self):
        # Create objective function for binary variables
        x_tilde_bin = {var:self.x_tilde[var] for var in self.x_tilde if var in self.model.binary_variables}
        objective_bin = sum([1 * var if x_tilde_bin[var] == 0 else -1 * var for var in x_tilde_bin])

        # Create variables and constraints for integer variables
        x_tilde_int = {var:self.x_tilde[var] for var in self.x_tilde if var in self.model.integer_variables}
        for var in x_tilde_int:
            # Create slack variables
            var_pos = self.positive_vars.setdefault(var, self.relaxation.add_variable("+{}".format(self.var_count)))
            var_neg = self.negative_vars.setdefault(var, self.relaxation.add_variable("-{}".format(self.var_count)))
            self.var_count += 1

            # Create constraints
            # Express var as a combination positive, negative parts and x_tilde
            constr1 = (var + (-1) * var_pos + var_neg == self.x_tilde_int[var])
            # Non-negativity constraints
            constr2 = var_pos >= 0
            constr3 = var_neg >= 0
            # Add constraints to relaxation
            self.relaxation.add_constraint(constr1)
            self.relaxation.add_constraint(constr2)
            self.relaxation.add_constraint(constr3)

