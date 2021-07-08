.. currentmodule:: hips

API Documentation
=================
On this page we document the user API of HIPS. Each section is dedicated to one subpackage of HIPS and contains links to detailed
descriptions of the different classes in these packages.

Models
______
The ``models`` subpackage contains the different classes to model the linear and mixed-integer programs.

.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:


   hips.models.LPModel
   hips.models.MIPModel
   hips.models.HIPSArray
   hips.models.Variable
   hips.models.LinExpr
   hips.models.Constraint


Solver
______
The ``solver`` subpackage contains the different linear programming solvers and a naive branch and bound solver.

.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:

   hips.solver.GurobiSolver
   hips.solver.ClpSolver
   hips.solver.BranchAndBound


Heuristics
__________
The ``heuristics`` subpackage contains the different heuristics to solve mixed-integer programs.

.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:

   hips.heuristics.FeasibilityPump
   hips.heuristics.TwoStageFeasibilityPump
   hips.heuristics.HeuristicBounds
   hips.heuristics.AbstractDiving
   hips.heuristics.FractionalDiving
   hips.heuristics.LineSearchDiving
   hips.heuristics.RENS
   hips.heuristics.SimpleRounding


Constants
_________
The ``constants`` subpackage contains the different enums/constants in HIPS.

.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:

   hips.ProblemSense
   hips.LPStatus
   hips.Comparator
   hips.VarTypes
   hips.VariableBound
   hips.HeuristicStatus
   hips.BoundDirection


Loader
______
HIPS makes it easy to load MPS files and even comes with example problems to get started quickly.

.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:

   hips.loader.load_mps
   hips.loader.load_mps_primitive
   hips.load_problem

Tracker
_______
This class supports methods for logging intermediate values of the heuristics and plotting them as a line graph.

.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:

   hips.utils.Tracker

