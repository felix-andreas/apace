import numpy as np

from .clib import accumulated_array
from .matrix_method import MatrixMethod
from .utils import Signal


class MatrixTracking:
    def __init__(self, main_cell, initial_distribution, turns=1, position=0):
        self.main_cell = main_cell
        self.matrix_method = MatrixMethod(main_cell)
        self._initial_distribution = initial_distribution
        self.turns = turns
        self.position = position

        self._orbit_position = None
        self._particle_trajectories = None
        self._particle_trajectories_needs_update = True
        self.particle_trajectories_changed = Signal(self.matrix_method.matrix_array_changed)
        self.particle_trajectories_changed.register(self.on_particle_trajectories_changed)

    @property
    def initial_distribution(self) -> np.ndarray:
        return self._initial_distribution

    @initial_distribution.setter
    def initial_distribution(self, value):
        self._initial_distribution = value
        self.particle_trajectories_changed()

    @property
    def particle_trajectories(self):
        if self._particle_trajectories_needs_update:
            self.update_particle_trajectories()

        return self._particle_trajectories

    @property
    def orbit_position(self) -> np.ndarray:
        if self._particle_trajectories_needs_update:
            self.update_particle_trajectories()

        return self._orbit_position

    @property
    def x_trajectory(self) -> np.ndarray:
        return self.particle_trajectories[:, 0, :]

    @property
    def x_dds_trajectory(self) -> np.ndarray:
        return self.particle_trajectories[:, 1, :]

    @property
    def y_trajectory(self) -> np.ndarray:
        return self.particle_trajectories[:, 2, :]

    @property
    def y_dds_trajectory(self) -> np.ndarray:
        return self.particle_trajectories[:, 3, :]

    @property
    def l_trajectory(self) -> np.ndarray:
        return self.particle_trajectories[:, 4, :]

    @property
    def delta_trajectory(self) -> np.ndarray:
        return self.particle_trajectories[:, 5, :]

    def update_particle_trajectories(self):
        n_kicks = self.matrix_method.n_kicks
        turns = self.turns
        position = self.position
        initial_distribution = self.initial_distribution
        matrix_array = self.matrix_method.matrix_array

        n = turns if position is not None else turns * n_kicks + 1
        result = np.empty((n, *initial_distribution.shape))
        orbit_position = np.empty(n)

        # TODO: implement in C
        if position == 0:
            acc_array = np.empty(matrix_array.shape)
            accumulated_array(matrix_array, acc_array)
            full_matrix = acc_array[-1]
            result[0] = initial_distribution
            orbit_position[0] = 0
            for i in range(1, turns):
                result[i] = np.dot(full_matrix, result[i - 1])
                orbit_position[i] = orbit_position[i - 1] + self.main_cell.length

        elif position is None:  # calc for all positions
            acc_array = np.empty(matrix_array.shape)
            # TODO: Remove identity from matrix_array ?
            accumulated_array(matrix_array, acc_array)
            result[0:n_kicks + 1] = np.dot(acc_array, initial_distribution)
            orbit_position[0:n_kicks + 1] = self.matrix_method.s
            for i in range(1, turns):
                idx = slice(i * n_kicks + 1, (i + 1) * n_kicks + 1)
                result[idx] = np.dot(acc_array[1:], result[i  * n_kicks])
                orbit_position[idx] = self.matrix_method.s[1:] + i * self.main_cell.length

        else:
            raise NotImplementedError  # TODO: change accumulated array for all positions

        self._orbit_position = orbit_position
        self._particle_trajectories = result
        self._particle_trajectories_needs_update = False

    def on_particle_trajectories_changed(self):
        self._particle_trajectories_needs_update = True
