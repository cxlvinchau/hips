RENS
====
Relaxation enforced neighborhood search, or short RENS, introduced by :cite:p:`Berthold2013` is a heuristic
for heuristically solving mixed-integer programs with binary and integer variables. The idea is to
solve the relaxation of the problem and use the solution of the relaxed solution to introduce new bounds.

W.l.o.g. suppose the feasible region of a relaxation of a problem is given by :math:`Ax \leq b` and let :math:`x^*` be
the optimal solution of the problem. RENS adds the constraints :math:`{x \leq \lceil x^* \rceil}` and :math:`{x \geq \lfloor x^* \rfloor}`
to the original problem and solves it using a mixed-integer program solver. Note that the computed solution, if it exists,
gives us the best solution that can be obtained from rounding the solution of the relaxation. Observe that the introduced
bounds do not have any effect on binary variables, except when their value in the relaxation is :math:`0` or :math:`1`.

In HIPS the :class:`RENS <hips.heuristics.RENS>` class implements this heuristic. Now we show how to use RENS in HIPS.


.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/rens-example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

.. code-block:: python

    from hips import load_problem
    from hips.heuristics import RENS

    # Load a problem
    mip = load_problem("gen-ip054")
    # Instantiate heuristic with MIP
    rens = RENS(mip)
    # Start the computation
    rens.compute(max_iter=100)
    # Print the objective value
    print(rens.get_objective_value())
    # Print the solution
    print({var: rens.variable_solution(var) for var in mip.get_variables()})

In this example we consider the `gen-ip054 problem <https://miplib2017.zib.de/instance_details_gen-ip054.html>`_
from MIPLIB 2017 :cite:`miplib2017` and use :func:`hips.load_problem` to load it.
The problem has 30 variables, of which all are integer, and 27 constraints. After loading the problem, we can simply
instantiate :class:`RENS <hips.heuristics.RENS>` with it and then call the :func:`compute <hips.heuristics.RENS.compute>`
method. In RENS, the ``max_iter`` argument correspond to the maximum number of nodes we want to visit in the branch
and bound tree. The smaller the number, the earlier the computation terminates. However, when the maximum number of
nodes is set too small, RENS might not be able to find a feasible solution at all. Further, a larger maximum number
of nodes potentially results in a solution with a better objective.