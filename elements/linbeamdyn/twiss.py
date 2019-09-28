import warnings

import numpy as np
from ..clib.twiss_product import twiss_product, accumulate_array

matrix_size = 5


def twiss_data(twiss, transfer_matrices, interpolate=None):
    acc_array = np.empty(transfer_matrices.shape)
    accumulate_array(transfer_matrices, acc_array)
    full_matrix = acc_array[-1]

    tmp_x = 2 - full_matrix[0, 0] ** 2 - 2 * full_matrix[0, 1] * full_matrix[1, 0] - full_matrix[1, 1] ** 2
    twiss.stable_x = tmp_x > 0

    tmp_y = 2 - full_matrix[2, 2] ** 2 - 2 * full_matrix[2, 3] * full_matrix[3, 2] - full_matrix[3, 3] ** 2
    twiss.stable_y = tmp_y > 0
    twiss.stable = twiss.stable_x and twiss.stable_y

    if not twiss.stable:
        ...
        # warnings.warn(f"Horizontal plane stability: {twiss.stable_x}\nVertical plane stability{twiss.stable_y}")
    else:
        x_b0 = np.abs(2 * full_matrix[0, 1]) / np.sqrt(tmp_x)
        x_a0 = (full_matrix[0, 0] - full_matrix[1, 1]) / (2 * full_matrix[0, 1]) * x_b0
        x_g0 = (1 + x_a0 ** 2) / x_b0
        y_b0 = np.abs(2 * full_matrix[2, 3]) / np.sqrt(tmp_y)
        y_a0 = (full_matrix[2, 2] - full_matrix[3, 3]) / (2 * full_matrix[2, 3]) * y_b0
        y_g0 = (1 + y_a0 ** 2) / y_b0
        d0ds = (full_matrix[1, 0] * full_matrix[0, 4] + full_matrix[1, 4] * (1 - full_matrix[0, 0])) / (
                    2 - full_matrix[0, 0] - full_matrix[1, 1])
        d0 = (full_matrix[0, 1] * d0ds + full_matrix[0, 4]) / (1 - full_matrix[1, 1])

        # beta, alpha, gamma
        # TODO: make lazy evaluated!
        B0vec = np.array([x_b0, y_b0, x_a0, y_a0, x_g0, y_g0, d0, d0ds])
        twiss_array = np.empty((B0vec.size, acc_array.shape[0]))
        twiss.twiss_array = twiss_array
        twiss.beta_x = twiss_array[0]  # beta_x
        twiss.beta_y = twiss_array[1]  # beta_y
        twiss.alpha_x = twiss_array[2]  # alpha_x
        twiss.alpha_y = twiss_array[3]  # alpha_y
        twiss.gamma_x = twiss_array[4]  # gamma_x
        twiss.gamma_y = twiss_array[5]  # gamma_y
        twiss.eta_x = twiss_array[6]  # gamma_y
        twiss.dds_eta_x = twiss_array[7]  # gamma_y
        twiss_product(acc_array, B0vec, twiss_array)

        if interpolate: # TODO return interploated instead of new values?? or different function! def twiss_interpolate
            twiss.s_int = np.linspace(0, twiss.s[-1], interpolate)
            twiss.beta_x_int = np.interp(twiss.s_int, twiss.s, twiss.beta_x)
            twiss.beta_y_int = np.interp(twiss.s_int, twiss.s, twiss.beta_y)
