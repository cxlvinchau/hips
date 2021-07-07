Feasibility Pump
================

The **Feasibility Pump**, proposed in 2005 by Fischetti et al. :cite:`Fischetti2005`, aims to compute
a feasible solution to an MIP without the need for an initial solution. The heuristic is an integral part of HIPS
and has significantly influenced and inspired the implementation of this library. The heuristic is also described in :cite:`2006:berthold`.

Assume we have the following general MIP:

.. math::
    \begin{array}{lr@{}l@{}l@{}l}
    \text{minimize }   & c^T x  \\
    \text{subject to } & Ax \le b \\
                        & x_j \in \mathbb{Z}\text{, } \forall j \in I
    \end{array}

We define the rounding :math:`\tilde{x}` of a variable :math:`x` as:

.. math::
    \tilde{x}_j = \begin{cases} [x_j], & j \in I\\ x_j, & \text{otherwise} \end{cases}

Note that :math:`[ \cdot ]` denotes the rounding to nearest integer. Then, we search the point :math:`{x\text{*}}`, the solution to the following LP:

.. math::
    \begin{array}{lr@{}l@{}l@{}l}
    \text{minimize }   & \Delta (x, \tilde{x})  \\
    \text{subject to } & Ax \le b,
    \end{array}

where :math:`\Delta` is defined as the :math:`L_1`-Norm:

.. math::
    \Delta(x, \tilde{x}) = \sum_{j \in I} | x_j - \tilde{x}_j |

With the terminology introduced, we can now generate two sequences which are the core of the **Feasibility Pump**.
We iteratively compute LP feasible points :math:`\bar{x}` and round it to the respective integer feasible points
:math:`\tilde{x}`. Subsequent points :math:`\bar{x}` are computed by finding the LP feasible point :math:`{x\text{*}}` (computed as above)
, which minimizes the distance from :math:`\tilde{x}` to the feasible region of the relaxation.
If a point :math:`\bar{x}` is feasible to the original MIP, we stop the computation and have found an integer feasible solution.

This computation sequence is expressed by the following pseudo-algorithmic schema.

.. image:: ../img/pseudo_algorithm_fs.png

Obviously a big difficulty of the **Feasibility Pump** is the chance of entering cylces, when reaching the same :math:`\tilde{x}`
twice. This means that the algorithm gets stuck and will never acquire as feasible solution. The easiest way to deal with this problem
is to perturb some of the integer variables in cases a cylce is detected.
The implementation in the :class:`Feasibility Pump<hips.heuristics._feasibility_pump.FeasibilityPump>` maintains two types
of cylce detection. The perturbation actions follow the rules described by Fischetti et al. :cite:`Fischetti2005`.

In case we reach a cycle of length 1 (i.e. :math:`\tilde{x}^{(i)}` = :math:`\tilde{x}^{(i+1)}`) in the algorithm, the
T binary variables of the current integer solution :math:`\tilde{x}` with highest distance :math:`|{x\text{*}}_j - \tilde{x}_j|` are flipped for the calculation of the next
:math:`\bar{x}`. The number T of variables to flip is uniformly chosen from the range :math:`( \lfloor \frac{t}{2} \rfloor , \lfloor 1.5t \rfloor )`.
The parameter :math:`t` can be specified when initializing the **Feasibility Pump**. By default :math:`t` will be assigned with :math:`\lceil \frac{n}{2} \rceil`,
with :math:`n` the number of binary variables in the model.

In case a cycle of length :math:`1 < l \le 3` is detected, we uniformly choose a value :math:`{\rho}_j \in [-0.3, 0.7]` for
each binary variable :math:`x_j` with :math:`j \in I`. We then decide for each of those variables to flip the corresponding :math:`\tilde{x}_j`
if :math:`|{x\text{*}}_j - \tilde{x}_j| + max(0, {\rho}_j) > 0.5`.

To find a high quality solution, the implementation offers the possibility to add a constraint
that ensures that the original objective function is still considered. The parameter :math:`\alpha` can be set on initialization
of the **Feasibility Pump** as a value between 0 and 1, corresponding to how much we take the original objective function into consideration.
The higher the :math:`\alpha`, the more we optimize towards the original objective.

Example 1
---------

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/feasibility_pump_10_teams_example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

In the example below, we consider the `10 teams <https://miplib.zib.de/instance_details_10teams.html>`_ problem from MIPLIB 2017 :cite:`miplib2017`.
A more detailed version of the example can be found on Google Colab.

.. code-block:: python

    from hips import load_problem
    from hips.heuristics._feasibility_pump import FeasibilityPump

    # Load the model
    mip_model = load_problem("10teams")
    # Create the Feasibility Pump
    heur = FeasibilityPump(mip_model, t=15)
    heur.compute(max_iter=1000)
    # Inspect the solution
    print("Status: {}".format(heur.get_status()))
    print("Found solution: {}".format(heur.get_objective_value()))
    heur.tracker.plot("feasibility objective")

The figure below depicts the feasibility objective during a single run of the feasibility pump. Recall that the objective
in the feasibility pump corresponds to the L1 distance between the LP solution and the rounded solution.

.. image:: ../img/fp-objective.png

Observe that the objective value decreases and suddenly increases after the 400th iteration. This indicates that the feasibility
pump got stuck and perturbed the values to resolve the cycle. Consequently, the objective value is suddenly increased.

Example 2
---------

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/feasibility_pump_22433_example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

Now we consider another problem, namely the `22433 <https://miplib.zib.de/instance_details_22433.html>`_ problem from MIPLIB 2017 :cite:`miplib2017`.

.. code-block:: python

    from hips import load_problem
    from hips.heuristics._feasibility_pump import FeasibilityPump

    # Load the model
    mip_model = load_problem("22433")
    # Create the Feasibility Pump
    heur = FeasibilityPump(mip_model, t=15)
    heur.compute(max_iter=1000)
    # Inspect the solution
    print("Status: {}".format(heur.get_status()))
    print("Found solution: {}".format(heur.get_objective_value()))
    heur.tracker.plot("feasibility objective")