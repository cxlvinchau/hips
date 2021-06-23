Getting started
===============
On this page we show you how to get started with HIPS. We assume that you have successfully completed the setup.

A simple linear program
-----------------------
Defining the program
____________________
Let us start with defining a linear program in HIPS. First, we need to decide which solver we would like to use. In this
example we use the :class:`GurobiSolver <hips.solver.GurobiSolver>`, but any other supported solver also works. Under the
hood, HIPS adds variables and constraints directly to the concrete solver to increase efficiency.

Suppose we are given the following linear program:

.. math::
    \begin{array}{lr@{}c@{}r@{}l}
    \text{maximize }   & 2 x_1 + 4 x_2  \\
    \text{subject to } & x_1 + 2 x_2 \leq 20 \\
                       & 3 x_1 - x_2 \leq 10 \\
                       & x_1, x_2 \geq 0 \\
                       & x_1, x_2 \in \mathbb{R}
    \end{array}

In HIPS, we can express the program as follows.

.. code-block:: python

    from hips import ProblemSense
    from hips.solver import GurobiSolver
    from hips.models import LPModel

    # Create solver
    solver = GurobiSolver()
    # Create LP model
    model = LPModel(solver)
    # Create variables
    x_1, x_2 = model.add_variable("x_1", lb=0), model.add_variable("x_2", lb=0)
    # Set sense
    model.set_lp_sense(ProblemSense.MAX)
    # Set objective
    model.set_objective(2*x_1 + 4*x_2)
    # Add constraints
    model.add_constraint(x_1 + 2*x_2 <= 20)
    model.add_constraint(3*x_1 - x_2 <= 10)

As you can see the definition of linear programs is very straightforward. However, for larger linear programs, this might
be a little bit cumbersome. Particularly, when we have many variables. Therefore, HIPS supports high-dimensional variables.
Below you can see the same linear program expressed with a single 2 dimensional variable.

.. code-block:: python

    from hips import ProblemSense
    from hips.solver import GurobiSolver
    from hips.models import LPModel, HIPSArray

    # Create solver
    solver = GurobiSolver()
    # Create LP model
    model = LPModel(solver)
    # Create 2 dim. variable with lower bound 0
    x = model.add_variable("x", lb=0, dim=2)
    # Set sense
    model.set_lp_sense(ProblemSense.MAX)
    # Set objective
    model.set_objective(HIPSArray([2, 4]) * x)
    # Add constraint
    model.add_constraint(HIPSArray([[1, 2], [3, -1]]) * x <= HIPSArray([20, 10]))

Observe that we have additionally imported :class:`HIPSArray <hips.models.HIPSArray>` to work with the 2 dimensional variable.
In contrast to the code above, we essentially work with vectors/matrices containing the coefficients for the variables.

.. note::
    Due to vectorization, it is often more efficient to use high-dimensional variables. Particularly, the implemented solvers
    and heuristics strongly benefit from high-dimensional variables.

Optimizing the program
______________________
Now, let us optimize the program and output the objective value and values for the variables.

The code for the first model.

.. code-block:: python

    # Optimize the program
    model.optimize()
    # Print the objective value
    print(f"Objective value: {model.get_objective_value()}")
    # Print the values of the variables
    print(f"x_1: {model.variable_solution(x_1)}")
    print(f"x_2: {model.variable_solution(x_2)}")

The code for the second model.

.. code-block:: python

    # Optimize the program
    model.optimize()
    # Print the objective value
    print(f"Objective value: {model.get_objective_value()}")
    # Print the values of the variables
    print(f"x: {model.variable_solution(x)}")


High-dimensional constraints
----------------------------
As you have seen in the previous section, HIPS can work with matrices and vectors. In this section, we explain how work
with high-dimensional constraints in more detail.

TODO

Mixed integer programs
----------------------

Loading mps files
-----------------
