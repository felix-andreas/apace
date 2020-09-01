import apace as ap


def test_tune(fodo_ring):
    import numpy as np
    from scipy.fftpack import fft

    n_particles = 10
    n_turns = 10000

    dist = ap.distribution(n_particles, x_dist="uniform", x_width=0.02, x_center=0.01)
    tracking = ap.TrackingMatrix(fodo_ring, dist, turns=n_turns, watch_points=[0])
    period_time = fodo_ring.length / 299_792_458
    freq = np.linspace(0.0, 1.0 / (2.0 * period_time), n_turns // 2)
    tmp = tracking.particle_trajectories[:, 0, -1]
    fft_tracking = 2.0 / n_turns * np.abs(fft(tmp))[: n_turns // 2]
    tune_khz = freq[np.argmax(fft_tracking)] / 1e3
    tune_fractional = tune_khz * period_time * 1e3
    assert 643 == round(tune_khz)
    assert 0.8970 == round(1 - tune_fractional, 4)


def test_particle_trajectory(fodo_ring):
    """Compare particle trajectory from matrix tracking x(s) with particle trajectory
    from beta functions x(s) = sqrt(beta_x * e) * cos(psi_x + psi_x0).
    """
    import numpy as np

    n_particles = 1
    n_turns = 1

    dist = ap.distribution(n_particles, x_dist="uniform", x_center=0.01)
    tracking = ap.TrackingMatrix(fodo_ring, dist, turns=n_turns, watch_points=None)
    twiss = ap.Twiss(fodo_ring)
    x = tracking.x
    beta_x = twiss.beta_x
    psi_x = twiss.psi_x

    np.random.seed(0)
    idx_test = np.random.randint(0, x.shape[0], 10)
    emittance_sqrt = x[0, 0] / (np.sqrt(beta_x[0]) * np.cos(psi_x[0]))
    assert np.allclose(
        x[idx_test, 0],
        emittance_sqrt * np.sqrt(beta_x[idx_test]) * np.cos(psi_x[idx_test]),
        atol=0.001,  # TODO: see issue 66
    )
