Feasibility Pump
================

The **Feasibility Pump** is the heuristic is responsible for the idea to this module and therefore the core
heuristic of HIPS. First proposed in 2005 by Fischetti et al. :cite:`Fischetti2005`, the **Feasibility Pump** aims to compute
a feasible solution to an MIP without the need for an initial solution. The heuristic is also described in :cite:`2006:berthold`.

Assume we have the following general MIP:

.. math::
    \begin{array}{lr@{}l@{}l@{}l}
    \text{minimize }   & c^T x  \\
    \text{subject to } & Ax \le b \\
                        & x_j \in \mathbb{Z}\text{, } \forall j \in I
    \end{array}

We define the rounding :math:`\tilde{x}` of a variable :math:`x` as :

.. math::
    \tilde{x}_j = \begin{cases} [x_j], & j \in I\\ x_j, & \text{otherwise} \end{cases}

We search the point :math:`{x\text{*}}`, the solution to the following LP:

.. math::
    \begin{array}{lr@{}l@{}l@{}l}
    \text{minimize }   & \Delta (x, \tilde{x})  \\
    \text{subject to } & Ax \le b,
    \end{array}

where :math:`\Delta` is defined as the :math:`L_1`-Norm:

.. math::
    \Delta(x, \tilde{x}) = \sum_{j \in I} | x_j - \tilde{x}_j |

With the terminology introduced, we can now generate two sequences which are the core to the **Feasibility Pump**.
We iteratively compute LP feasible points :math:`\bar{x}` and round it to the respective integer feasible points
:math:`\tilde{x}`. Subsequent points :math:`\bar{x}` are computed by finding th LP feasible point :math:`{x\text{*}}` (computed as above)
, which minimizes the distance from :math:`\bar{x}` to the feasible region of the relaxation.
If any of the rounded points :math:`\tilde{x}` is feasible, we stop the computation and have found an integer feasible solution.

This computation sequence is expressed by the following pseudo-algorithmic schema.

.. code-block:: python

    x_bar = LP relaxation solution
    do
        x_tilde = [x_bar]
        x_bar = argmin{Delta(x, x_tilde), Ax <= b}
    while(x_tilde infeasible)

Obviously a big difficulty of the **Feasibility Pump** is the chance of entering cylces, when reaching the same :math:`\tilde{x}`
twice. This means that the algorithm gets stuck and will never acquire as feasible solution. The easiest way to deal with this problem
is to perturb some of the integer variables in cases a cylce is detected.
The implementation in the :class:`Feasibility Pump<hips.heuristics._feasibility_pump.FeasibilityPump>` maintains two types
of cylce detection. The perturbation actions follow the rules described by Fischetti et al. :cite:`Fischetti2005`.

In case we reach a cycle of length 1 (i.e. :math:`\tilde{x}^i` = :math:`\tilde{x}^{i+1}`) the algorithm, the
T binary variables of the current integer solution :math:`\tilde{x}` with highest distance :math:`|{x\text{*}}_j - \tilde{x}_j|` are flipped and fixed for the calculation of the next
:math:`\bar{x}`. The number T of variables to flip is uniformally chosen from the range :math:`( \lfloor \frac{t}{2} \rfloor , \lfloor 1.5t \rfloor )`.
The parameter :math:`t` can be specified when initializing the **Feasibility Pump**. By default :math:`t` will be assigned with :math:`\lceil \frac{n}{2} \rceil`,
with :math:`n` the number of binary variables in the model.

In case a cycle of length :math:`1 < l \le 3` is detected we uniformally chose a value :math:`{\rho}_j \in [-0.3, 0.7]` for
each binary variable :math:`x_j` with :math:`j \in I`. We then decide for each of those variables to flip the corresponding :math:`\tilde{x}_j`
if :math:`|{x\text{*}}_j - \tilde{x}_j| + max(0, {\rho}_j) > 0.5`.

To ensure that we do not only find any integer feasible solution, but a good one, the implementation addds a constraint,
that ensures that the original objective function is still regarded. The parameter :math:`\alpha` can be set on initialization
of the **Feasibility Pump** as a value between 0 and 1, denoting how much respect we pay to the original objective function.
The higher the :math:`\alpha`, the more we optimize towards the original objective.

