.. HIPS documentation master file, created by
   sphinx-quickstart on Mon Apr  5 15:29:27 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

HIPS Documentation
==================
HIPS is a Python library for heuristically solving mixed integer programs. At its core, HIPS implements various
well-established heuristics for mixed-integer programming, e.g. the feasibility pump :cite:`Fischetti2005`, RENS :cite:`Berthold2013`
and various diving heuristics. Further, HIPS implements wrappers for popular linear programming solvers like Gurobi
:cite:`gurobi` and Clp :cite:`johnjforrest_2020_3748677`, and thereby allows for easily switching solvers.

HIPS is designed to be easily extensible and user-friendly. Adding new heuristics or solvers can be done by implementing
the corresponding interfaces.

The code for this project is on `GitHub <https://github.com/cxlvinchau/hips>`_. Feel free to discuss any open issues with us.

If you are not familiar with linear or mixed-integer programming, consider reading `this <https://en.wikipedia.org/wiki/Linear_programming>`_
and `this <https://en.wikipedia.org/wiki/Integer_programming>`_ Wikipedia article.

Google Colab
------------
Throughout the following pages, you can find `Google Colab <https://colab.research.google.com/notebooks/intro.ipynb?utm_source=scs-index>`_
badges that look like this:

.. raw:: html

    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>

These badges lead to code examples in Python notebooks that you can run and try out without any setup. In addition,
the examples on Google Colab are often more detailed and contain additional code. Thus, we strongly recommend the usage of Google
Colab.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   getting_started
   heuristics
   api
   dev_api
   references


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

Authors
=======
HIPS is developed and maintained by Severin Bals and `Calvin Chau <https://cxlvinchau.github.io/>`_ from the
`Department of Informatics <https://www.in.tum.de/en/cover-page/>`_ at the `Technical University of Munich <https://www.tum.de/en/>`_.
