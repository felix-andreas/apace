import numpy as np
from .classes import Drift, Bend, Quad
from .utils import Signal

MATRIX_SIZE = 6
IDENTITY = np.identity(MATRIX_SIZE)
C = 299_792_458
C_SQUARED = C ** 2
N_KICKS_DEFAULT = 1


class MatrixMethod:
    def __init__(self, main_cell, n_kicks_per_type=None, velocity=C):
        self.velocity = velocity
        self.main_cell = main_cell
        self.changed_elements = set()
        self.main_cell.element_changed.register(self._on_element_changed)

        self.n_kicks_changed = Signal()

        self._element_indices = None
        self._element_indices_needs_update = True
        self.element_indices_changed = Signal(self.main_cell.tree_changed)
        self.element_indices_changed.register(self._on_element_indices_changed)

        self._n_kicks_total = None
        self._n_kicks_total_needs_update = True
        self.n_kicks_total_changed = Signal(self.main_cell.tree_changed, self.n_kicks_changed)
        self.n_kicks_total_changed.register(self._on_n_kicks_changed)

        self._step_size = None
        self._step_size_needs_update = True
        self.step_size_changed = Signal(self.n_kicks_total_changed, self.main_cell.length_changed)
        self.step_size_changed.register(self._on_step_size_changed)

        self._s = None
        self._s_needs_update = True
        self.s_changed = Signal(self.step_size_changed)
        self.s_changed.register(self._on_s_changed)

        self._matrix_array = None
        self._matrix_array_needs_full_update = True
        self._matrix_array_needs_partial_update = False
        self.matrix_array_changed_full = Signal(self.n_kicks_total_changed)
        self.matrix_array_changed_full.register(self._on_matrix_array_changed_full)
        self.matrix_array_changed_partial = Signal()
        self.matrix_array_changed_partial.register(self._on_matrix_array_changed_partial)
        self.matrix_array_changed = Signal(self.matrix_array_changed_partial, self.matrix_array_changed_full)

        if n_kicks_per_type is None:
            self.n_kicks_per_type = {
                Drift: 3,
                Bend: 10,
                Quad: 5,
            }
        else:
            self.n_kicks_per_type = n_kicks_per_type

    def _on_element_changed(self, element):
        self.changed_elements.add(element)
        self.matrix_array_changed_partial()

    # TODO: Better API to set n_kicks
    def set_n_kicks(self):
        self.n_kicks_changed()
        raise NotImplementedError

    def get_n_kicks(self, element):
        return self.n_kicks_per_type.get(element.__class__, N_KICKS_DEFAULT)

    @property
    def n_kicks_total(self) -> int:
        if self._n_kicks_total_needs_update:
            self.update_n_kicks()

        return self._n_kicks_total

    def update_n_kicks(self):
        self._n_kicks_total = sum([self.get_n_kicks(element) for element in self.main_cell.lattice])
        self._n_kicks_total_needs_update = False

    def _on_n_kicks_changed(self):
        self._n_kicks_total_needs_update = True

    @property
    def element_indices(self) -> dict:
        if self._element_indices_needs_update:
            self.update_element_indices()

        return self._element_indices

    def update_element_indices(self):
        self._element_indices = {}
        start = 1  # starts with 1 because 0th entry is identity matrix
        for element in self.main_cell.lattice:
            end = start + self.get_n_kicks(element)
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
        if self._step_size_needs_update:
            self.update_step_size()

        return self._step_size

    def update_step_size(self):
        self._step_size = np.empty(self.n_kicks_total + 1)
        self._step_size[0] = 0
        for element in self.main_cell.elements.values():
            self._step_size[self.element_indices[element]] = element.length / self.get_n_kicks(element)

        self._step_size_needs_update = False

    def _on_step_size_changed(self):
        self._step_size_needs_update = True

    @property
    def s(self):
        if self._s_needs_update:
            self.update_s()

        return self._s

    def update_s(self):
        self._s = np.add.accumulate(self.step_size)  # s corresponds to the orbit position

    def _on_s_changed(self):
        self._s_needs_update = True

    @property
    def matrix_array(self):
        if self._matrix_array_needs_full_update:  # update all
            self.allocate_matrix_array()
            self.update_matrix_array(self.main_cell.elements.values())
            self.changed_elements.clear()
            self._matrix_array_needs_full_update = False

        elif self._matrix_array_needs_partial_update:  # update partial
            self.update_matrix_array(self.changed_elements)
            self.changed_elements.clear()
            self._matrix_array_needs_partial_update = False

        return self._matrix_array

    def allocate_matrix_array(self):
        self._matrix_array = np.empty((self.step_size.size, MATRIX_SIZE, MATRIX_SIZE))
        self._matrix_array[0] = np.identity(MATRIX_SIZE)

    def update_matrix_array(self, elements):
        matrix_array = self._matrix_array
        for element in elements:
            pos = self.element_indices[element]  # indices in matrix matrix_array
            n_kicks = self.get_n_kicks(element)
            step_size = element.length / n_kicks

            # TODO: change element 4,5 for velocity smaller than light
            velocity = self.velocity
            if velocity < C:
                gamma = 1 / np.sqrt(1 - velocity ** 2 / C_SQUARED)
                el_45 = step_size / gamma ** 2
            else:
                el_45 = 0

            if isinstance(element, Quad) and element.k1:  # Quad with k != 0
                sqk = np.sqrt(np.absolute(element.k1))
                om = sqk * step_size
                sin = np.sin(om)
                cos = np.cos(om)
                sinh = np.sinh(om)
                cosh = np.cosh(om)
                if element.k1 > 0:  # k > horizontal focusing
                    matrix_array[pos] = [
                        [cos, 1 / sqk * sin, 0, 0, 0, 0],
                        [-sqk * sin, cos, 0, 0, 0, 0],
                        [0, 0, cosh, 1 / sqk * sinh, 0, 0],
                        [0, 0, sqk * sinh, cosh, 0, 0],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1]
                    ]
                else:  # k < vertical focusing
                    matrix_array[pos] = [
                        [cosh, 1 / sqk * sinh, 0, 0, 0, 0],
                        [sqk * sinh, cosh, 0, 0, 0, 0],
                        [0, 0, cos, 1 / sqk * sin, 0, 0],
                        [0, 0, -sqk * sin, cos, 0, 0],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1]
                    ]

            elif isinstance(element, Bend) and element.angle:  # Bend with angle != 0
                phi = step_size / element.radius
                sin = np.sin(phi)
                cos = np.cos(phi)
                radius = element.radius
                kappa_x = 1 / radius
                matrix_array[pos] = [
                    [cos, element.radius * sin, 0, 0, 0, element.radius * (1 - cos)],
                    [-kappa_x * sin, cos, 0, 0, 0, sin],
                    [0, 0, 1, step_size, 0, 0],
                    [0, 0, 0, 1, 0, 0],
                    [-sin, (cos - 1) * radius, 0, 0, 1, (sin - phi) * radius],
                    [0, 0, 0, 0, 0, 1]
                ]

                if element.e1:
                    tan_r1 = np.tan(element.e1) / element.radius
                    matrix_edge_1 = IDENTITY.copy()
                    matrix_edge_1[1, 0], matrix_edge_1[3, 2] = tan_r1, -tan_r1
                    matrix_array[pos[::n_kicks]] = np.dot(matrix_array[pos[0]], matrix_edge_1)

                if element.e2:
                    tan_r2 = np.tan(element.e2) / element.radius
                    matrix_edge_2 = IDENTITY.copy()
                    matrix_edge_2[1, 0], matrix_edge_2[3, 2] = tan_r2, -tan_r2
                    matrix_array[pos[n_kicks - 1::n_kicks]] = np.dot(matrix_edge_2, matrix_array[pos[-1]])

            else:  # Drifts and remaining elements
                matrix = IDENTITY.copy()
                matrix[0, 1] = matrix[2, 3] = step_size
                matrix_array[pos] = matrix

    def _on_matrix_array_changed_partial(self):
        self._matrix_array_needs_partial_update = True

    def _on_matrix_array_changed_full(self):
        self._matrix_array_needs_full_update = True
