from collections.abc import Iterable

import numpy as np

from .clib import matrix_product_accumulated, matrix_product_ranges
from .matrixmethod import MatrixMethod, MATRIX_SIZE
from .utils import Signal


class TrackingMatrix:
    """Particle tracking using the transfer matrix method.

    :param Lattice lattice: Lattice which particles will be tracked through.
    :param np.ndarray initial_distribution: Initial particle distribution.
    :param int turns: Number of turns.
    :param watch_points: List of watch points. If unset all particle trajectory
           will be saved for all positions. Indices correspont to ``orbit_positions``.
    :type watch_points: array-like, optional
    :param int start_point: Point at which the particle tracking begins.
    """

    def __init__(
        self, lattice, initial_distribution, turns=1, watch_points=None, start_point=0
    ):
        self.lattice = lattice
        self.matrix_method = MatrixMethod(lattice)
        self._initial_distribution = initial_distribution

        self.n_turns = turns
        self.start_point = start_point
        self.watch_points = watch_points

        self._orbit_position = np.empty(0)
        self._particle_trajectories = np.empty(0)
        self._particle_trajectories_needs_update = True
        self.particle_trajectories_changed = Signal(self.matrix_method.matrices_changed)
        self.particle_trajectories_changed.connect(
            self._on_particle_trajectories_changed
        )

    @property
    def watch_points(self):
        return self._watch_points

    @watch_points.setter
    def watch_points(self, value):
        if value is None:
            value = ()
        elif not isinstance(value, Iterable):
            raise ValueError("Watch points must be a Iterable or None!")

        # TODO: needs to update trajectories
        self._watch_points = np.sort(np.array(value, dtype=np.int32))

    @property
    def initial_distribution(self) -> np.ndarray:
        return self._initial_distribution

    @initial_distribution.setter
    def initial_distribution(self, value):
        self._initial_distribution = value
        self.particle_trajectories_changed()

    @property
    def particle_trajectories(self) -> np.ndarray:
        """Contains the 6D particle trajectories."""
        if self._particle_trajectories_needs_update:
            self.update_particle_trajectories()
        return self._particle_trajectories

    @property
    def orbit_position(self) -> np.ndarray:
        if self._particle_trajectories_needs_update:
            self.update_particle_trajectories()
        return self._orbit_position

    @property
    def x(self) -> np.ndarray:
        return self.particle_trajectories[:, 0]

    @property
    def x_dds(self) -> np.ndarray:
        return self.particle_trajectories[:, 1]

    @property
    def y(self) -> np.ndarray:
        return self.particle_trajectories[:, 2]

    @property
    def y_dds(self) -> np.ndarray:
        return self.particle_trajectories[:, 3]

    @property
    def lon(self) -> np.ndarray:
        return self.particle_trajectories[:, 4]

    @property
    def delta(self) -> np.ndarray:
        return self.particle_trajectories[:, 5]

    def update_particle_trajectories(self):
        """Manually update the 6D particle trajectories"""
        n_steps = self.matrix_method.n_steps
        n_points = n_steps + 1
        n_turns = self.n_turns
        watch_points = self.watch_points
        n_watch_points = len(watch_points)
        watch_all = n_watch_points == 0
        initial_distribution = self.initial_distribution
        matrices = self.matrix_method.matrices

        if any(0 > point > n_steps for point in watch_points):
            raise ValueError("Invalid watch points!")

        if watch_all:
            n = n_turns * n_steps + 1
        else:
            n = n_turns * n_watch_points

        if self._orbit_position.size != n:
            self._orbit_position = np.empty(n)
            self._particle_trajectories = np.empty((n, *initial_distribution.shape))

        orbit_position = self._orbit_position
        trajectories = self._particle_trajectories

        # TODO: implement in C
        if watch_all:
            acc_array = np.empty(matrices.shape)
            matrix_product_accumulated(matrices, acc_array, 0)
            trajectories[0] = initial_distribution
            np.dot(acc_array, initial_distribution, out=trajectories[1:n_points])
            orbit_position[0:n_points] = self.matrix_method.s
            for i in range(1, n_turns):
                idx = slice(i * n_steps + 1, (i + 1) * n_steps + 1)
                np.dot(acc_array, trajectories[i * n_steps], out=trajectories[idx])
                orbit_position[idx] = self.matrix_method.s[1:] + i * self.lattice.length
        else:
            if watch_points[0] == 0:
                trajectories[0] = initial_distribution
            else:
                to_first_point = np.empty((1, *initial_distribution.shape))
                matrix_product_ranges(
                    matrices,
                    to_first_point,
                    np.array([[0, watch_points[0]]], dtype=np.int32),
                )
                trajectories[0] = np.dot(to_first_point, initial_distribution)

            orbit_position[:n_watch_points] = self.matrix_method.s[watch_points]
            acc_array = np.empty((n_watch_points, MATRIX_SIZE, MATRIX_SIZE))
            ranges = np.empty((n_watch_points, 2), dtype=np.int32)
            for i, point in enumerate(watch_points):
                # for multiple turns start and end_point must be the same!
                if point == n_steps:
                    point = 0

                ranges[i, 0] = point
                ranges[i - 1, 1] = point

            matrix_product_ranges(matrices, acc_array, ranges)

            for turn in range(1, n_turns):
                idx = turn * n_watch_points
                orbit_position[idx : idx + n_watch_points] = (
                    self.matrix_method.s[watch_points] + turn * self.lattice.length
                )
                for j in range(n_watch_points):
                    i = idx + j
                    np.dot(acc_array[j - 1], trajectories[i - 1], out=trajectories[i])

        self._particle_trajectories_needs_update = False

    def _on_particle_trajectories_changed(self):
        self._particle_trajectories_needs_update = True
