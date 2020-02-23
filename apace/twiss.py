import numpy as np
from scipy.integrate import trapz, cumtrapz
from .clib import twiss_product, accumulate_array
from .matrix_method import MatrixMethod
from .utils import Signal

CONST_C = 299_792_458
TWO_PI = 2 * np.pi


class Twiss(MatrixMethod):
    """Calculate the Twiss parameter for a given lattice.

    :param Lattice lattice: Lattice to calculate the Twiss parameter for.
    :param start_idx: Index from which the accumulated array is calculated.
                       This index is also used to calculated the initial twiss parameter
                       using the periodicity condition.
    :type start_idx: int, optional
    """

    def __init__(self, lattice, start_idx=0):
        super().__init__(lattice)
        self.lattice = lattice

        self._start_idx = start_idx
        self.start_idx_changed = Signal()  # TODO: is currently unused
        """Gets emitted when the start index changes"""

        self.one_turn_matrix_changed = Signal(
            self.start_idx_changed, self.transfer_matrices_changed
        )
        """Gets emitted when the one turn matrix changes."""
        self.one_turn_matrix_changed.connect(self._on_one_turn_matrix_changed)
        self._one_turn_matrix_needs_update = True
        self._one_turn_matrix = np.empty(0)
        self._accumulated_array = np.empty(0)
        self._term_x = None
        self._term_y = None

        self.twiss_array_changed = Signal(self.one_turn_matrix_changed)
        """Gets emitted when the twiss functions change."""
        self.twiss_array_changed.connect(self._on_twiss_array_changed)
        self._twiss_array_needs_update = True
        self._twiss_array = np.empty(0)
        self._initial_twiss = np.empty(8)

        self.psi_changed = Signal(self.twiss_array_changed)
        """Gets emitted when the betatron phase changes."""
        self.psi_changed.connect(self._on_psi_changed)
        self._psi_needs_update = True
        self._psi_x = np.empty(0)
        self._psi_y = np.empty(0)
        self._tune_x = None
        self._tune_y = None

        self.tune_fractional_changed = Signal(self.one_turn_matrix_changed)
        """Gets emitted when the fractional tune changes."""
        self.tune_fractional_changed.connect(self._on_tune_fractional_changed)
        self._tune_fractional_needs_update = True
        self._tune_x_fractional = None
        self._tune_y_fractional = None
        self._tune_x_fractional_hz = None
        self._tune_y_fractional_hz = None

        self.alpha_c_changed = Signal(
            self.transfer_matrices_changed, self.twiss_array_changed
        )
        self.tune_fractional_changed.connect(self._on_alpha_c_changed)
        """Gets emitted when the natural chormaticity changes."""
        self._alpha_c_needs_update = True
        self._alpha_c = None

        self.chromaticity_changed = Signal(
            self.transfer_matrices_changed, self.twiss_array_changed
        )
        self.tune_fractional_changed.connect(self._on_chromaticity_changed)
        """Gets emitted when the natural chormaticity changes."""
        self._chromaticity_needs_update = True
        self._chromaticity_x = None
        self._chromaticity_y = None

    @property
    def start_idx(self) -> int:
        """Index from which the accumulated array is calculated. This index is also used
        to calculated the initial twiss parameter using the periodicity condition."""
        return self._start_idx

    @start_idx.setter
    def start_idx(self, value):
        if value >= self.n_kicks:
            raise ValueError(
                f"Start index {value} is too high! (Maximum {self.n_kicks})"
            )

        self._start_idx = value
        self.start_idx_changed()

    @property
    def accumulated_array(self) -> np.ndarray:
        """Contains accumulated transfer matrices."""
        if self._one_turn_matrix_needs_update:
            self.update_one_turn_matrix()
        return self._accumulated_array

    @property
    def one_turn_matrix(self) -> np.ndarray:
        """The transfer matrix for a full turn."""
        if self._one_turn_matrix_needs_update:
            self.update_one_turn_matrix()
        return self._one_turn_matrix

    @property
    def term_x(self) -> float:
        """Corresponds to :math:`2 - m_{11}^2 - 2 m_{12} m_{21} - m_{22}^2`, where :math:`m` is the one turn matrix.
        Can be used to calculate the initial :attr:`beta_x` value :math:`\\beta_{x0} = |2 m_{12}| / \\sqrt{term_x}`.
        If :attr:`term_x` > 0, this means that there exists a periodic solution within the horizontal plane."""
        if self._one_turn_matrix_needs_update:
            self.update_one_turn_matrix()
        return self._term_x

    @property
    def term_y(self) -> float:
        """Corresponds to :math:`2 - m_{33}^2 - 2 m_{34} m_{43} - m_{44}^2`, where :math:`m` is the one turn matrix.
        Can be used to calculate the initial :attr:`beta_y` value :math:`\\beta_{y0} = |2 m_{12}| / \\sqrt{term_y}`.
        If :attr:`term_y` > 0, this means that there exists a periodic solution within the vertical plane."""
        if self._one_turn_matrix_needs_update:
            self.update_one_turn_matrix()

        return self._term_y

    @property
    def stable_x(self) -> bool:
        """Periodicity condition :attr:`term_x` > 0 for a stable solution in the horizontal plane."""
        return self.term_x > 0

    @property
    def stable_y(self) -> bool:
        """Periodicity condition :attr:`term_y` > 0 for a stable solution in the vertical plane."""
        return self.term_y > 0

    @property
    def stable(self) -> bool:
        """Periodicity condition :attr:`term_x` > 0 and :attr:`term_y` > 0 for a stable solution in both planes."""
        return self.term_x > 0 and self.term_y > 0

    def update_one_turn_matrix(self):
        """Manually update the one turn matrix and the accumulated array."""
        matrix_array = self.transfer_matrices
        if self._accumulated_array.shape[0] != self.n_kicks:
            self._accumulated_array = np.empty(matrix_array.shape)

        accumulate_array(matrix_array, self._accumulated_array, self.start_idx)
        self._one_turn_matrix = m = self._accumulated_array[self.start_idx - 1]
        self._term_x = 2 - m[0, 0] ** 2 - 2 * m[0, 1] * m[1, 0] - m[1, 1] ** 2
        self._term_y = 2 - m[2, 2] ** 2 - 2 * m[2, 3] * m[3, 2] - m[3, 3] ** 2
        self._one_turn_matrix_needs_update = False

    def _on_one_turn_matrix_changed(self):
        self._one_turn_matrix_needs_update = True

    @property
    def initial_twiss(self) -> np.ndarray:
        """Array containing the initial twiss parameter."""
        if self._twiss_array_needs_update:
            self.update_twiss_array()
        return self._initial_twiss

    @property
    def twiss_array(self) -> np.ndarray:
        """Contains the twiss parameter."""
        if self._twiss_array_needs_update:
            self.update_twiss_array()
        return self._twiss_array

    def update_twiss_array(self):
        """Manually update the twiss_array."""
        n_points = self.n_points
        if self._twiss_array.shape[0] != n_points:
            self._twiss_array = np.empty((8, n_points))

        if not self.stable:  # TODO: replace with warning
            print(
                f"Horizontal plane stability: {self.stable_x}\n"
                f"Vertical plane stability: {self.stable_y}"
            )
            return

        m = self.one_turn_matrix
        beta_x0 = np.abs(2 * m[0, 1]) / np.sqrt(self.term_x)
        alpha_x0 = (m[0, 0] - m[1, 1]) / (2 * m[0, 1]) * beta_x0
        gamma_x0 = (1 + alpha_x0 ** 2) / beta_x0
        beta_y0 = np.abs(2 * m[2, 3]) / np.sqrt(self.term_y)
        alpha_y0 = (m[2, 2] - m[3, 3]) / (2 * m[2, 3]) * beta_y0
        gamma_y0 = (1 + alpha_y0 ** 2) / beta_y0

        # TODO: Wille seems to be wrong, investigate!
        # eta_x_dds0 = (m[1, 0] * m[0, 5] + m[1, 5] * (1 - m[0, 0])) / (2 - m[0, 0] - m[1, 1])
        # eta_x0 = (m[0, 1] * eta_x_dds0 + m[0, 5]) / (1 - m[1, 1])

        eta_x0, eta_x_dds0 = (
            (m[0, 5] * (1 - m[1, 1]) + m[0, 1] * m[1, 5]) / (2 - m[0, 0] - m[1, 1]),
            (m[1, 5] * (1 - m[0, 0]) + m[1, 0] * m[0, 5]) / (2 - m[0, 0] - m[1, 1]),
        )

        self._initial_twiss[:] = (
            beta_x0,
            beta_y0,
            alpha_x0,
            alpha_y0,
            gamma_x0,
            gamma_y0,
            eta_x0,
            eta_x_dds0,
        )
        twiss_product(
            self.accumulated_array,
            self._initial_twiss,
            self._twiss_array,
            self.start_idx,
        )

        self._twiss_array_needs_update = False

    def _on_twiss_array_changed(self):
        self._twiss_array_needs_update = True

    @property
    def beta_x(self) -> np.ndarray:
        """Horizontal beta function."""
        return self.twiss_array[0]

    @property
    def beta_y(self) -> np.ndarray:
        """Vertical beta function."""
        return self.twiss_array[1]

    @property
    def alpha_x(self) -> np.ndarray:
        """Horizontal alpha function."""
        return self.twiss_array[2]

    @property
    def alpha_y(self) -> np.ndarray:
        """Vertical alpha function."""
        return self.twiss_array[3]

    @property
    def gamma_x(self) -> np.ndarray:
        """Horizontal gamma function."""
        return self.twiss_array[4]

    @property
    def gamma_y(self) -> np.ndarray:
        """Vertical gamma function."""
        return self.twiss_array[5]

    @property
    def eta_x(self) -> np.ndarray:
        """Horizontal dispersion function."""
        return self.twiss_array[6]

    @property
    def eta_x_dds(self) -> np.ndarray:
        """Derivative of the horizontal dispersion function with respect to the orbit position s."""
        return self.twiss_array[7]

    @property
    def psi_x(self) -> np.ndarray:
        """Horizontal betatron phase."""
        if self._psi_needs_update:
            self.update_betatron_phase()
        return self._psi_x

    @property
    def psi_y(self) -> np.ndarray:
        """Vertical betatron phase."""
        if self._psi_needs_update:
            self.update_betatron_phase()
        return self._psi_y

    @property
    def tune_x(self) -> float:
        """Horizontal tune. Corresponds to psi_x[-1] / 2 pi. Strongly depends on the selected step size."""
        if self._psi_needs_update:
            self.update_betatron_phase()
        return self._tune_x

    @property
    def tune_y(self) -> float:
        """Vertical tune. Corresponds to psi_y[-1] / 2 pi. Strongly depends on the selected step size."""
        if self._psi_needs_update:
            self.update_betatron_phase()
        return self._tune_y

    def update_betatron_phase(self):
        """Manually update the betatron phase psi and the tune."""
        size = self.accumulated_array.shape[0]
        if self._psi_x.shape[0] != size:
            self._psi_x = np.empty(size)
            self._psi_y = np.empty(size)

        beta_x_inverse = 1 / self.beta_x
        beta_y_inverse = 1 / self.beta_y
        # TODO: use faster integration!
        # TODO: question: is pos=0 weighted doubled because start/end are same point?
        self._psi_x = cumtrapz(beta_x_inverse, self.s, initial=0)
        self._psi_y = cumtrapz(beta_y_inverse, self.s, initial=0)
        self._tune_x = self._psi_x[-1] / TWO_PI
        self._tune_y = self._psi_y[-1] / TWO_PI
        self._psi_needs_update = False

    def _on_psi_changed(self):
        self._psi_needs_update = True

    @property
    def tune_x_fractional(self) -> float:
        """Fractional part of the horizontal tune.
        Gets calculated from the one turn matrix.
        """
        if self._tune_fractional_needs_update:
            self.update_fractional_tune()
        return self._tune_x_fractional

    @property
    def tune_y_fractional(self) -> float:
        """Fractional part of the vertical tune.
        Gets calculated from the one turn matrix.
        """
        if self._tune_fractional_needs_update:
            self.update_fractional_tune()
        return self._tune_y_fractional

    @property
    def tune_x_fractional_hz(self) -> float:
        """Fractional part of the horizontal tune in Hz."""
        if self._tune_fractional_needs_update:
            self.update_fractional_tune()
        return self._tune_x_fractional_hz

    @property
    def tune_y_fractional_hz(self) -> float:
        """Fractional part of the vertical tune in Hz."""
        if self._tune_fractional_needs_update:
            self.update_fractional_tune()
        return self._tune_y_fractional_hz

    def update_fractional_tune(self):
        """Manually update the fractional tune."""
        m = self.one_turn_matrix
        self._tune_x_fractional = np.arccos((m[0, 0] + m[1, 1]) / 2) / TWO_PI
        self._tune_y_fractional = np.arccos((m[2, 2] + m[3, 3]) / 2) / TWO_PI
        tmp = self.velocity / self.lattice.length
        self._tune_x_fractional_hz = self._tune_x_fractional * tmp
        self._tune_y_fractional_hz = self._tune_y_fractional * tmp
        self._tune_fractional_needs_update = False

    def _on_tune_fractional_changed(self):
        self._tune_fractional_needs_update = True

    @property
    def alpha_c(self) -> float:
        """Momentum Compaction Factor. Depends on `n_kicks`"""
        if self._alpha_c_needs_update:
            self.update_alpha_c()
        return self._alpha_c

    def update_alpha_c(self):
        """Manually update the Momentum Compaction Factor."""
        length = self.lattice.length
        self._alpha_c = 1 / length * trapz(self.k0 * self.eta_x[1:], self.s[1:])

    def _on_alpha_c_changed(self):
        self._alpha_c_needs_update = True

    @property
    def chromaticity_x(self) -> float:
        """Natural Horizontal Chromaticity. Depends on `n_kicks`"""
        if self._chromaticity_needs_update:
            self.update_chromaticity()
        return self._chromaticity_x

    @property
    def chromaticity_y(self) -> float:
        """Natural Vertical Chromaticity. Depends on `n_kicks`"""
        if self._chromaticity_needs_update:
            self.update_chromaticity()
        return self._chromaticity_y

    def update_chromaticity(self):
        """Manually update the natural chromaticity."""
        const = 1 / 4 / np.pi
        self._chromaticity_x = -const * trapz(self.k1 * self.beta_x[1:], self.s[1:])
        self._chromaticity_y = +const * trapz(self.k1 * self.beta_y[1:], self.s[1:])

    def _on_chromaticity_changed(self):
        self._chromaticity_needs_update = True

    def beta_x_int(self, positions) -> np.ndarray:
        """Linear interpolated :attr:`beta_x` for given orbit positions.

        :param array_like positions: The orbit position at which to evaluate the interpolated values.
        :return: Interpolated horizontal beta function.
        """
        return np.interp(positions, self.s, self.beta_x)

    def beta_y_int(self, positions) -> np.ndarray:
        """Linear interpolated :attr:`beta_y` for given orbit positions.

        :param array_like positions: The orbit position at which to evaluate the interpolated values.
        :return: Interpolated vertical beta function.
        """
        return np.interp(positions, self.s, self.beta_x)
