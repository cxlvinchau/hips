Bounds Heuristic
================

The **Bounds Heuristic** is implemented according to the scipopt primal heuristic ``heur_bounds.h``.
The `ScipOpt <https://www.scipopt.org/doc/html/heur__bound_8h.php>`_ library describes it as a
"heuristic which fixes all integer variables to a bound (lower/upper) and solves the remaining LP".
Although this heuristic leads to no feasible solution in most cases, it is often a good entry point, as it is very efficiently computable.

The heuristic can be found in the ScipOpt library documentation under the following link:
`heur_bound.h File Reference <https://www.scipopt.org/doc/html/heur__bound_8h.php>`_. In HIPS the heuristic is
implemented by :class:`hips.heuristics.HeuristicBounds`.

This heuristic fixes every integer and binary variable to a respective bound and solves the remaining linear program.
There are 3 ways to use this heuristic, represented by the values of the enum :class:`hips.constants.BoundDirection`.
In the cases :class:`LOWER <hips.constants.BoundDirection>` or :class:`UPPER <hips.constants.BoundDirection>`,
every integer variable is fixed to their respective lower or upper bound, respectively.
In case :class:`CLOSEST <hips.constants.BoundDirection>` is selected, each integer variable is fixed to the bound
closest to the initial relaxation LP solution.

Example
-------

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/bounds-example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

Now let us consider a simple example where apply the **Bounds Heuristic**. The example can also be found on Google Colab.
First, we define a method that creates a simple mixed-integer program. Afterwards, we try out the different bound settings.

.. code-block:: python

    from hips import HIPSArray, VarTypes, ProblemSense, BoundDirection
    from hips.models import MIPModel
    from hips.solver import GurobiSolver
    from hips.heuristics import HeuristicBounds

    def build_model(mip_model):
        # Create variable
        x = mip_model.add_variable("x", VarTypes.INTEGER, lb=0, ub=2, dim=2)
        # Add constraints
        mip_model.add_constraint(HIPSArray([1,2/3])*x <= 2)
        mip_model.add_constraint(HIPSArray([1,3])*x <= 3)
        # Set objective function and problem sense
        mip_model.set_objective(HIPSArray([1,1])*x)
        mip_model.lp_model.set_lp_sense(ProblemSense.MAX)

**Fixing to lower bound**

.. code-block:: python

    # Test lower bound (LOWER) -> x* = [0,0]
    mip_model = MIPModel(GurobiSolver())
    build_model(mip_model)
    heur = HeuristicBounds(mip_model, BoundDirection.LOWER)
    heur.compute()
    print("Status: {}".format(heur.get_status()))
    print("Found solution: {}".format(heur.get_objective_value()))
    print("With Variable values: {}".format({var: heur.variable_solution(var).to_numpy() for var in mip_model.get_variables()}))
    print("#---------------------------#")

**Fixing to upper bound**

.. code-block:: python

    # Test upper bound (UPPER) -> Infeasible
    mip_model = MIPModel(GurobiSolver())
    build_model(mip_model)
    heur = HeuristicBounds(mip_model, BoundDirection.UPPER)
    heur.compute()
    print("Status: {}".format(heur.get_status()))
    print("#---------------------------#")

**Fixing to closest bound**

.. code-block:: python

    # Test closest bound (CLOSEST) -> [2,0]
    mip_model = MIPModel(GurobiSolver())
    build_model(mip_model)
    heur = HeuristicBounds(mip_model, BoundDirection.CLOSEST)
    heur.compute()
    print("Status: {}".format(heur.get_status()))
    print("Found solution: {}".format(heur.get_objective_value()))
    print("With Variable values: {}".format({var: heur.variable_solution(var).to_numpy() for var in mip_model.get_variables()}))
    print("#---------------------------#")

Observe that the outcome of the computation differs, depending on the bound setting. This has to be kept in mind when using
the heuristic.