.. _getting-started-label:

Getting Started
===============
On this page we show you how to get started with HIPS. We assume that you have successfully completed the setup and
installations as described in the previous chapter.

A simple linear program
-----------------------

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/simple-lp-example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

Defining the program
____________________
Let us start with defining a linear program in HIPS. First, we need to decide which solver we would like to use. In this
example we use the :class:`GurobiSolver <hips.solver.GurobiSolver>`, but any other supported solver also works. Under the
hood, HIPS adds variables and constraints directly to the concrete solver to increase efficiency.

Suppose we are given the following linear program:

.. math::
    \begin{array}{lr@{}c@{}r@{}l}
    \text{maximize }   & 2 x_1 + 4 x_2  \\
    \text{subject to } & x_1 + 2 x_2 \leq 20 \\
                       & 3 x_1 - x_2 \leq 10 \\
                       & x_1, x_2 \geq 0 \\
                       & x_1, x_2 \in \mathbb{R}
    \end{array}

In HIPS, we can express the program as follows.

.. code-block:: python

    from hips import ProblemSense
    from hips.solver import GurobiSolver
    from hips.models import LPModel

    # Create solver
    solver = GurobiSolver()
    # Create LP model
    model = LPModel(solver)
    # Create variables
    x_1, x_2 = model.add_variable("x_1", lb=0), model.add_variable("x_2", lb=0)
    # Set sense
    model.set_lp_sense(ProblemSense.MAX)
    # Set objective
    model.set_objective(2*x_1 + 4*x_2)
    # Add constraints
    model.add_constraint(x_1 + 2*x_2 <= 20)
    model.add_constraint(3*x_1 - x_2 <= 10)

As you can see, the definition of linear programs is straightforward. However, for larger linear programs, this might
be a little bit cumbersome. Particularly, when we have many variables. Therefore, HIPS supports high-dimensional variables.
Below you can see the same linear program expressed with a single 2 dimensional variable.

.. code-block:: python

    from hips import ProblemSense
    from hips.solver import GurobiSolver
    from hips.models import LPModel, HIPSArray

    # Create solver
    solver = GurobiSolver()
    # Create LP model
    model = LPModel(solver)
    # Create 2 dim. variable with lower bound 0
    x = model.add_variable("x", lb=0, dim=2)
    # Set sense
    model.set_lp_sense(ProblemSense.MAX)
    # Set objective
    model.set_objective(HIPSArray([2, 4]) * x)
    # Add constraint
    model.add_constraint(HIPSArray([[1, 2], [3, -1]]) * x <= HIPSArray([20, 10]))

Observe that we have additionally imported :class:`HIPSArray <hips.models.HIPSArray>` to work with the 2 dimensional variable.
In contrast to the code above, we essentially work with vectors/matrices containing the coefficients for the variables.

.. note::
    Due to vectorization, it is often more efficient to use high-dimensional variables. Particularly, the implemented solvers
    and heuristics strongly benefit from high-dimensional variables.

Optimizing the program
______________________
Now, let us optimize the program and output the objective value and values for the variables.

This is done as follows for the one-dimensional model:

.. code-block:: python

    # Optimize the program
    model.optimize()
    # Print the objective value
    print(f"Objective value: {model.get_objective_value()}")
    # Print the values of the variables
    print(f"x_1: {model.variable_solution(x_1)}")
    print(f"x_2: {model.variable_solution(x_2)}")

The following prints the values of the multi-dimensional model:

.. code-block:: python

    # Optimize the program
    model.optimize()
    # Print the objective value
    print(f"Objective value: {model.get_objective_value()}")
    # Print the values of the variables
    print(f"x: {model.variable_solution(x)}")


High-dimensional constraints
----------------------------

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/constraints-example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

As you have seen in the previous section, HIPS can work with matrices and vectors. In this section, we explain how to work
with high-dimensional constraints in more detail.

Generally, we can express high-dimensional constraints with multiple variables in HIPS, i.e. we can express constraints
of the following type:

.. math::

    A_1 x_1 + \dots + A_n x_n \ \mathrm{?} \ b

where :math:`b \in \mathbb{Q}^m`, :math:`\mathrm{?} \in \{\leq, =, \geq\}`, :math:`A_i \in \mathbb{Q}^{m \times d_i}` and
variable :math:`x_i` has dimension :math:`d_i`.

Consider the example below:

.. math::

    \begin{pmatrix}
    1 & 1 \\
    2 & 0
    \end{pmatrix}
    \begin{pmatrix}
    x_1 \\
    x_2
    \end{pmatrix} +
    \begin{pmatrix}
    1 & 2 & 3 \\
    1 & 0 & 1
    \end{pmatrix}
    \begin{pmatrix}
    y_1 \\
    y_2 \\
    y_3
    \end{pmatrix}
    \geq
    \begin{pmatrix}
    10 \\
    20
    \end{pmatrix}

The corresponding code in HIPS:

.. code-block:: python

    from hips.models import LPModel, HIPSArray
    from hips.solver import ClpSolver

    model = LPModel(ClpSolver())
    x, y = model.add_variable("x", dim=2), model.add_variable("y", dim=3)
    A = HIPSArray([[1, 1], [2, 0]])
    B = HIPSArray([[1, 2, 3], [1, 0, 1]])
    b = HIPSArray([10, 20])
    constr = A*x + B*y >= b


NumPy support
_____________
NumPy is the de facto standard library for scientific computing with multi-dimensional arrays and matrices in Python.
You can find more information about NumPy `here <https://numpy.org/>`_. HIPS supports the usage of NumPy arrays, because
:class:`HIPSArray <hips.models.HIPSArray>` is essentially a wrapper for NumPy arrays.

Thus, instead of passing lists to the constructor of :class:`hips.models.HIPSArray`, we can also pass ``numpy.ndarray`` objects.

>>> from hips.models import HIPSArray
>>> import numpy as np
>>> # Creating a 4x4 identity matrix
>>> HIPSArray(np.identity(4))
[[1. 0. 0. 0.]
 [0. 1. 0. 0.]
 [0. 0. 1. 0.]
 [0. 0. 0. 1.]]
>>> # Creating a 2x3 matrix with zeros
>>> HIPSArray(np.zeros((2, 3)))
[[0. 0. 0.]
 [0. 0. 0.]]
>>> # A simple numpy array
>>> HIPSArray(np.array([1, 2, 3]))
[1, 2, 3]

A simple mixed integer program
------------------------------

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/mip-example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

Now, let us consider a mixed-integer program. Particularly, we consider the linear program from above with an additional constraint.

.. math::
    \begin{array}{lr@{}c@{}r@{}l}
    \text{maximize }   & 2 x_1 + 4 x_2  \\
    \text{subject to } & x_1 + 2 x_2 \leq 20 \\
                       & 3 x_1 - x_2 \leq 10 \\
                       & x_1, x_2 \geq 0 \\
                       & \color{red} {x_1 \in \mathbb{Z}}, \color{black} x_2 \in \mathbb{R} \\
    \end{array}

Compared to the example above, we have introduced the constraint :math:`\color{red} {x_1 \in \mathbb{Z}}`. This means
that our program contains an integer and a real variable. Thus, it is no longer a linear program, but a mixed-integer program.

In HIPS we can write the problem as follows:

.. code-block:: python

    from hips.solver import ClpSolver
    from hips.models import MIPModel
    from hips import ProblemSense, VarTypes

    # Create solver
    solver = ClpSolver()
    # Create MIP model
    model = MIPModel(solver)
    # Create variables with lower bound 0
    x_1 = model.add_variable("x_1", lb=0, ub=20, var_type=VarTypes.INTEGER)
    x_2 = model.add_variable("x_2", lb=0)
    # Set sense
    model.set_mip_sense(ProblemSense.MAX)
    # Set objective
    model.set_objective(2*x_1 + 4*x_2)
    # Add constraints
    model.add_constraint(x_1 + 2*x_2 <= 20)
    model.add_constraint(3*x_1 - x_2 <= 10)

Here, we need to replace the :class:`LPModel <hips.models.LPModel>` with the :class:`MIPModel <hips.models.MIPModel>`.
In HIPS there is a separation between these two program types to emphasize that heuristics are only applied to mixed-integer programs.
In terms of defining the program, the two classes share many similarities and barely differ. Please refer to the API documentation for details.
However, in contrast, the :class:`MIPModel <hips.models.MIPModel>` has no ``optimize()`` method and needs heuristics or the branch and bound
solver for optimization.

Note that we have added an upper bound for variable ``x_1``. In HIPS it is necessary to add bounds to integer variables
because many heuristics explicitly require bounds. However, this does not actually impose a limitation, as also mentioned in
:cite:`Fischetti2005`, because an optimal solution to a solvable mixed-integer program has to be finite.

Solving the program using branch and bound
__________________________________________
As mentioned before, the :class:`MIPModel <hips.models.MIPModel>` class does not offer the possibility to directly optimize the program.
However, it is possible to use :class:`BranchAndBound <hips.solver.BranchAndBound>`, HIPS' branch and bound implementation, to
compute the optimal solution of the mixed-integer program. Please note that the class only implements a naive version of the
branch and bound algorithm and is thus not suitable for solving large problems.

In the following, we optimize the mixed-integer program from above. To this end, consider the code below.

.. code-block:: python

    from hips.solver import BranchAndBound

    bb = BranchAndBound(model)
    bb.optimize()

    # Print solution
    bb.get_incumbent()

    # Print objective value
    bb.get_incumbent_val()

Loading .mps files
-----------------

.. raw:: html

    <a href="https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/mps-example.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
    </a>

The previous sections introduced how to explicitly create an MIP model.
This approach is impractical for most real-life problems, since the number of variable and constraints in those models can
be very large. Therefore, HIPS provides utility functions to read models from MPS files.

MPS (Mathematical Programming System) is a file format for representing linear and mixed-integer problem and is a standard in most commercial and open-source
solvers. It is column-oriented which makes it rather difficult to read for humans. An elaborate explanation of the format and its various
header sections can be found in :cite:`the official Gurobi documentation<gurobi-mps>`. It should be noted, that the optimization
sense is not specifiable in the MPS format and, thus, has to be set manually after loading.

There are two utility functions implemented in HIPS for loading an MPS file into a :class:`MIPModel <hips.models.MIPModel>`.

The :func:`primitive loader<hips.loader.load_mps_primitive>` loads every variable of the MPS file specified
in the ``path`` parameter as a 1-dimensional variable. The specified ``path`` is concatenated with the current
working directory. This loader version can be used for easy understanding and debugging of the created model. However
the runtime of this loader suffers from computational inefficiency.

The second :func:`loader<hips.loader.load_mps>` loads the continuous, integer and binary variables as
multidimensional variables. This allows the underlying solvers to make use of vectorization. Therefore, this loader is
much more efficient than the primitive version.

We can use the MPS loader in HIPS as follows:

.. code-block:: python

    from hips.solver import ClpSolver
    from hips.models import MIPModel
    from hips.loader import load_mps
    from hips import ProblemSense

    # create an mip model with an underlying solver
    model = MIPModel(ClpSolver())
    # load the problem specified in the .mps file at the path parameter into our model
    load_mps(mip_model=model, path='path_to_mps/mps_file.mps')
    # set the optimization sense
    model.set_mip_sense(ProblemSense.MIN)

Solving the program using branch and bound
__________________________________________
As shown above, we run the following lines to optimize the loaded model with branch and bound algorithm.

.. code-block:: python

    from hips.solver import BranchAndBound

    bb = BranchAndBound(model)
    bb.optimize()

    # Print solution
    bb.get_incumbent()

    # Print objective value
    bb.get_incumbent_val()

Example mixed-integer programs from MIPLIB2017
----------------------------------------------
The MIPLIB2017 :cite:`miplib2017` is a collection of real-world mixed-integer programs. HIPS already comes with a selection
of problems from the collection to help you get started faster.

The following problems can be easily loaded:

- ``10teams`` (https://miplib.zib.de/instance_details_10teams.html)
- ``bppc8-02`` (http://miplib2017.zib.de/instance_details_bppc8-02.html)
- ``flugpl`` (http://miplib2017.zib.de/instance_details_flugpl.html)
- ``gen-ip054`` (https://miplib2017.zib.de/instance_details_gen-ip054.html)
- ``gr4x6`` (https://miplib.zib.de/instance_details_gr4x6.html)
- ``osorio-cta`` (http://miplib.zib.de/instance_details_osorio-cta.html)
- ``22433`` (https://miplib.zib.de/instance_details_22433.html)

We would like to thank the authors and people involved for their contribution and would like to emphasize that they are not linked to or involved in HIPS,
nor do they endorse HIPS. The examples are licensed under Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) (https://creativecommons.org/licenses/by-sa/4.0/).

In order to load a problem, we simply pass the problem name to :func:`hips.load_problem` and it automatically returns a :class:`MIPModel <hips.models.MIPModel>`
containing the problem. By default, the function tries to use the :class:`hips.solver.GurobiSolver`. If this fails, the :class:`hips.solver.ClpSolver` is used.
The code below loads the ``10teams`` problem.

.. code-block:: python

    from hips import load_problem

    mip_model = load_problem("10teams")