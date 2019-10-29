import apace as el
import os

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, 'data', 'lattices', 'FODO-lattice.json')
fodo = el.read_lattice_file(file_path)


def test_tune():
    import numpy as np
    from scipy.fftpack import fft

    n_particles = 10
    n_turns = 10000

    initial_distribution = el.create_particle_distribution(n_particles, x_dist='uniform', x_width=0.02, x_center=0.01)
    matrix_tracking = el.MatrixTracking(fodo, initial_distribution, turns=n_turns, position=0)
    period_time = fodo.length / 299_792_458
    freq = np.linspace(0.0, 1.0 / (2.0 * period_time), n_turns // 2)
    fft_tracking = 2.0 / n_turns * np.abs(fft(matrix_tracking.particle_trajectories[:, 0, -1])[:n_turns // 2])
    tune_khz = freq[np.argmax(fft_tracking)] / 1e3
    tune_fractional = tune_khz * period_time * 1e3
    assert 643 == round(tune_khz)
    assert 0.8970 == round(1 - tune_fractional, 4)


# compare matrix tracking with particle trajectory from beta functions:
# x(s) = sqrt(beta_x * e) * cos(psi_x + psi_0)
def test_matrix_tracking():
    from math import sqrt, cos
    import numpy as np
    n_particles = 1
    n_turns = 1

    initial_distribution = el.create_particle_distribution(n_particles, x_dist='uniform', x_center=0.01)
    matrix_tracking = el.MatrixTracking(fodo, initial_distribution, turns=n_turns, position=None)
    twiss = el.Twiss(fodo)
    x = matrix_tracking.x_trajectory
    beta_x = twiss.beta_x
    psi_x = twiss.psi_x

    low, high = 0, x.shape[0]
    for pos_1 in np.random.randint(low, high, 10):
        for pos_2 in np.random.randint(low, high, 10):
            term_1= x[pos_1, 0] * sqrt(beta_x[pos_2]) * cos(psi_x[pos_2])
            term_2 = x[pos_2, 0] * sqrt(beta_x[pos_1]) * cos(psi_x[pos_1])
            assert abs(term_1 - term_2) < 0.01
