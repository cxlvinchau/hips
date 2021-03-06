Developer Documentation
=======================
On this page, we elaborate on the concepts of HIPS and how to extend the existing functionality. Further, we explain how
HIPS can be tested and how the documentation can be updated and built.

Below the core structure of HIPS is depicted in the UML diagram.

.. image:: img/hips-uml.png

The ``solver`` package contains the linear programming solvers and can easily be extended.

The ``models`` package contains the :class:`hips.models.LPModel` and
:class:`hips.models.MIPModel` classes and interacts with the ``solver`` package. The :class:`hips.models.LPModel` class has a connection to a solver.
Under the hood, whenever the linear program represented by :class:`hips.models.LPModel` is changed, the changes are
directly redirected to the concrete solver. This means that the concrete solver (Gurobi or Clp) is constantly updated and
warm starts of the solvers are supported.

Lastly, the ``heuristics`` package contains the different heuristic implementations.

In the following sections we explain how to apply changes in the respective packages.

``solver`` package
------------------
The ``solver`` package contains the different linear programming solvers supported by HIPS.
Currently, :class:`hips.solver.GurobiSolver` and :class:`hips.solver.ClpSolver` are supported.
These classes inherit from the abstract class :class:`hips.solver._abstract_solver.AbstractSolver` and need to
implement various methods.

Adding a new solver
___________________
A new solver can be added by creating a class that inherits from :class:`hips.solver._abstract_solver.AbstractSolver`
and implements the different abstract methods. Please have a look at the documentation of the class below for details.

.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:

   hips.solver._abstract_solver.AbstractSolver

``models`` package
------------------
The ``models`` package contains all necessary classes to express linear and mixed integer programs in HIPS. As mentioned
before, the :class:`hips.models.LPModel` uses the solver interface to update the underlying linear program. Therefore, this
has to be kept in mind when applying changes to the ``models`` package.

``heuristics`` package
----------------------
The heuristics package contains the different heuristic implementations. Particularly, the two abstract classes :class:`hips.heuristics._heuristic.Heuristic`
and :class:`hips.heuristics._abstract_diving.AbstractDiving` are relevant when adding new heuristics.

Adding general MIP heuristics
_____________________________
A new heuristic can be added by inheriting from the :class:`hips.heuristics._heuristic.Heuristic` class. The class has
various abstract methods that need to implemented in the child class. Of particular interest is the
:func:`hips.heuristics._heuristic.Heuristic.compute` method that needs to implement the computation of the heuristic.
Please have a look at the documentation of the class for details.


Adding diving heuristics
________________________
When implementing new diving heuristics, it might be more appropriate to inherit from the
:class:`hips.heuristics._abstract_diving.AbstractDiving` class and implement the abstract methods there.
Particularly, only the :func:`hips.heuristics._abstract_diving.AbstractDiving.dive` and
:func:`hips.heuristics._abstract_diving.AbstractDiving.revert` methods need to be overriden.

The *dive* method should be overridden to follow the specific branching condition of the diving heuristic to be implemented.
This means :func:`adding <hips.models._mip_model.MIPModel.add_constraint>` either a new constraint or
:func:`setting <hips.models._lp_model.LPModel.set_variable_bound>` the bound of a variable to restrict the feasible region
to the corresponding subproblem.

The *revert* method should be implemented to revert the MIP model to the state before any diving has happened. This method will
be called at the end of a diving heuristic run, independent of the outcome. This behaviour is vital in case the heuristic is
used during the computations of another heuristic.


.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:

   hips.heuristics._abstract_diving.AbstractDiving
   hips.heuristics._heuristic.Heuristic


Testing
-------
We have introduced two different types of tests for HIPS, `unit` and `integration` tests. The unit tests, as the name
suggests, test various units of HIPS in a separate way. They are located in ``tests/unit``. The integration tests test
the interplay between the different components of HIPS, particularly the integration tests cover the testing of the heuristics.
The integration tests are located in ``tests/integration``.

To run the tests, navigate into ``src`` and then run

.. code-block::

    python -m unittest discover -s ../tests/unit

to run the unit tests or

.. code-block::

    python -m unittest discover -s ../tests/integration

to run the integration tests.

.. note::
    Commits on the main branch trigger a `GitHub action <https://github.com/cxlvinchau/hips/actions/workflows/test.yml>`_ that automatically
    runs the unit and integration tests.


The Sphinx documentation
------------------------
It is good practice to document the code of a project and provide explanations on how to use it. The documentation of HIPS
is generated with `Sphinx <https://www.sphinx-doc.org/en/master/>`_. Please familiarize yourself with Sphinx before working
on the documentation.

Setup
_____
The documentation is located in the ``docs`` folder. To work with the documentation, you need to install the requirements listed
in ``docs/requirements.txt``. Please have a look at `Sphinx extensions <https://www.sphinx-doc.org/en/master/usage/extensions/index.html>`_
for more details.

Building the documentation
__________________________
Navigate into the ``docs`` folder and run

.. code-block::

    make html

or

.. code-block::

    make clean html

to ensure that the documentation is completely rebuilt. The built documentation can then be found in ``docs/_build/html``.

Editing the documentation
_________________________
The documentation itself is written in `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_
markup language. This also means that the docstrings have to adhere to this format.

.. note::
    Commits on the main branch trigger a `GitHub action <https://github.com/cxlvinchau/hips/actions/workflows/main.yml>`_ that automatically
    builds and deploys the documentation. Particularly, this means that there is no need to setup Sphinx locally, although
    it is generally recommended.