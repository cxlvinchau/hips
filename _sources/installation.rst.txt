Installation and Requirements
=============================
In the following we describe how to setup an environment to work with HIPS. HIPS needs at least Python 3.8 to work properly.

1. Creating a virtual environment (optional)
--------------------------------------------
Typically, when working on different Python projects it is advisable to create
virtual environments to separate the dependencies of the different projects.
While this step is optional, we highly recommend setting up a virtual environment.
If virtual environments are not familiar to you, please consult the
`Python documentation <https://docs.python.org/3/tutorial/venv.html>`_ or
`Python Virtual Environments: A Primer <https://realpython.com/python-virtual-environments-a-primer/>`_.

First, we create a directory ``my_project`` where we would like to create
the virtual environment. Navigate into this directory, then run the following command:

.. code-block::

    python -m venv my_venv

The code above creates a virtual environment with the name ``my_venv`` in our project
directory. Afterwards, we have to activate the environment.

On Windows:

.. code-block::

    my_venv\Scripts\activate.bat

On Unix or MacOS:

.. code-block::

    source my_venv/bin/activate

Now we can install packages without affecting other dependencies in other projects.

2. Installing a solver
----------------------
HIPS supports two of the most popular solvers for linear programming,
`Gurobi <https://www.gurobi.com/>`_ :cite:`gurobi` and
`Clp <https://github.com/coin-or/Clp>`_ :cite:`johnjforrest_2020_3748677`.
Note that you do not need to install both solvers. The presence of one solver
is sufficient. Generally, we recommend the installation of both solvers though.

Installing Gurobi
_____________________
Gurobi is a commercial solver for linear programming but also quadratic programming,
mixed integer programming and more. However, within HIPS we only make use of
its linear programming capabilities. While the usage of Gurobi is generally not free,
academic licenses can be obtained `here <https://www.gurobi.com/academia/academic-program-and-licenses/>`_. Once you have
obtained a license you need to activate it. To this end, please follow the instructions on `Gurobi's website <https://support.gurobi.com/hc/en-us>`_.

Then, run the following line to install Gurobi.

.. code-block::

    pip install gurobipy

Installing CyLP
__________________
Clp is an open source solver for linear programming and licensed under the Eclipse Public License. It is part of the larger
open source `COIN-OR project <https://www.coin-or.org/>`_. To use Clp, we install its Python interface
`cylp <https://github.com/coin-or/CyLP>`_. Please follow the instructions in the *Prerequisites* section on the
`GitHub <https://github.com/coin-or/CyLP>`_ page.

Then, once the steps described in the *Prerequisites* are done, we can install cylp.

.. code-block::

    pip install cylp

**Troubleshooting:**
The installation of Clp can be quite cumbersome and might not be as smooth as the Gurobi installation because various
COIN-OR dependencies have to be installed.

- For Linux/Ubuntu users this `GitHub issue <https://github.com/coin-or/CyLP/issues/47#issuecomment-545120587>`_ might be helpful.
- You might need to install numpy before installing cylp. Simply run ``pip install numpy``.

3. Installing HIPS
-------------------
Finally, we can install HIPS. For the latest version of HIPS, we can simply install the version from the repository.

.. code-block::

    pip install https://github.com/cxlvinchau/hips/archive/master.zip


