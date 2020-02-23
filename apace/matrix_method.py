import numpy as np
from .classes import Element, Drift, Dipole, Quadrupole
from .utils import Signal
from typing import List, Dict

from .clib import accumulate_array

MATRIX_SIZE = 6
IDENTITY = np.identity(MATRIX_SIZE)
C = 299_792_458
C_SQUARED = C ** 2
N_KICKS_DEFAULT = 1


class MatrixMethod:
    """The transfer matrix method.

    :param lattice: Lattice which transfer matrices gets calculated for.
    :param int start_index: Start index for the one-turn matrix
           and for the accumulated transfer matrices.
    :param float start_position: Same as start_index but uses position instead of index of the position.
           Is ignored if start_index is set.
    :param number velocity: Velocity of the particles.
    """

    def __init__(self, lattice, start_index=None, start_position=None, velocity=C):
        self.lattice = lattice
        self.velocity = velocity

        self.changed_elements = set()
        self.lattice.element_changed.connect(self._on_element_changed)

        self.element_n_kicks = {Drift: 3, Dipole: 10, Quadrupole: 5}
        self.element_n_kicks_changed = Signal()

        self._element_indices = {}
        self._element_indices_needs_update = True
        self.element_indices_changed = Signal(self.element_n_kicks_changed)
        self.element_indices_changed.connect(self._on_element_indices_changed)

        self._n_kicks = 0
        self._n_points = 0
        self._n_kicks_needs_update = True
        self.n_kicks_changed = Signal(self.element_n_kicks_changed)
        self.n_kicks_changed.connect(self._on_n_kicks_changed)

        self._step_size = np.empty(0)
        self._step_size_needs_update = True
        self.step_size_changed = Signal(
            self.n_kicks_changed, self.lattice.length_changed
        )
        self.step_size_changed.connect(self._on_step_size_changed)

        self._s = np.empty(0)
        self._s_needs_update = True
        self.s_changed = Signal(self.step_size_changed)
        self.s_changed.connect(self._on_s_changed)

        self._transfer_matrices = np.empty(0)
        self._transfer_matrices_needs_full_update = True
        self.transfer_matrices_changed = Signal()
        self._k0 = np.empty(0)
        self._k1 = np.empty(0)

        self._start_index = start_index
        self._start_position_changed = Signal()

        if start_position is not None and start_index is None:
            self.start_position = start_position

        self._transfer_matrices_acc = np.empty(0)
        self._transfer_matrices_acc_needs_update = True
        self.transfer_matrices_acc_changed = Signal(
            self.transfer_matrices_changed, self._start_position_changed
        )
        self.transfer_matrices_acc_changed.connect(
            self._on_transfer_matrices_accumulated_changed
        )

        self._one_turn_matrix = np.empty(0)

    def _on_element_changed(self, element, attribute):
        self.changed_elements.add(element)
        self.transfer_matrices_changed()

    # TODO: Better API to set n_kicks
    def set_n_kicks(self):
        self.element_n_kicks_changed()
        raise NotImplementedError

    def n_kicks_per_element(self, element) -> int:
        """Returns the number of kicks for a given element"""
        return self.element_n_kicks.get(element.__class__, N_KICKS_DEFAULT)

    @property
    def n_kicks(self) -> int:
        """Total number of kicks. (:attr:`n_points` - 1)."""
        if self._n_kicks_needs_update:
            self.update_n_kicks()

        return self._n_kicks

    @property
    def n_points(self) -> int:
        """Total number of points (:attr:`n_kicks` + 1)."""
        if self._n_kicks_needs_update:
            self.update_n_kicks()

        return self._n_points

    def update_n_kicks(self):
        """Manually update the total number of kicks."""
        n_kicks = sum(map(self.n_kicks_per_element, self.lattice.arrangement))
        self._n_kicks = n_kicks
        self._n_points = n_kicks + 1
        self._n_kicks_needs_update = False

    def _on_n_kicks_changed(self):
        self._n_kicks_needs_update = True

    @property
    def element_indices(self) -> Dict[Element, List[int]]:
        """Contains the indices of each element within the transfer_matrices."""
        if self._element_indices_needs_update:
            self.update_element_indices()

        return self._element_indices

    def update_element_indices(self):
        """Manually update the indices of each element."""
        self._element_indices.clear()
        start = 0
        for element in self.lattice.arrangement:
            end = start + self.n_kicks_per_element(element)
            tmp = list(range(start, end))
            try:
                self._element_indices[element].extend(tmp)
            except KeyError:
                self._element_indices[element] = tmp
            start = end

        self._element_indices_needs_update = False

    def _on_element_indices_changed(self):
        self._element_indices_needs_update = True

    @property
    def step_size(self) -> np.ndarray:
        """Contains the step_size for each point. Has length of `n_kicks`"""
        if self._step_size_needs_update:
            self.update_step_size()

        return self._step_size

    def update_step_size(self):
        """Manually update the step_size array."""
        if self._step_size.size != self.n_kicks:
            self._step_size = np.empty(self.n_kicks)
            self._step_size[0] = 0

        for element in self.lattice.elements:
            n_kicks = self.n_kicks_per_element(element)
            self._step_size[self.element_indices[element]] = element.length / n_kicks

        self._step_size_needs_update = False

    def _on_step_size_changed(self):
        self._step_size_needs_update = True

    @property
    def s(self) -> np.ndarray:
        """Contains the orbit position s for each point. Has length of `n_kicks + 1`."""
        if self._s_needs_update:
            self.update_s()

        return self._s

    def update_s(self):
        """Manually update the orbit position array s."""
        points = self.n_kicks + 1
        if self._s.size != points:
            self._s = np.empty(points)
            self._s[0] = 0

        np.add.accumulate(self.step_size, out=self._s[1:])

    def _on_s_changed(self):
        self._s_needs_update = True

    @property
    def transfer_matrices(self) -> np.ndarray:
        """Array of transfer matrices with shape (6, 6, n_kicks)"""
        if self.changed_elements or self._transfer_matrices_needs_full_update:
            self.update_transfer_matrices()

        return self._transfer_matrices

    @property
    def k0(self) -> np.ndarray:
        """Array of deflections angles with shape (n_kicks)."""
        if self.changed_elements or self._transfer_matrices_needs_full_update:
            self.update_transfer_matrices()

        return self._k0

    @property
    def k1(self) -> np.ndarray:
        """Array of geometric quadruole strenghts with shape (n_kicks)."""
        if self.changed_elements or self._transfer_matrices_needs_full_update:
            self.update_transfer_matrices()

        return self._k1

    def update_transfer_matrices(self):
        """Manually update the transfer_matrices."""
        if self._transfer_matrices.shape[0] != self.n_kicks:
            self._transfer_matrices = np.empty((self.n_kicks, MATRIX_SIZE, MATRIX_SIZE))
            self._k0 = np.empty(self.n_kicks)
            self._k1 = np.empty(self.n_kicks)

        if self._transfer_matrices_needs_full_update:
            elements = self.lattice.elements
        else:
            elements = self.changed_elements

        matrix_array = self._transfer_matrices
        for element in elements:
            pos = self.element_indices[element]  # indices in matrix transfer_matrices
            n_kicks = self.n_kicks_per_element(element)
            step_size = element.length / n_kicks

            # TODO: change element 4,5 for velocity smaller than light
            velocity = self.velocity
            if velocity < C:
                gamma = 1 / np.sqrt(1 - velocity ** 2 / C_SQUARED)
                el_45 = step_size / gamma ** 2
            else:
                el_45 = 0

            if isinstance(element, Quadrupole) and element.k1:
                k0 = 0
                k1 = element.k1
                sqk = np.sqrt(np.absolute(k1))
                om = sqk * step_size
                sin = np.sin(om)
                cos = np.cos(om)
                sinh = np.sinh(om)
                cosh = np.cosh(om)
                if k1 > 0:  # k1 > horizontal focusing
                    matrix_array[pos] = [
                        [cos, 1 / sqk * sin, 0, 0, 0, 0],
                        [-sqk * sin, cos, 0, 0, 0, 0],
                        [0, 0, cosh, 1 / sqk * sinh, 0, 0],
                        [0, 0, sqk * sinh, cosh, 0, 0],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1],
                    ]
                else:  # k1 < vertical focusing
                    matrix_array[pos] = [
                        [cosh, 1 / sqk * sinh, 0, 0, 0, 0],
                        [sqk * sinh, cosh, 0, 0, 0, 0],
                        [0, 0, cos, 1 / sqk * sin, 0, 0],
                        [0, 0, -sqk * sin, cos, 0, 0],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1],
                    ]
            elif isinstance(element, Dipole) and element.angle:
                k0 = element.k0
                k1 = 0
                phi = element.angle / n_kicks
                sin = np.sin(phi)
                cos = np.cos(phi)
                radius = element.radius
                matrix_array[pos] = [
                    [cos, radius * sin, 0, 0, 0, radius * (1 - cos)],
                    [-k0 * sin, cos, 0, 0, 0, sin],
                    [0, 0, 1, step_size, 0, 0],
                    [0, 0, 0, 1, 0, 0],
                    [-sin, (cos - 1) * radius, 0, 0, 1, (sin - phi) * radius],
                    [0, 0, 0, 0, 0, 1],
                ]

                if element.e1:
                    tan_r1 = np.tan(element.e1) / radius
                    matrix_edge_1 = IDENTITY.copy()
                    matrix_edge_1[1, 0], matrix_edge_1[3, 2] = tan_r1, -tan_r1
                    matrix_array[pos[::n_kicks]] = np.dot(
                        matrix_array[pos[0]], matrix_edge_1
                    )

                if element.e2:
                    tan_r2 = np.tan(element.e2) / radius
                    matrix_edge_2 = IDENTITY.copy()
                    matrix_edge_2[1, 0], matrix_edge_2[3, 2] = tan_r2, -tan_r2
                    matrix_array[pos[n_kicks - 1 :: n_kicks]] = np.dot(
                        matrix_edge_2, matrix_array[pos[-1]]
                    )
            else:  # Drifts and remaining elements
                k0 = 0
                k1 = 0
                matrix = IDENTITY.copy()
                matrix[0, 1] = matrix[2, 3] = step_size
                matrix_array[pos] = matrix

            self._k0[pos] = k0
            self._k1[pos] = k1

        self.changed_elements.clear()
        self._transfer_matrices_needs_full_update = False

    @property
    def start_index(self) -> int:
        """Start index of the one-turn matrix and the accumulated transfer matrices."""
        return self._start_index

    @start_index.setter
    def start_index(self, value):
        self._start_index = value
        self._start_position_changed()

    @property
    def start_position(self) -> float:
        """Same as start_index, but position in meter instead of index."""
        return self.s[self.start_index]

    @start_position.setter
    def start_position(self, value):
        self.start_index = np.searchsorted(self.s, value) - 1

    @property
    def transfer_matrices_acc(self) -> np.ndarray:
        """The accumulated transfer matrices starting from start_index."""
        if self._transfer_matrices_acc_needs_update:
            self.update_transfer_matrices_acc()
        return self._transfer_matrices_acc

    def update_transfer_matrices_acc(self):
        accumulate_array(
            self.transfer_matrices, self.transfer_matrices_acc, self.start_index
        )

    def _on_transfer_matrices_accumulated_changed(self):
        self.transfer_matrices_acc_changed = True
