import numpy as np
from enum import Enum
from .classes import LinBeamDyn


def tracking(lin : LinBeamDyn, initial_distribution, turns, position=0):
    n_kicks = lin.main_cell.n_kicks
    n = turns if position else turns * n_kicks
    result = np.empty((n, *initial_distribution.shape))
    transfer_matrices = lin.transfer_matrices
    if position == 0:
        for i in range(turns):
            result[i] = np.dot(transfer_matrices[0], initial_distribution)
    elif position is None: # calc for all positions
        result[0:n_kicks] = np.dot(transfer_matrices, initial_distribution)
        for i in range(1, turns):
            result[i:i+n_kicks] = np.dot(transfer_matrices, result[i - 1])


class Distribution(Enum):
    DIRAC = 0
    UNIFORM = 1
    GAUSS = 2


def create_particle_distribution(
        n_particles,
        x=None,
        x_center=0,
        x_width=0,
        y=None,
        y_center=0,
        y_width=0,
        x_dds=None,
        x_dds_center=0,
        x_dds_width=0,
        y_dds=None,
        y_dds_center=0,
        y_dds_width=0,
        l=None,
        l_center=0,
        l_width=0,
        delta=None,
        delta_center=0,
        delta_width=None,
):
    n_particles = n_particles
    particle_distribution = np.zeros((6, n_particles))
    particle_distribution[0] = _create_distribution(x, x_center, x_width)
    particle_distribution[1] = _create_distribution(y, y_center, y_width)
    particle_distribution[2] = _create_distribution(x_dds, x_dds_center, x_dds_width)
    particle_distribution[3] = _create_distribution(y_dds, y_dds_center, y_dds_width)
    particle_distribution[4] = _create_distribution(l, l_center, l_width)
    particle_distribution[5] = _create_distribution(delta, delta_center, delta_width)
    return particle_distribution


def _create_distribution(distribution, center, width):
    if distribution == None:
        pass
    elif distribution == 'uniform':
        tmp = width / 2
        return np.linspace(center - tmp, center + tmp)
    else:
        raise NotImplementedError
