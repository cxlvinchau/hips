Fractional diving
====================

:class:`hips.heuristics.FractionalDiving` is a diving heuristic, that bounds the integer variable with lowest fractionality to the nearest
integer in each dive. The idea is based on page 17 of :cite:p:`2006:berthold`. It can be used to find a quick initial solution
or an efficient direction of branching in the branch and bound.

The heuristic traverses one path of the branch and bound tree of the MIP model to the leaf node. At each branch of the tree,
the variable :math:`x_j` with lowest fractionality :math:`f(x_j)` with respect to the current relaxation solution is bound
to the closest integer value :math:`[x_j]`. This is done as follows:

.. math::
    \begin{array}{l@c@c@r}
        if & & & x_j - \lfloor x_j \rfloor \le \lceil x_j \rceil - x_j\\
        then & & & upper\_bound(x_j) \leftarrow \lfloor x_j \rfloor\\
        else & & & lower\_bound(x_j) \leftarrow \lceil x_j \rceil
    \end{array}

The traversal is discontinued if any relaxation is infeasible or a feasible integer solution is found.