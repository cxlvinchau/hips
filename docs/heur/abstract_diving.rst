Diving Heuristics
=================

The following heuristics are so called **Diving Heuristics**. The general idea of **Diving Heuristics** is to quickly
depth first traverse the *branch\&bound* tree to reach one of its leave nodes. This quick traversal down the tree lead to
the term **diving**. At each node of the tree the heuristic decides on which variable to branch based on some promising
intuition. The specific branching condition depends on the type of heuristic.

A **Diving Heuristic** will stop in two cases:

    1. The current LP relaxation is infeasible
    2. The iteration limit is reached

The first one is if the current LP relaxation gets infeasible. In this case,
the heuristic will be aborted and no MIP solution was found. The second case occurs if the heuristic exceed a predetermined
iteration limit. In this case the heuristic will yield the best found MIP solution, if any were found.

    3. The current LP relaxation solution is worse than the incumbent solution

A third case can be constructed by providing an initial MIP solution to the run of the heuristic. In case the solution
of the current LP relaxation is worse than this incumbent MIP solution, the heuristic will abort, as any further branching
can only lead to worse solutions.

**Diving Heuristics** can be useful in many different scenarios. Since these heuristics do not require an MIP solver nor an
incumbent MIP solution, they can be used to find an initial solutions for other heuristics. Furthermore in many cases
any we do not search for the best solution to the MIP, rather than any feasible solution.
Furthermore diving heuristics can be used in combination with a full *branch\&bound* run, to quickly find feasible solutions
to the MIP. This allows to bound early and thus larger portions of the tree, which leads to major decrease in run time.

Unfortunately **Diving Heuristics** do not always find a feasible solution. Since the size of the *branch\&bound* tree exponentially
increases in the number of variables, the chance of success of a **Diving Heuristic** is proportionally small. Nevertheless,
the low computational cost of these heuristics encourages their application in practise.

Fractional diving
-----------------

:class:`hips.heuristics.FractionalDiving` is a diving heuristic, that bounds the integer variable with lowest fractionality to the nearest
integer in each dive. The idea is based on page 17 of :cite:p:`2006:berthold`. It can be used to find a quick initial solution
or an efficient direction of branching in the branch and bound.

The heuristic traverses one path of the branch and bound tree of the MIP model to the leaf node. At each branch of the tree,
the variable :math:`x_j` with lowest fractionality :math:`f(x_j)` with respect to the current relaxation solution is bound
to the closest integer value :math:`[x_j]`. This is done as follows:

.. math::
        \textbf{if} \quad x_j - \lfloor x_j \rfloor \le \lceil x_j \rceil - x_j\\
        \textbf{then} \quad upper\_bound(x_j) \leftarrow \lfloor x_j \rfloor\\
        \textbf{else} \quad lower\_bound(x_j) \leftarrow \lceil x_j \rceil

The traversal is discontinued if any relaxation is infeasible or a feasible integer solution is found.

Line Search Diving
------------------

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