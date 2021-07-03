Diving Heuristics
=================

The following heuristics are so called **Diving Heuristics**. The general idea of **Diving Heuristics** is to quickly
depth first traverse the *branch\&bound* tree to reach one of its leave nodes. This quick traversal down the tree lead to
the term **diving**. At each node of the tree the heuristic decides on which variable to branch based on some promising
intuition. The specific branching condition depends on the type of heuristic.

A **Diving Heuristic** will stop in two cases:
\begin{enumerate}
    \item The current LP relaxation is infeasible
    \item The iteration limit is reached\\
The first one is if the current LP relaxation gets infeasible. In this case,
the heuristic will be aborted and no MIP solution was found. The second case occurs if the heuristic exceed a predetermined
iteration limit. In this case the heuristic will yield the best found MIP solution, if any were found.
    \item The current LP relaxation solution is worse than the incumbent solution \\
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