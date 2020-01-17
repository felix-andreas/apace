import numpy as np

from .clib import accumulate_array
from .matrix_method import MatrixMethod
from .utils import Signal


class MatrixTracking:
    """Particle tracking using the transfer matrix method.

    :param Lattice lattice: Lattice which particles will be tracked through.
    :param np.ndarray initial_distribution: Initial particle distribution.
    :param int turns: Number of turns.
    :param positions: List of positions to watch. If unset all particle trajectory
           will be saved for all positions.
    :type positions: list, optional
    """

    def __init__(self, lattice, initial_distribution, turns=1, positions=None):
        self.lattice = lattice
        self.matrix_method = MatrixMethod(lattice)
        self._initial_distribution = initial_distribution
        self.turns = turns
        self.positions = positions  # TODO: make sure it is list!

        self._orbit_position = np.empty(0)
        self._particle_trajectories = np.empty(0)
        self._particle_trajectories_needs_update = True
        self.particle_trajectories_changed = Signal(
            self.matrix_method.transfer_matrices_changed
        )
        self.particle_trajectories_changed.connect(
            self._on_particle_trajectories_changed
        )

    @property
    def initial_distribution(self) -> np.ndarray:
        return self._initial_distribution

    @initial_distribution.setter
    def initial_distribution(self, value):
        self._initial_distribution = value
        self.particle_trajectories_changed()

    @property
    def particle_trajectories(self) -> np.ndarray:
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
        return self.particle_trajectories[:, 0, :]

    @property
    def x_dds(self) -> np.ndarray:
        return self.particle_trajectories[:, 1, :]

    @property
    def y(self) -> np.ndarray:
        return self.particle_trajectories[:, 2, :]

    @property
    def y_dds(self) -> np.ndarray:
        return self.particle_trajectories[:, 3, :]

    @property
    def long(self) -> np.ndarray:
        return self.particle_trajectories[:, 4, :]

    @property
    def delta(self) -> np.ndarray:
        return self.particle_trajectories[:, 5, :]

    def update_particle_trajectories(self):
        n_kicks = self.matrix_method.n_kicks
        n_points = self.matrix_method.n_points
        turns = self.turns
        position = self.positions
        initial_distribution = self.initial_distribution
        matrix_array = self.matrix_method.transfer_matrices

        n = turns if position is not None else turns * n_points
        if self._orbit_position.size != n:
            self._orbit_position = np.empty(n)
            self._particle_trajectories = np.empty((n, *initial_distribution.shape))

        orbit_position = self._orbit_position
        trajectories = self._particle_trajectories

        # TODO: implement in C
        if position == 0:
            acc_array = np.empty(matrix_array.shape)
            accumulate_array(matrix_array, acc_array, 0)  # TODO: use partial method!
            full_matrix = acc_array[-1]
            trajectories[0] = initial_distribution
            orbit_position[0] = 0
            for i in range(1, turns):
                trajectories[i] = np.dot(full_matrix, trajectories[i - 1])
                orbit_position[i] = orbit_position[i - 1] + self.lattice.length
        elif position is None:  # calc for all positions
            acc_array = np.empty(matrix_array.shape)
            accumulate_array(matrix_array, acc_array, 0)
            trajectories[0] = initial_distribution
            trajectories[1:n_points] = np.dot(acc_array, initial_distribution)
            orbit_position[0:n_points] = self.matrix_method.s
            for i in range(1, turns):
                idx = slice(i * n_points, (i + 1) * n_points)
                trajectories[idx] = np.dot(acc_array, trajectories[i * n_kicks])
                orbit_position[idx] = self.matrix_method.s[1:] + i * self.lattice.length
        else:
            raise NotImplementedError  # TODO: change accumulated array for all positions

        self._particle_trajectories_needs_update = False

    def _on_particle_trajectories_changed(self):
        self._particle_trajectories_needs_update = True
