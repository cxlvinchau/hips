import numpy as np
from hips.models import HIPSArray
# Define global constants

REL_TOLERANCE = 1e-05
ABS_TOLERANCE = 1e-08


def set_tolerance(rel_tolerance=1e-09, abs_tolerance=0.0):
    """
    Sets the relative or absolute tolerance with which float comparison are done in HIPS.

    :param rel_tolerance: The relative tolerance, by default 1e-09
    :param abs_tolerance: The absolute tolerance, by default 1e-04
    :return: None
    """
    global REL_TOLERANCE, ABS_TOLERANCE
    REL_TOLERANCE = rel_tolerance
    ABS_TOLERANCE = abs_tolerance


def is_close(a, b):
    if isinstance(a, HIPSArray):
        a = a.to_numpy()
    if isinstance(b, HIPSArray):
        b = b.to_numpy()
    return np.isclose(a, b, rtol=REL_TOLERANCE, atol=ABS_TOLERANCE)
