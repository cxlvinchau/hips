Simple Rounding
===============

The class :class:`hips.heuristics.SimpleRounding` implements a simple rounding heuristic, that rounds each integer and
binary variable to the closest integer with respect to the relaxation LP solution.
The approach roughly follows the idea presented in :cite:`2006:berthold`, although the heuristic from the paper rounds
only the trivially roundable variables (refer to :meth:`hips.models._mip_model.trivially_roundable`).

First the LP relaxation of the model is solved resulting in the solution :math:`\bar{x}`. Every integer or binary variable :math:`x_j` is then rounded to the integer value
:math:`[x_j]` closest to its value in the LP solution. The resulting MIP solution is then checked for feasibility.