import os

import numpy as np
import pysmps.smps_loader as loader
from hips.models._mip_model import MIPModel
from hips.models._lp_model import LPModel
from hips.models._lp_model import Variable
from hips.models._lp_model import HIPSArray
from hips.constants import VarTypes
from hips.solver import GurobiSolver


def load_mps(mip_model : MIPModel, abs_path=None, rel_path=None):
    """
    Loads a MIP problem in MPS or COR format into the given mip_model, specified by either the absolute or relative path.

    :param mip_model: The mip_model, in which the MIP problem should be loaded.
    :param abs_path: The absolute path to the .mps or .cor file.
    :param rel_path: The relative path to the .mps or .cor file starting in the examples/mps_files directory.
    :return: None
    """

    if abs_path is None:
        mps_examples_dir = os.path.abspath(os.path.join(os.getcwd(), '../..', 'examples/mps_files'))
        print(mps_examples_dir)
        abs_path = os.path.join(mps_examples_dir, rel_path)
    print(abs_path)
    if not os.path.isfile(abs_path):
        raise Exception("ILLEGAL FILEPATH: The specified file path does not point to an existing file.")
    file_ext = os.path.splitext(abs_path)[1]
    if file_ext not in ['.mps', '.cor']:
        raise Exception("ILLEGAL FILEEXTENSION: The specified file path does not point to an .mps or .cor file.")
    name, objective_name, row_names, col_names, col_types, types, c, A, rhs_names, rhs, bnd_names, bnd = loader.load_mps(abs_path)
    # model variables
    n = len(c)
    x = []
    bnd_name = bnd_names[0]
    lb_vec = bnd[bnd_name]["LO"]
    ub_vec = bnd[bnd_name]["UP"]
    for i in range(n):
        if i == 225:
            debug = 1
        # TODO watch out: pysmps specifies lb <= x < ub
        lb = lb_vec[i]
        ub = ub_vec[i]
        var_type = VarTypes.CONTINUOUS if col_types[i] == 'continuous' else (VarTypes.BINARY if lb == 0 and ub == 1 else VarTypes.INTEGER)
        x += [mip_model.add_variable(name="x{}".format(i), var_type=var_type, lb=lb, ub=ub)]
    # objective function
    objective_function = sum([c_i*x_i for c_i,x_i in zip(c,x)])
    mip_model.set_objective(objective_function)
    # constraints
    rhs_name = rhs_names[0]
    b = rhs[rhs_name]
    for row, row_index in [(A_row, row_index) for row_index, (A_row,type) in enumerate(zip(A,types)) if type == "E"]:
        curr_lhs = sum([a_i*x_i for a_i,x_i in zip(row,x) if a_i>0 or a_i<0])
        curr_constraint = curr_lhs == float(b[row_index])
        mip_model.add_constraint(constraint=curr_constraint)

    row_index=0
    for row, row_index in [(A_row, row_index) for row_index, (A_row,type) in enumerate(zip(A,types)) if type == "G"]:
        curr_lhs = sum([a_i*x_i for a_i,x_i in zip(row,x) if a_i>0 or a_i<0])
        curr_constraint = curr_lhs >= float(b[row_index])
        mip_model.add_constraint(constraint=curr_constraint)

    row_index=0
    for row, row_index in [(A_row, row_index) for row_index, (A_row,type) in enumerate(zip(A,types)) if type == "L"]:
        curr_lhs = sum([a_i*x_i for a_i,x_i in zip(row,x) if a_i>0 or a_i<0])
        curr_constraint = curr_lhs <= float(b[row_index])
        mip_model.add_constraint(constraint=curr_constraint)

    print(mip_model)
    print("Constraints: " + str(len(mip_model.lp_model.constraints)))
    print("Variables: " + str(len(mip_model.lp_model.vars)))

if __name__ == "__main__":
    mip_model = MIPModel(GurobiSolver())
    load_mps(mip_model, rel_path="10teams.mps")