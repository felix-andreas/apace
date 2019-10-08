import numpy as np


def tracking(lin_beam_dyn, initial_distribution, turns):
    pass


from enum import Enum


class Distribution(Enum):
    DIRAC = 0
    UNIFORM = 1
    GAUSS = 2


class ParticleDistribution:
    def __init__(
            self,
            n_particles,
            x=None,
            x_width=None,
            y=None,
            y_width=None,
            x_dds=None,
            x_dds_width=None,
            y_dds=None,
            y_dds_width=None,
            delta=None,
            delta_width=None,
    ):
        self.n_particles = n_particles
        particle_distribution = np.zeros(6, n_particles)
        if x:
            particle_distribution[0] = self.create_distribution('uniform', None, None) # TODO: change

    def create_distribution(self, name, center, width):
        if name == 'uniform':
            tmp = width / 2
            return np.linspace(center - tmp, center + tmp)
