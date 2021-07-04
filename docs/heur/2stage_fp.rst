Two Stage Feasibility Pump
==========================
The **Two Stage Feasibility pump** proposed by :cite:p:`BERTACCO200763` is an extension of the **Feasibility Pump** :cite:p:`Fischetti2005` and can
be used to solve general mixed integer programs, i.e. programs containing binary and integer variables. In contrast, the original
feasibility pump is only designed for mixed integer programs containing binary variables only.

The basic idea of this feasibility pump is to handle binary and integer variables in two different stages. In the first stage,
the integer variables are ignored, i.e. treated as if they were continuous, and only the binary variables are considered.
The first stage is completed once a feasible solution w.r.t. the binary variables has been found or when the maximum iteration
has been reached. Afterwards, in the second stage, the integer variables are considered. Note that the original feasibility
pump can also handle integer variables, but might be less suited for this purpose.