import warnings

import numpy as np
from scipy import integrate
from ..clib.twiss_product import twiss_product, accumulate_array

CONST_C = 299_792_458
TWO_PI = 2 * np.pi


def twiss_data(twiss, transfer_matrices, interpolate=None, betatron_phase=False):
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
        beta_x0 = np.abs(2 * full_matrix[0, 1]) / np.sqrt(tmp_x)
        alpha_x0 = (full_matrix[0, 0] - full_matrix[1, 1]) / (2 * full_matrix[0, 1]) * beta_x0
        gamma_x0 = (1 + alpha_x0 ** 2) / beta_x0
        beta_y0 = np.abs(2 * full_matrix[2, 3]) / np.sqrt(tmp_y)
        alpha_y0 = (full_matrix[2, 2] - full_matrix[3, 3]) / (2 * full_matrix[2, 3]) * beta_y0
        gamma_y0 = (1 + alpha_y0 ** 2) / beta_y0
        eta_x_dds0 = (full_matrix[1, 0] * full_matrix[0, 5] + full_matrix[1, 5] * (1 - full_matrix[0, 0])) / (
                2 - full_matrix[0, 0] - full_matrix[1, 1])
        eta_x0 = (full_matrix[0, 1] * eta_x_dds0 + full_matrix[0, 5]) / (1 - full_matrix[1, 1])

        # beta, alpha, gamma
        # TODO: make lazy evaluated!
        B0vec = np.array([beta_x0, beta_y0, alpha_x0, alpha_y0, gamma_x0, gamma_y0, eta_x0, eta_x_dds0])
        twiss_array = np.empty((B0vec.size, acc_array.shape[0]))
        twiss.twiss_array = twiss_array
        twiss.beta_x = twiss_array[0]
        twiss.beta_y = twiss_array[1]
        twiss.alpha_x = twiss_array[2]
        twiss.alpha_y = twiss_array[3]
        twiss.gamma_x = twiss_array[4]
        twiss.gamma_y = twiss_array[5]
        twiss.eta_x = twiss_array[6]
        twiss.eta_x_dds = twiss_array[7]
        twiss_product(acc_array, B0vec, twiss_array)

        if interpolate:  # TODO return interpolated instead of new values?? or different function! def twiss_interpolate
            twiss.s_int = np.linspace(0, twiss.s[-1], interpolate)
            twiss.beta_x_int = np.interp(twiss.s_int, twiss.s, twiss.beta_x)
            twiss.beta_y_int = np.interp(twiss.s_int, twiss.s, twiss.beta_y)

        if betatron_phase: # TODO: should this be its own function?
            twiss.psi_x = np.empty(acc_array.shape[0])
            twiss.psi_y = np.empty(acc_array.shape[0])
            beta_x_inverse = 1 / twiss.beta_x
            beta_y_inverse = 1 / twiss.beta_y
            # TODO: use faster integration!
            twiss.psi_x = integrate.cumtrapz(beta_x_inverse, twiss.s)
            twiss.psi_y = integrate.cumtrapz(beta_y_inverse, twiss.s)

            twiss.tune_x = twiss.psi_x[-1] / TWO_PI
            twiss.tune_y = twiss.psi_y[-1] / TWO_PI
            twiss.tune_x_fractional = np.arccos((full_matrix[0, 0] + full_matrix[1, 1]) / 2) / TWO_PI
            twiss.tune_y_fractional = np.arccos((full_matrix[2, 2] + full_matrix[3, 3]) / 2) / TWO_PI
            lattice_length = twiss.s[-1]
            tmp = CONST_C / lattice_length / 1000 # kHz
            twiss.tune_x_fractional_kHz = twiss.tune_x_fractional * tmp
            twiss.tune_y_fractional_kHz = twiss.tune_y_fractional * tmp
