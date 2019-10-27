import numpy as np
from .classes import LinBeamDyn

from ..clib.twiss_product import accumulate_array


def matrix_tracking(lin: LinBeamDyn, initial_distribution, turns, position=0):
    n_kicks = lin.main_cell.n_kicks
    n = turns if position is not None else turns * n_kicks
    result = np.empty((n, *initial_distribution.shape))
    transfer_matrices = lin.transfer_matrices
    if position == 0:
        acc_array = np.empty(transfer_matrices.shape)
        accumulate_array(transfer_matrices, acc_array)
        full_matrix = acc_array[-1]
        result[0] = initial_distribution
        for i in range(1, turns):
            result[i] = np.dot(full_matrix, result[i - 1])
    elif position is None:  # calc for all positions
        result[0:n_kicks] = np.dot(transfer_matrices, initial_distribution)
        for i in range(1, turns):
            result[i:i + n_kicks] = np.dot(transfer_matrices, result[i - 1])

    return result
