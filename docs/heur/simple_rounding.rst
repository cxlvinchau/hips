Simple Rounding
===============

The **Simple Rounding** heuristic rounds each integer and binary variable to the closest integer with respect to the solution of the relaxation.
The approach roughly follows the idea presented in :cite:`2006:berthold`, although the heuristic from the paper rounds
only the trivially roundable variables (refer to :func:`hips.models._mip_model.trivially_roundable`). In HIPS the
:class:`hips.heuristics.SimpleRounding` class implements the **Simple Rounding** heuristic.

First the LP relaxation of the model is solved resulting in the solution :math:`\bar{x}`. Every integer or binary variable :math:`x_j` is then rounded to the integer value
:math:`[x_j]` closest to its value in the LP solution. The resulting MIP solution is then checked for feasibility.

Example
-------

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/simple_rounding_example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

In the following we consider a simple mixed-integer program and use **Simple Rounding** to find a solution.
The example can also be found on the Google Colab notebook linked above.

.. code-block:: python

    from hips import VarTypes, HIPSArray, ProblemSense
    from hips.models import MIPModel
    from hips.solver import GurobiSolver
    from hips.heuristics import SimpleRounding

    # Create model with GurobiSolver
    mip_model = MIPModel(GurobiSolver())
    # Create variable
    x = mip_model.add_variable("x", VarTypes.INTEGER, lb=0, ub=float("inf"), dim=2)
    # Add constraints
    mip_model.add_constraint(HIPSArray([1,2/3])*x <= 2)
    mip_model.add_constraint(HIPSArray([1,1.5])*x <= 3)
    # Specify objective and set problem sense
    mip_model.set_objective(HIPSArray([1,1])*x)
    mip_model.lp_model.set_lp_sense(ProblemSense.MAX)

    # Run the heuristic and output the solution
    heur = SimpleRounding(mip_model)
    heur.compute()
    print("Status: {}".format(heur.get_status()))
    print("Found solution: {}".format(heur.get_objective_value()))
    print("With Variable values: {}".format({var: heur.variable_solution(var) for var in mip_model.get_variables()}))