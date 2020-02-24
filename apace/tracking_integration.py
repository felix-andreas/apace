import math
import numpy as np
from .classes import Drift, Dipole, Quadrupole, Sextupole


def runge_kutta_4(y0, t, h, element):
    k1 = h * y_prime(y0, t, element)
    k2 = h * y_prime(y0 + k1 / 2, t + h / 2, element)
    k3 = h * y_prime(y0 + k2 / 2, t + h / 2, element)
    k4 = h * y_prime(y0 + k3, t + h, element)
    return t + h, y0 + (k1 + 2 * k2 + 2 * k3 + k4) / 6


def y_prime(y, t, element):
    out = np.zeros(y.shape)
    out[0] = np.copy(y[1])
    out[2] = np.copy(y[3])
    if isinstance(element, Drift):
        out[1] = 0
        out[3] = 0
    elif isinstance(element, Dipole):
        out[1] = -element.k0 / (1 + y[5])
        out[3] = 0
        h = 1 + element.k0 * y[0]
        out[1] *= h ** 2
        out[1] += h * element.k0
        out[3] *= h ** 2
    elif isinstance(element, Quadrupole):
        out[1] = -element.k1 * y[0] / (1 + y[5])
        out[3] = element.k1 * y[2] / (1 + y[5])
    elif isinstance(element, Sextupole):
        out[1] = -element.k2 * (y[0] ** 2 - y[2] ** 2) / (1 + y[5])
        out[3] = 2 * element.k2 * y[0] * y[2] / (1 + y[5])
    else:
        raise Exception(f"Unsupported type {type(element)}.")

    return out


# TODO: this is still experimental and not well tested!!!
class Tracking:
    def __init__(self, lattice):
        self.lattice = lattice

    def track(self, initial_distribution, step_size=0.01):
        n_steps = math.ceil(self.lattice.length / step_size) + 10
        n_particles = initial_distribution.shape[1]
        s = np.empty(n_steps)
        s[0] = 0
        trajectory = np.empty((n_steps, 6, n_particles))
        trajectory[0] = initial_distribution

        end = 0
        i = 0
        for element in self.lattice.arrangement:
            end += element.length
            while s[i] < end:
                step_size_arg = min(step_size, end - s[0])
                s[i + 1], trajectory[i + 1] = runge_kutta_4(
                    trajectory[i], s[i], step_size_arg, element
                )
                i += 1
        return s[: i + 1], trajectory[: i + 1]
