Two Stage Feasibility Pump
==========================

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/two-stage-fp-example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

The **Two Stage Feasibility pump** proposed by :cite:p:`BERTACCO200763` is an extension of the **Feasibility Pump** :cite:p:`Fischetti2005` and can
be used to solve general mixed integer programs, i.e. programs containing binary and integer variables. In contrast, the original
feasibility pump is only designed for mixed integer programs containing binary variables only.

The basic idea of this feasibility pump is to handle binary and integer variables in two different stages. In the first stage,
the integer variables are ignored, i.e. treated as if they were continuous, and only the binary variables are considered.
The first stage is completed once a feasible solution w.r.t. the binary variables has been found or when the maximum iteration
has been reached. Afterwards, in the second stage, the integer variables are considered. Note that the original feasibility
pump can also handle integer variables, but might be less suited for this purpose.

In HIPS, the :class:`hips.heuristics.TwoStageFeasibilityPump` implements the described heuristic.

.. code-block:: python

    from hips import load_problem
    from hips.heuristics import TwoStageFeasibilityPump

    mip = load_problem("bppc8-02")
    fp = TwoStageFeasibilityPump(mip)
    fp.compute(max_iter=100)

    # Print objective value
    print(fp.get_objective_value())

    # Print solution
    print({var: fp.variable_solution(var) for var in mip.get_variables()})

In this example we consider the `bppc8-02 problem <http://miplib2017.zib.de/instance_details_bppc8-02.html>`_
from MIPLIB 2017 :cite:`miplib2017` and use :func:`hips.load_problem` to load it. Here, ``max_iter=100`` means that at most
100 iterations are spent in the first and second stage, respectively. Consequently, at most 200 iterations are computed
in total.