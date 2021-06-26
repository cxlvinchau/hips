Linear search diving
====================

Now we consider the line search diving heuristic as presented by :cite:`Hendel2011`. As the name suggests, this
heuristic follows the general structure of a diving heuristic, i.e. bounds are introduced or variables are fixed to
explore a branch of a branch and bound tree. In :class:`hips.heuristics.LineSearchDiving`, the selected variable in each step is fixed to a value.

The choice of the variable that is fixed is made as follows. Suppose :math:`x^R` is the solution found at the root
node :math:`R` in the branch and bound algorithm. Let :math:`N` be an arbitrary node within the branch and bound tree
(i.e. not the root node) and :math:`x^N` the corresponding solution. At :math:`N` line search diving considers the line
between :math:`x^N` and :math:`x^R` and conceptually moves towards :math:`x^R` and checks which variable becomes integer first.
This variable is then selected and fixed.

Since our heuristic does not operate within a branch and bound algorithm, the initial variables that are fixed/selected
are chosen randomly.