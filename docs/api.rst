.. currentmodule:: hips

API Documentation
=================

Documentation of the API.


Models
______
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
.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:

   hips.solver.GurobiSolver
   hips.solver.ClpSolver


Heuristics
__________
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


Loader and Tracker
______
.. autosummary::
   :toctree: _autosummary
   :nosignatures:
   :recursive:

   hips.loader.mps_loader.load_mps
   hips.loader.mps_loader.load_mps_primitive
   hips.utils.Tracker