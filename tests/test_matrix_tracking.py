import elements as el

fodo = el.read_lattice_file_json('tests/data/lattices/FODO-lattice.json')
lin = el.LinBeamDyn(fodo)

N_PARTICLES = 10
N_TURNS = 10000
particles = el.create_particle_distribution(N_PARTICLES, x='uniform', x_width=0.02, x_center=0.01)
tracking_data = el.matrix_tracking(lin, particles, N_TURNS)


def test_tune():
    import numpy as np
    from scipy.fftpack import fft
    period_time = fodo.length / 299_792_458
    freq = np.linspace(0.0, 1.0 / (2.0 * period_time), N_TURNS // 2)
    fft_tracking = 2.0 / N_TURNS * np.abs(fft(tracking_data[:, 0, -1])[:N_TURNS // 2])
    tune_kHz = freq[np.argmax(fft_tracking)] / 1e3
    tune_fractional = tune_kHz * period_time * 1e3
    assert 643 == round(tune_kHz)
    assert 0.8970 == round(1 - tune_fractional , 4)
