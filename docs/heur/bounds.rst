Bounds Heuristic
================

This heuristic is implemented after the scipopt primal heuristic 'heur_bounds.h'.
The `ScipOpt <https://www.scipopt.org/doc/html/heur__bound_8h.php>`_ library describes this as a
"heuristic which fixes all integer variables to a bound (lower/upper) and solves the remaining LP ".
Although this heuristic in most cases leads to no feasible solution, it is often a good entry point, as it is very efficiently computable.

The heuristic can be found in the ScipOpt library documentation under the following link:
`heur_bound.h File Reference <https://www.scipopt.org/doc/html/heur__bound_8h.php>`_.

This heuristic fixes every integer and binary variable to a respective bound and solves the remaining Linear Program.
There are 3 ways to use this heuristic, represent by the values of the enum :class:`hips.constants.BoundDirection`.
In the cases :class:`LOWER <hips.constants.BoundDirection>` or :class:`UPPER <hips.constants.BoundDirection>`,
every integer variable is fixed to their respective lower or upper bound respectibely.
In case :class:`CLOSEST <hips.constants.BoundDirection>` is selected, each integer variable is fixed to the bound
closest to the initial relaxation LP solution.

You can find an example in the following notebook:
.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/bounds-example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>
