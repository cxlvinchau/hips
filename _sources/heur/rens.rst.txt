RENS
====
Relaxation enforced neighborhood search, or short RENS, introduced by :cite:p:`Berthold2013` is a heuristic
for heuristically solving mixed-integer programs with binary and integer variables. The idea is to
solve the relaxation of the problem and use the solution of the relaxed solution to introduce new bounds.

W.l.o.g. suppose the feasible region of a relaxation of a problem is given by :math:`Ax \leq b` and let :math:`x^*` be
the optimal solution of the problem. RENS adds the constraints :math:`{x \leq \lceil x^* \rceil}` and :math:`{x \geq \lfloor x^* \rfloor}`
to the original problem and solves it using a mixed-integer program solver. Note that the computed solution, if it exists,
gives us the best solution that can be obtained from rounding the solution of the relaxation.

In HIPS the :class:`RENS <hips.heuristics.RENS>` class implements this heuristic. Now we show how to use RENS in HIPS.

.. code-block:: python

    from hips import load_problem
    from hips.heuristics import RENS

    # Load a problem
    mip = load_problem("gr4x6")
    # Instantiate heuristic with MIP
    rens = RENS(mip)
    # Start the computation
    rens.compute(10)
    # Print the objective value
    print(rens.get_objective_value())
    # Print the solution
    print({var: rens.variable_solution(var) for var in mip.get_variables()})

Note that we have used :func:`hips.load_problem` to load a problem. In this example we consider 