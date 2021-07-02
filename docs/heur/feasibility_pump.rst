Feasibility Pump
================

The \textbf{Feasibility Pump} is the heuristic is responsible for the idea to this module and therefore the core
heuristic of HIPS. First proposed in 2005 by Fischetti et al. \cite{Fischetti2005}, the Feasibility Pump aims to compute
a feasible solution to an MIP without the need for an initial solution.

Assume we have the following general MIP:

.. math::
    \begin{array}{lr@{}c@{}r@{}l}
    \text{minimize }   & c^T x  \\
    \text{subject to } & Ax \le b \\
                        & x_j \in \mathbb{Z}\text{, } \forall j \in I
    \end{array}

We define the rounding :math:`\tilde{x}` of a variable :math:`x` as :

.. math::
    \tilde{x}_j = \begin{cases} [x_j], & j \in I\\ x_j, & \text{otherwise} \end{cases}

We search the point :math:`x*`, the solution to the following LP:

.. math::
    \begin{array}{lr@{}c@{}r@{}l}
    \text{minimize }   & \Delta (x, \tilde{x})  \\
    \text{subject to } & Ax \le b,
    \end{array}

where :math:`\Delta` is defined as the :math:`L_1`-Norm:

.. math::
    \Delta(x, \tilde{x}) = \sum_{j \in I} | x_j - \tilde{x}_j |

