import numpy as np
from scipy.fftpack import fft
import matplotlib.pyplot as plt

import elements as el

fodo = el.read_lattice_file_json('lattices/FODO-lattice.json')
lin = el.LinBeamDyn(fodo)

n_particles = 10
n_turns = 100
particles = el.create_particle_distribution(n_particles, x='uniform', x_width=0.02, x_center=0.01)
tracking_data = el.matrix_tracking(lin, particles, n_turns)

freq = np.linspace(0.0, 1.0 / (2.0 * fodo.length / 299_792_458), n_turns // 2)
fft_tracking = 2.0 / n_turns * np.abs(fft(tracking_data[:, 0, -1])[:n_turns // 2])
main_freq = freq[np.argmax(fft_tracking)]

plt.subplot(1, 2, 1)
for i in range(n_particles):
    plt.plot(tracking_data[:, 0, i], tracking_data[:, 1, i], 'o')

plt.xlabel('x / mm')
plt.ylabel('x\'')

plt.subplot(1, 2, 2)
plt.plot(freq, fft_tracking)
plt.xlabel('Freq / Hz')
plt.ylabel('Fourier transform')

plt.tight_layout()
plt.savefig('tracking.pdf')
