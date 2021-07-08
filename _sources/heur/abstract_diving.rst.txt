Diving Heuristics
=================

The following heuristics are so called **Diving Heuristics**. The general idea of **Diving Heuristics** is to quickly
depth-first traverse the *branch\&bound* tree to reach one of its leave nodes. This quick traversal down the tree leads to
the term **diving**. At each node of the tree the heuristic decides on which variable to branch, based on some promising
intuition. The specific branching condition depends on the type of heuristic.

A **Diving Heuristic** will stop in two cases:

    1. The current LP relaxation is infeasible
    2. The iteration limit is reached

In the first case, the LP relaxation is infeasible. In this case,
the heuristic will be aborted and no MIP solution was found. The second case occurs if the heuristic exceeds a predetermined
iteration limit. In this case, the heuristic will yield the best found MIP solution, if any were found.

    3. The current LP relaxation solution is worse than the incumbent solution

A third case can be constructed by providing an initial MIP solution to the run of the heuristic. In case the solution
of the current LP relaxation is worse than this incumbent MIP solution, the heuristic will abort, as any further branching
can only lead to worse solutions.

**Diving Heuristics** can be useful in many different scenarios. Since these heuristics do not require an MIP solver nor an
incumbent MIP solution, they can be used to find an initial solution for other heuristics. Although, in many cases we do
not search for the best solution to the MIP, but rather only a feasible solution.
Furthermore, diving heuristics can be used in combination with a full *branch\&bound* run, to quickly find feasible solutions
to the MIP. This means that the bounding can be done early, thereby ignoring larger portions of the tree and leading to
a major decrease in computation time.

Unfortunately **Diving Heuristics** do not always find a feasible solution. Since the size of the *branch\&bound* tree exponentially
increases in the number of variables, the chance of a **Diving Heuristic** finding a successful path is proportionally small. Nevertheless,
the low computational cost of these heuristics justifies their application in practice.

Fractional diving
-----------------

**Fractional Diving** is a diving heuristic, that bounds the integer variable with lowest fractionality to the nearest
integer as its branching condition. The idea is based on page 17 of :cite:p:`2006:berthold`. It can be used to find a quick initial solution
or an efficient direction of branching in the *branch&bound*. In HIPS the heuristic is implemented in the :class:`FractionalDiving <hips.heuristics.FractionalDiving>` class.

The heuristic traverses one path of the branch and bound tree of the MIP model to the leaf node. At each branch of the tree,
the variable :math:`x_j` with the lowest fractionality :math:`f(x_j)` with respect to the current relaxation solution is bounded
to the closest integer value :math:`[x_j]`. This is done as follows:

.. math::
        \textbf{if} \quad x_j - \lfloor x_j \rfloor \le \lceil x_j \rceil - x_j\\
        \textbf{then} \quad upper\_bound(x_j) \leftarrow \lfloor x_j \rfloor\\
        \textbf{else} \quad lower\_bound(x_j) \leftarrow \lceil x_j \rceil

The traversal is discontinued if any relaxation is infeasible or a feasible integer solution is found.

Example
_______

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/fractional_diving_example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

In this example we consider a simple mixed-integer program. The example can also be found on Google Colab.

First, we define a method that creates the model.

.. code-block:: python

    from hips import HIPSArray, VarTypes, ProblemSense
    from hips.models import MIPModel
    from hips.solver import GurobiSolver
    from hips.heuristics import FractionalDiving

    def build_model(mip_model):
        # Create variables
        x = mip_model.add_variable("x", VarTypes.INTEGER, lb=0, ub=float("inf"), dim=2)
        # Add constraints
        mip_model.add_constraint(HIPSArray([-3,2])*x <= 2)
        mip_model.add_constraint(HIPSArray([2,2])*x <= 7)
        # Set objective and problem sense
        mip_model.set_objective(HIPSArray([1,2])*x)
        mip_model.set_mip_sense(ProblemSense.MAX)

Afterwards, we instantiate the model, apply the heuristic and print the found solution.

.. code-block:: python

    mip_model = MIPModel(GurobiSolver())
    build_model(mip_model)

    heur = FractionalDiving(mip_model)
    heur.compute()

    print("Status: {}".format(heur.get_status()))
    print("Found solution: {}".format(heur.get_objective_value()))
    print("With Variable values: {}".format({var: heur.variable_solution(var) for var in mip_model.get_variables()}))

Line Search Diving
------------------
Now we consider the **Line Search Diving** heuristic as presented by :cite:`Hendel2011`. As the name suggests, this
heuristic follows the general structure of a diving heuristic, i.e. bounds are introduced or variables are fixed to
explore a path in the branch and bound tree. In :class:`LineSearchDiving <hips.heuristics.LineSearchDiving>`, the selected variable in each step is fixed to a value.

The choice of the variable that is fixed is made as follows. Suppose :math:`x^R` is the solution found at the root
node :math:`R` in the branch and bound algorithm. Let :math:`N` be an arbitrary node within the branch and bound tree
(i.e. not the root node) and :math:`x^N` the corresponding solution. At :math:`N` line search diving considers the line
between :math:`x^N` and :math:`x^R` and conceptually moves towards :math:`x^R` and checks which variable becomes integer first.
This variable is then selected and fixed.

Since our heuristic does not operate within a branch and bound algorithm, the initial variables to fix/select
are chosen randomly.

Example
_______

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/line_search_diving_example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

In the following, we consider the `gr4x6 <https://miplib.zib.de/instance_details_gr4x6.html>`_ problem from MIPLIB 2017 :cite:`miplib2017`.
The problem is already part of HIPS, so there is no need to download any files.

.. code-block:: python

    from hips import load_problem
    from hips.heuristics import LineSearchDiving

    # Load problem
    mip_model = load_problem("gr4x6")

    # Instantiate diving heuristic
    diver = LineSearchDiving(mip_model)
    # Deactivate trivial rounding
    diver._round_trivially = lambda : False
    # Start computation
    diver.compute()

    # Output solution
    print(f"Status: {diver.get_status()}")
    print(f"Found solution: {diver.get_objective_value()}")
    print(f"With Variable values: { {var: diver.variable_solution(var) for var in mip_model.get_variables()} }")