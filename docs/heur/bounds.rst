Bounds Heuristic
================

This heuristic is implemented after the scipopt primal heuristic 'heur_bounds.h'.
The `ScipOpt <https://www.scipopt.org/doc/html/heur__bound_8h.php>`_ library describes this as a
"heuristic which fixes all integer variables to a bound (lower/upper) and solves the remaining LP ".
Although this heuristic in most cases leads to no feasible solution, it is often a good entry point, as it is very efficiently computable.

The heuristic can be found in the ScipOpt library documentation under the following link:
`heur_bound.h File Reference <https://www.scipopt.org/doc/html/heur__bound_8h.php>`_.

This heuristic fixes every integer and binary variable to a respective bound and solves the remaining Linear Program.
There are 3 ways to use this heuristic, represent by the values of the enum :class:`hips.heuristics.BoundDirection`.
In the cases :ref:`LOWER <src/hips/constants.py:61>` or :ref:`UPPER <src/hips/heuristics/_bounds.py:15>`, every integer variable is fixed to their respective lower or upper bound respectibely.
In case :ref:`CLOSEST <src/hips/heuristics/_bounds.py:16>` is selected, each integer variable is fixed to the bound closest to the initial relaxation LP solution.