from .transfer_matrices import get_transfer_matrices, matrix_size
import numpy as np
from .twiss import twissdata
from ..classes import PropertyTrigger


class LinBeamDyn:
    def __init__(self, mainline):
        """
        Creates
        Args:
            Mainline:
        """
        self.mainline = mainline
        self._changed_elements = set()

        # properties
        self._transfer_matrices = None
        self.trigger_allocate_transfer_matrices = PropertyTrigger(depends_on=self.mainline.stepsize_trigger)
        self.trigger_transfer_matrices_all = PropertyTrigger(depends_on=self.trigger_allocate_transfer_matrices)
        self.trigger_transfer_matrices_partial = PropertyTrigger(initial_state = False)
        self.trigger_twissdata = PropertyTrigger(depends_on=[self.trigger_transfer_matrices_all,
                                                             self.trigger_transfer_matrices_partial])
        self._twissdata = None
        self._trackingdata = None
        self.twissdata_changed = True

    def changed_elements(self, changed_elements):
        self._changed_elements.update(changed_elements)
        self.trigger_transfer_matrices_partial.changed = True


    @property
    def transfer_matrices(self):
        if self.trigger_allocate_transfer_matrices.changed:
            self.trigger_allocate_transfer_matrices.changed = False
            self.allocate_transfer_matrices()
        if self.trigger_transfer_matrices_partial.changed: # update partial
            self.trigger_transfer_matrices_partial.changed = False
            get_transfer_matrices(self._changed_elements, self._transfer_matrices)
            self._changed_elements.clear()
        if self.trigger_transfer_matrices_all.changed: # update all
            self.trigger_transfer_matrices_all.changed = False
            get_transfer_matrices(self.mainline.elements, self._transfer_matrices)
        return self._transfer_matrices

    def allocate_transfer_matrices(self):
        self._transfer_matrices = np.empty((self.mainline.stepsize.size, matrix_size, matrix_size))
        self._transfer_matrices[0] = np.identity(matrix_size)

    @property
    def twiss(self):
        if self.trigger_twissdata.changed:
            self.trigger_twissdata.changed = False
            self._twissdata = twissdata(self.transfer_matrices)
            self._twissdata.s = self.mainline.s
        return self._twissdata