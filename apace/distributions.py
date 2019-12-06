import numpy as np


def create_particle_distribution(
    n_particles,
    x_dist=None,
    x_center=0,
    x_width=0,
    y_dist=None,
    y_center=0,
    y_width=0,
    x_dds_dist=None,
    x_dds_center=0,
    x_dds_width=0,
    y_dds_dist=None,
    y_dds_center=0,
    y_dds_width=0,
    l_dist=None,
    l_center=0,
    l_width=0,
    delta_dist=None,
    delta_center=0,
    delta_width=None,
) -> np.ndarray:
    """Create a particle distribution.

    :param int n_particles: Number of particles.
    :param str x_dist: Type of distribution in horizontal phase space.
    :param float x_center: Center of distribution.
    :param float x_width: Width of distribution.
    :param str y_dist: Type of distribution in vertical phase space.
    :param float y_center: Center of distribution.
    :param float y_width: Width of distribution.
    :param str x_dds_dist: Type of distribution in horizontal slope phase space.
    :param float x_dds_center: Center of distribution.
    :param float x_dds_width: Width of distribution.
    :param str y_dds_dist: Type of distribution in vertical slope phase space.
    :param float y_dds_center: Center of distribution.
    :param float y_dds_width: Width of distribution.
    :param str l_dist: Type of distribution in longitudinal phase space.
    :param float l_center: Center of distribution.
    :param float l_width: Width of distribution.
    :param str delta_dist: Type of distribution in momentum phase space.
    :param float delta_center: Center of distribution.
    :param float delta_width: Width of distribution.
    :return: Array of shape (6, n_particles)
    :rtype: numpy.ndarray
    """
    n_particles = n_particles
    particle_distribution = np.zeros((6, n_particles))
    for i, (dist_type, center, width) in enumerate(
        (
            (x_dist, x_center, x_width),
            (x_dds_dist, x_dds_center, x_dds_width),
            (y_dist, y_center, y_width),
            (y_dds_dist, y_dds_center, y_dds_width),
            (l_dist, l_center, l_width),
            (delta_dist, delta_center, delta_width),
        )
    ):
        if dist_type is not None:
            particle_distribution[i] = _create_distribution(
                n_particles, dist_type, center, width
            )

    return particle_distribution


def _create_distribution(n_particles, dist_type, center, width):
    if dist_type is None:
        return
    elif dist_type == "uniform":
        tmp = width / 2
        return np.linspace(center - tmp, center + tmp, num=n_particles)
    elif dist_type == "dirac":
        return np.full(n_particles, center)
    else:
        raise NotImplementedError
