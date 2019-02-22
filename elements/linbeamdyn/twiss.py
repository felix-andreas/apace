import warnings

import numpy as np
from ..clib import accumulate_array, twissparameter_parallel, twissparameter

matrix_size = 5


def twissdata(twiss, transfer_matrices, interpolate=None):
    acc_array = np.empty(transfer_matrices.shape)
    accumulate_array(transfer_matrices, acc_array)
    fullmatrix = acc_array[-1]

    tmp_x = 2 - fullmatrix[0, 0] ** 2 - 2 * fullmatrix[0, 1] * fullmatrix[1, 0] - fullmatrix[1, 1] ** 2
    twiss.stable_x = tmp_x > 0

    tmp_y = 2 - fullmatrix[2, 2] ** 2 - 2 * fullmatrix[2, 3] * fullmatrix[3, 2] - fullmatrix[3, 3] ** 2
    twiss.stable_y = tmp_y > 0
    twiss.stable = twiss.stable_x and twiss.stable_y

    if not twiss.stable:
        ...
        # warnings.warn(f"Horizontal plane stability: {twiss.stable_x}\nVertical plane stability{twiss.stable_y}")
    else:
        x_b0 = np.abs(2 * fullmatrix[0, 1]) / np.sqrt(tmp_x)
        x_a0 = (fullmatrix[0, 0] - fullmatrix[1, 1]) / (2 * fullmatrix[0, 1]) * x_b0
        x_g0 = (1 + x_a0 ** 2) / x_b0
        y_b0 = np.abs(2 * fullmatrix[2, 3]) / np.sqrt(tmp_y)
        y_a0 = (fullmatrix[2, 2] - fullmatrix[3, 3]) / (2 * fullmatrix[2, 3]) * y_b0
        y_g0 = (1 + y_a0 ** 2) / y_b0
        d0ds = (fullmatrix[1, 0] * fullmatrix[0, 4] + fullmatrix[1, 4] * (1 - fullmatrix[0, 0])) / (2 - fullmatrix[0, 0] - fullmatrix[1, 1])
        d0 = (fullmatrix[0, 1] * d0ds + fullmatrix[0, 4]) / (1 - fullmatrix[1, 1])

        # beta, alpha, gamma
        B0vec = np.array([x_b0, y_b0, x_a0, y_a0, x_g0, y_g0, d0, d0ds])
        twissarray = np.empty((B0vec.size, acc_array.shape[0]))
        twiss.twissarray = twissarray
        twiss.betax = twissarray[0]  # betax
        twiss.betay = twissarray[1]  # betay
        twiss.alphax = twissarray[2]  # alphax
        twiss.alphay = twissarray[3]  # alphay
        twiss.gammax = twissarray[4]  # gammax
        twiss.gammay = twissarray[5]  # gammay
        twiss.etax = twissarray[6]  # gammay
        twiss.ddsetax = twissarray[7]  # gammay
        twissparameter(acc_array, B0vec, twissarray)

        if interpolate:
            twiss.s_int = np.linspace(0, twiss.s[-1], interpolate)
            twiss.betax_int = np.interp(twiss.s_int, twiss.s, twiss.betax)
            twiss.betay_int = np.interp(twiss.s_int, twiss.s, twiss.betay)
