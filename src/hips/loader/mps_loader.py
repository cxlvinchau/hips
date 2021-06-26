import math
import re
import os

import timeit

import numpy
import numpy as np
import pysmps.smps_loader as loader
from hips.models._mip_model import MIPModel
from hips.models._lp_model import HIPSArray
from hips.constants import VarTypes, ProblemSense


def _bounds_set(path):
    bounds_defined = False
    with open(path, "r") as file:
        for line in file:
            line = re.split(" |\t", line)
            line = [x.strip() for x in line]
            line = list(filter(None, line))
            if line[0] == "BOUNDS":
                bounds_defined = True
                break
    return bounds_defined


def load_mps_primitive(mip_model: MIPModel, path):
    """
    Loads a MIP problem in MPS or COR format into the given mip_model, specified by either the absolute or relative path.
    This method only uses 1-dimensional variables to create the model.
    If the specified .mps file does not contain a 'BOUNDS' section, standard bounds x ∈ [0,inf) are set.
    Makes use of the library :py:`pysmps <pysmps.smps_loader.py>`.

    :param mip_model: The mip_model, in which the MIP problem should be loaded.
    :param path: The path to the .mps file. This can be either relative to the current working directory or absolute.
    :return: None
    """
    name, objective_name, row_names, col_names, col_types, types, c, A, rhs_names, rhs, bnd_names, bnd = loader.load_mps(
        path)
    # model variables
    n = len(col_names)
    x = []
    # Check if bounds were defined, as :func:`pysmps <pysmps.smps_loader.py.load_mps>` does not check for missing bounds definition
    bounds_defined = _bounds_set(path)
    lb_vec, ub_vec = [], []
    if not bounds_defined:
        lb_vec, ub_vec = np.zeros(n), np.repeat(math.inf, n)
    else:
        bnd_name = bnd_names[0]
        lb_vec, ub_vec = bnd[bnd_name]["LO"], bnd[bnd_name]["UP"]
    for i in range(n):
        lb, ub = lb_vec[i], ub_vec[i]
        var_type = VarTypes.CONTINUOUS if col_types[i] == 'continuous' else (
            VarTypes.BINARY if lb == 0 and ub == 1 else VarTypes.INTEGER)
        x += [mip_model.add_variable(name="x{}".format(i), var_type=var_type, lb=lb, ub=ub)]
    # objective function
    objective_function = sum([c_i * x_i for c_i, x_i in zip(c, x)])
    mip_model.set_objective(objective_function)
    # constraints
    b = rhs[rhs_names[0]] if len(rhs_names) > 0 else numpy.zeros(len(row_names))
    for row, row_index in [(A_row, row_index) for row_index, (A_row, type) in enumerate(zip(A, types)) if type == "E"]:
        curr_lhs = sum([a_i * x_i for a_i, x_i in zip(row, x) if a_i > 0 or a_i < 0])
        curr_constraint = curr_lhs == float(b[row_index])
        mip_model.add_constraint(constraint=curr_constraint)

    for row, row_index in [(A_row, row_index) for row_index, (A_row, type) in enumerate(zip(A, types)) if type == "G"]:
        curr_lhs = sum([a_i * x_i for a_i, x_i in zip(row, x) if a_i > 0 or a_i < 0])
        curr_constraint = curr_lhs >= float(b[row_index])
        mip_model.add_constraint(constraint=curr_constraint)

    for row, row_index in [(A_row, row_index) for row_index, (A_row, type) in enumerate(zip(A, types)) if type == "L"]:
        curr_lhs = sum([a_i * x_i for a_i, x_i in zip(row, x) if a_i > 0 or a_i < 0])
        curr_constraint = curr_lhs <= float(b[row_index])
        mip_model.add_constraint(constraint=curr_constraint)


def load_mps_advanced(mip_model: MIPModel, path):
    """
    Loads a MIP problem in MPS or COR format into the given mip_model, specified by either the absolute or relative path.
    This method uses multidimensional variables to create the model.
    If the specified .mps file does not contain a 'BOUNDS' section, standard bounds x ∈ [0,inf) are set.
    Makes use of the library :py:`pysmps <pysmps.smps_loader.py>`.

    :param mip_model: The mip_model, in which the MIP problem should be loaded.
    :param path: The path to the .mps file. This can be either relative to the current working directory or absolute.
    :return: None
    """
    name, objective_name, row_names, col_names, col_types, types, c, A, rhs_names, rhs, bnd_names, bnd = loader.load_mps(
        path)
    # model variables
    cont_indices = []
    int_indices = []
    bin_indices = []
    n = len(col_names)
    # Check if bounds were defined, as :func:`pysmps <pysmps.smps_loader.py.load_mps>` does not check for missing bounds definition
    bounds_defined = _bounds_set(path)
    lb_vec, ub_vec = [], []
    if not bounds_defined:
        lb_vec, ub_vec = np.zeros(n), np.repeat(math.inf, n)
    else:
        bnd_name = bnd_names[0]
        lb_vec, ub_vec = bnd[bnd_name]["LO"], bnd[bnd_name]["UP"]
    for i in range(n):
        lb, ub = lb_vec[i], ub_vec[i]
        if col_types[i] == 'continuous':
            cont_indices += [i]
        else:
            if lb == 0 and ub == 1:
                bin_indices += [i]
            else:
                int_indices += [i]
    empty = {"cont": True if len(cont_indices) == 0 else False, "int": True if len(int_indices) == 0 else False,
             "bin": True if len(bin_indices) == 0 else False}
    x_cont = mip_model.add_variable(name="cont", var_type=VarTypes.CONTINUOUS,
                                    lb=HIPSArray([lb_vec[i] for i in cont_indices]),
                                    ub=HIPSArray([ub_vec[i] for i in cont_indices]),
                                    dim=len(cont_indices)) if not empty["cont"] else None
    x_int = mip_model.add_variable(name="int", var_type=VarTypes.INTEGER,
                                   lb=HIPSArray([lb_vec[i] for i in int_indices]),
                                   ub=HIPSArray([ub_vec[i] for i in int_indices]),
                                   dim=len(int_indices)) if not empty["int"] else None
    x_bin = mip_model.add_variable(name="bin", var_type=VarTypes.BINARY, dim=len(bin_indices)) if not empty[
        "bin"] else None
    # objective function
    c_cont = HIPSArray(np.array([c[i] for i in cont_indices]))
    c_int = HIPSArray(np.array([c[i] for i in int_indices]))
    c_bin = HIPSArray(np.array([c[i] for i in bin_indices]))
    objective_function = sum([c_cont * x_cont if not empty["cont"] else 0, c_int * x_int if not empty["int"] else 0,
                              c_bin * x_bin if not empty["bin"] else 0])
    mip_model.set_objective(objective=objective_function)
    # constraints
    b = rhs[rhs_names[0]] if len(rhs_names) > 0 else numpy.zeros(len(row_names))
    A_E = np.array([A[i] for i, typestr in enumerate(types) if typestr == "E"])
    if not A_E.shape[0] == 0:
        b_E = HIPSArray(np.array([b[i] for i, typestr in enumerate(types) if typestr == "E"]))
        A_E_cont = HIPSArray(np.array([A_E[:, i] for i in cont_indices]).transpose())
        A_E_int = HIPSArray(np.array([A_E[:, i] for i in int_indices]).transpose())
        A_E_bin = HIPSArray(np.array([A_E[:, i] for i in bin_indices]).transpose())
        lhs_E = sum([A_E_cont * x_cont if not empty["cont"] else 0, A_E_int * x_int if not empty["int"] else 0,
                     A_E_bin * x_bin if not empty["bin"] else 0])
        constraint_E = lhs_E == b_E
        mip_model.add_constraint(constraint=constraint_E)

    A_G = np.array([A[i] for i, typestr in enumerate(types) if typestr == "G"])
    if not A_G.shape[0] == 0:
        b_G = HIPSArray(np.array([b[i] for i, typestr in enumerate(types) if typestr == "G"]))
        A_G_cont = HIPSArray(np.array([A_G[:, i] for i in cont_indices]).transpose())
        A_G_int = HIPSArray(np.array([A_G[:, i] for i in int_indices]).transpose())
        A_G_bin = HIPSArray(np.array([A_G[:, i] for i in bin_indices]).transpose())
        lhs_G = sum([A_G_cont * x_cont if not empty["cont"] else 0, A_G_int * x_int if not empty["int"] else 0,
                     A_G_bin * x_bin if not empty["bin"] else 0])
        constraint_G = lhs_G >= b_G
        mip_model.add_constraint(constraint=constraint_G)

    A_L = np.array([A[i] for i, typestr in enumerate(types) if typestr == "L"])
    if not A_L.shape[0] == 0:
        b_L = HIPSArray(np.array([b[i] for i, typestr in enumerate(types) if typestr == "L"]))
        A_L_cont = HIPSArray(np.array([A_L[:, i] for i in cont_indices]).transpose())
        A_L_int = HIPSArray(np.array([A_L[:, i] for i in int_indices]).transpose())
        A_L_bin = HIPSArray(np.array([A_L[:, i] for i in bin_indices]).transpose())
        lhs_L = sum([A_L_cont * x_cont if not empty["cont"] else 0, A_L_int * x_int if not empty["int"] else 0,
                     A_L_bin * x_bin if not empty["bin"] else 0])
        constraint_L = lhs_L <= b_L
        mip_model.add_constraint(constraint=constraint_L)
