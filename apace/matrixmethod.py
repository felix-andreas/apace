from typing import List, Dict
import numpy as np
from math import ceil
from .classes import Element, Drift, Dipole, Quadrupole
from .utils import Signal, Attribute
from .clib import matrix_product_accumulated

MATRIX_SIZE = 6
IDENTITY = np.identity(MATRIX_SIZE)
C = 299_792_458
C_SQUARED = C ** 2
CONST_MEV = 1.602176634e-13  # MeV to Joule
CONST_ME = 9.1093837015e-31  # kg

# TODO: What is the best way to set the number of steps ?
#    1. Fixed number of steps per element (depending on element type)
#    2. Steps per meter (depending on element type)
#    3. User defined function, which returns number of steps for given element


class MatrixMethod:
    """The transfer matrix method.

    :param lattice: Lattice which transfer matrices gets calculated for.
    :param int steps_per_element: Fixed number of steps per element.
                                     (ignored if steps_per_meter is passed)
    :param number steps_per_meter: Fixed number of steps per meter.
    :param int start_index: Start index for the one-turn matrix and for the accumulated
                            transfer matrices.
    :param number start_position: Same as start_index but uses position instead of index
                                  of the position. Is ignored if start_index is set.
    :param number energy: Total energy per particle in MeV.
    """

    def __init__(
        self,
        lattice,
        steps_per_element=10,
        steps_per_meter=None,
        start_index=None,
        start_position=None,
        energy=None,
    ):
        self.lattice = lattice
        self._energy = energy
        if steps_per_meter is None:
            if isinstance(steps_per_element, (int, float)):
                self.get_steps = lambda element: steps_per_element
            elif isinstance(steps_per_element, dict):
                self.get_steps = lambda element: steps_per_element.get(type(element))
            else:
                raise TypeError("steps_per_element must be a number or a dict.")
        elif isinstance(steps_per_meter, (int, float)):
            self.get_steps = lambda element: ceil(steps_per_meter * element.length)
        elif isinstance(steps_per_meter, dict):
            self.get_steps = lambda element: ceil(
                steps_per_meter.get(type(element)) * element.length
            )
        else:
            raise TypeError("steps_per_meter must be a number or a dict.")

        self.changed_elements = self.lattice.elements.copy()
        self.lattice.element_changed.connect(self._on_element_changed)

        self._element_indices = {}
        self._element_indices_needs_update = True
        self.element_indices_changed = Signal()
        self.element_indices_changed.connect(self._on_element_indices_changed)

        self._n_steps = 0
        self._n_steps_needs_update = True
        self.n_steps_changed = Signal()
        self.n_steps_changed.connect(self._on_n_steps_changed)

        self._step_size = np.empty(0)
        self._step_size_needs_update = True
        self.step_size_changed = Signal(
            self.n_steps_changed, self.lattice.length_changed
        )
        self.step_size_changed.connect(self._on_step_size_changed)

        self._s = np.empty(0)
        self._s_needs_update = True
        self.s_changed = Signal(self.step_size_changed)
        self.s_changed.connect(self._on_s_changed)

        self._matrices = np.empty(0)
        self.matrices_changed = Signal()
        self._k0 = np.empty(0)
        self._k1 = np.empty(0)

        self._start_index = start_index
        self._start_position_changed = Signal()

        if start_position is not None and start_index is None:
            self.start_position = start_position

        self._matrices_acc = np.empty(0)
        self._matrices_acc_needs_update = True
        self.matrices_acc_changed = Signal(
            self.matrices_changed, self._start_position_changed
        )
        self.matrices_acc_changed.connect(self._on_matrices_accumulated_changed)

        self._one_turn_matrix = np.empty(0)

    @property
    def energy(self) -> float:
        if self._energy is None:
            raise Exception("Energy is not set!")
        return self._energy

    @property
    def gamma(self) -> float:
        return self.energy * CONST_MEV / CONST_ME / C_SQUARED

    @property
    def velocity(self) -> float:
        return C * np.sqrt(1 - 1 / self.gamma ** 2)

    def _on_element_changed(self, element, attribute):
        if attribute == Attribute.LENGTH:
            # TODO: n_steps and n_indices can change if the length of an element changes
            # but it is relativly expensive to recalculate them every time!
            # n_steps_changed()
            # element_indices_changed()
            pass

        self.changed_elements.add(element)
        self.matrices_changed()

    @property
    def n_steps(self) -> int:
        """Total number of steps."""
        if self._n_steps_needs_update:
            self.update_n_steps()
        return self._n_steps

    def update_n_steps(self):
        """Manually update the total number of kicks."""
        self._n_steps = sum(map(self.get_steps, self.lattice.arrangement))
        self._n_steps_needs_update = False

    def _on_n_steps_changed(self):
        self._n_steps_needs_update = True

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
            end = start + self.get_steps(element)
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
        if self._step_size.size != self.n_steps:
            self._step_size = np.empty(self.n_steps)
            self._step_size[0] = 0

        for element in self.lattice.elements:
            n_steps = self.get_steps(element)
            self._step_size[self.element_indices[element]] = element.length / n_steps

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
        points = self.n_steps + 1
        if self._s.size != points:
            self._s = np.empty(points)
            self._s[0] = 0

        np.add.accumulate(self.step_size, out=self._s[1:])

    def _on_s_changed(self):
        self._s_needs_update = True

    @property
    def matrices(self) -> np.ndarray:
        """Array of transfer matrices with shape (6, 6, n_kicks)"""
        if self.changed_elements:
            self.update_matrices()
        return self._matrices

    @property
    def k0(self) -> np.ndarray:
        """Array of deflections angles with shape (n_kicks)."""
        if self.changed_elements:
            self.update_matrices()
        return self._k0

    @property
    def k1(self) -> np.ndarray:
        """Array of geometric quadruole strenghts with shape (n_kicks)."""
        if self.changed_elements:
            self.update_matrices()
        return self._k1

    def update_matrices(self):
        """Manually update the transfer_matrices."""
        if self._matrices.shape[0] != self.n_steps:
            self._matrices = np.empty((self.n_steps, MATRIX_SIZE, MATRIX_SIZE))
            self._k0 = np.empty(self.n_steps)
            self._k1 = np.empty(self.n_steps)

        elements = self.changed_elements

        matrix_array = self._matrices
        for element in elements:
            pos = self.element_indices[element]  # indices in matrix array
            n_kicks = self.get_steps(element)
            step_size = element.length / n_kicks

            # TODO: change element (4,5) for velocity smaller than light
            # el_45 = 0 if energy is None else step_size / gamma ** 2

            self._k0[pos] = k0 = getattr(element, "k0", 0)
            self._k1[pos] = k1 = getattr(element, "k1", 0)

            if isinstance(element, Quadrupole) and k1:
                sqk = np.sqrt(np.absolute(k1))
                om = sqk * step_size
                sin = np.sin(om)
                cos = np.cos(om)
                sinh = np.sinh(om)
                cosh = np.cosh(om)
                if k1 > 0:  # horizontal focusing
                    matrix_array[pos] = [
                        [cos, 1 / sqk * sin, 0, 0, 0, 0],
                        [-sqk * sin, cos, 0, 0, 0, 0],
                        [0, 0, cosh, 1 / sqk * sinh, 0, 0],
                        [0, 0, sqk * sinh, cosh, 0, 0],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1],
                    ]
                else:  # vertical focusing
                    matrix_array[pos] = [
                        [cosh, 1 / sqk * sinh, 0, 0, 0, 0],
                        [sqk * sinh, cosh, 0, 0, 0, 0],
                        [0, 0, cos, 1 / sqk * sin, 0, 0],
                        [0, 0, -sqk * sin, cos, 0, 0],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1],
                    ]
            elif isinstance(element, Dipole) and k0:
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
                matrix = IDENTITY.copy()
                matrix[0, 1] = matrix[2, 3] = step_size
                matrix_array[pos] = matrix

        self.changed_elements.clear()

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
    def matrices_acc(self) -> np.ndarray:
        """The accumulated transfer matrices starting from start_index."""
        if self._matrices_acc_needs_update:
            self.update_matrices_acc()
        return self._matrices_acc

    def update_matrices_acc(self):
        matrix_product_accumulated(self.matrices, self.matrices_acc, self.start_index)

    def _on_matrices_accumulated_changed(self):
        self.matrices_acc_changed = True
