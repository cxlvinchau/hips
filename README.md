# HIPS
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Documentation](https://github.com/cxlvinchau/hips/actions/workflows/main.yml/badge.svg)](https://cxlvinchau.github.io/hips) [![Test](https://github.com/cxlvinchau/hips/actions/workflows/test.yml/badge.svg)](https://github.com/cxlvinchau/hips/actions/workflows/test.yml) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cxlvinchau/hips-examples/blob/main/notebooks/mip-example.ipynb)


HIPS is a Python library for heuristically solving mixed integer programs. At its core, HIPS implements various well-established heuristics for mixed-integer programming, e.g. the feasibility pump [[FGL05]](file:///home/calvin/Repositories/hips/docs/_build/html/references.html#id4), RENS [[Ber13]](file:///home/calvin/Repositories/hips/docs/_build/html/references.html#id6) and various diving heuristics. Further, HIPS implements wrappers for popular linear programming solvers like Gurobi [[GurobiOptimizationLLC21]](file:///home/calvin/Repositories/hips/docs/_build/html/references.html#id9) and Clp [[jVR+20]](file:///home/calvin/Repositories/hips/docs/_build/html/references.html#id8), and thereby allows for easily switching solvers.

HIPS is designed to be easily extensible and user-friendly. Adding new heuristics or solvers can be done by implementing the corresponding interfaces.

If you are not familiar with linear or mixed-integer programming, consider reading this and this Wikipedia article.

## Authors
Severin Bals (Technical University of Munich) and Calvin Chau (Technical University of Munich)
