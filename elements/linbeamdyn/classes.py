from .transfer_matrices import get_transfer_matrices, matrix_size
import numpy as np
from .twiss import twiss_data
from ..classes import CachedPropertyFlag
from elements.utils import Structure

class LinBeamDyn:
    def __init__(self, main_cell):
        """
        Creates
        Args:
            Mainline:
        """
        self.main_cell = main_cell
        self.main_cell.methods.append(self)
        self._changed_elements = set()

        # properties
        self._transfer_matrices = None
        self.flag_allocate_transfer_matrices = CachedPropertyFlag(depends_on=[self.main_cell.step_size_flag])
        self.flag_transfer_matrices_all = CachedPropertyFlag(depends_on=[self.flag_allocate_transfer_matrices])
        self.flag_transfer_matrices_partial = CachedPropertyFlag(depends_on=[self.main_cell.changed_elements_flag], initial_state=False)
        self.flag_twiss_data = CachedPropertyFlag(depends_on=[self.flag_transfer_matrices_all,
                                                              self.flag_transfer_matrices_partial])
        self._twiss_data = Structure()
        self._tracking_data = Structure()
        self.twiss_data_changed = True
        self.twiss_options = dict()

    def changed_elements(self, changed_elements):
        self._changed_elements.add(changed_elements)
        self.flag_transfer_matrices_partial.has_changed = True

    @property
    def transfer_matrices(self):
        if self.flag_allocate_transfer_matrices.has_changed:
            self.allocate_transfer_matrices()
            self.flag_allocate_transfer_matrices.has_changed = False

        if self.flag_transfer_matrices_partial.has_changed:  # update partial
            get_transfer_matrices(self._changed_elements, self._transfer_matrices)
            self.flag_transfer_matrices_partial.has_changed = False
            self._changed_elements.clear()

        if self.flag_transfer_matrices_all.has_changed:  # update all
            get_transfer_matrices(self.main_cell.elements.values(), self._transfer_matrices)
            self._changed_elements.clear()
            self.flag_transfer_matrices_all.has_changed = False

        return self._transfer_matrices

    def allocate_transfer_matrices(self):
        self._transfer_matrices = np.empty((self.main_cell.step_size.size, matrix_size, matrix_size))
        self._transfer_matrices[0] = np.identity(matrix_size)

    @property
    def twiss(self):
        if self.flag_twiss_data.has_changed:
            self.get_twiss(**self.twiss_options)
        return self._twiss_data

    def get_twiss(self, **options):
        self.twiss_options = options
        self._twiss_data.s = self.main_cell.s
        twiss_data(self._twiss_data, self.transfer_matrices, **options)
        self.flag_twiss_data.has_changed = False
        return self.twiss

