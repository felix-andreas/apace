from .transfer_matrices import get_transfer_matrices, matrix_size
import numpy as np
from .twiss import twissdata
from ..classes import CachedPropertyFlag
from elements.utils import Structure

class LinBeamDyn:
    def __init__(self, maincell):
        """
        Creates
        Args:
            Mainline:
        """
        self.maincell = maincell
        self._changed_elements = set()

        # properties
        self._transfer_matrices = None
        self.flag_allocate_transfer_matrices = CachedPropertyFlag(depends_on=[self.maincell.stepsize_flag])
        self.flag_transfer_matrices_all = CachedPropertyFlag(depends_on=[self.flag_allocate_transfer_matrices])
        self.flag_transfer_matrices_partial = CachedPropertyFlag(depends_on=None, initial_state=False)
        self.flag_twissdata = CachedPropertyFlag(depends_on=[self.flag_transfer_matrices_all,
                                                             self.flag_transfer_matrices_partial])
        self._twissdata = Structure()
        self._trackingdata = Structure()
        self.twissdata_changed = True

    def changed_elements(self, changed_elements):
        self._changed_elements.update(changed_elements)
        self.flag_transfer_matrices_partial.has_changed = True

    @property
    def transfer_matrices(self):
        if self.flag_allocate_transfer_matrices.has_changed:
            self.flag_allocate_transfer_matrices.has_changed = False
            self.allocate_transfer_matrices()
        if self.flag_transfer_matrices_partial.has_changed:  # update partial
            self.flag_transfer_matrices_partial.has_changed = False
            get_transfer_matrices(self._changed_elements, self._transfer_matrices)
            self._changed_elements.clear()
        if self.flag_transfer_matrices_all.has_changed:  # update all
            self.flag_transfer_matrices_all.has_changed = False
            get_transfer_matrices(self.maincell.elements.values(), self._transfer_matrices)
        return self._transfer_matrices

    def allocate_transfer_matrices(self):
        self._transfer_matrices = np.empty((self.maincell.stepsize.size, matrix_size, matrix_size))
        self._transfer_matrices[0] = np.identity(matrix_size)

    @property
    def twiss(self):
        if self.flag_twissdata.has_changed:
            self.flag_twissdata.has_changed = False
            twissdata(self._twissdata, self.transfer_matrices)
            self._twissdata.s = self.maincell.s
        return self._twissdata
