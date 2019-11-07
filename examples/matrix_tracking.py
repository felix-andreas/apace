import numpy as np
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import os
from math import sqrt

import apace as ap

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, 'lattices', 'fodo_ring.json')
fodo = ap.load_lattice(file_path)

# Example 1: Get tune by Fourier-Transform of particle offset at fixed position
n_particles = 20
n_turns = 30
particles = ap.create_particle_distribution(n_particles, x_dist='uniform', x_width=0.02, x_center=0.01)
matrix_tracking = ap.MatrixTracking(fodo, particles, turns=n_turns)
tracking_data = matrix_tracking.particle_trajectories

freq = np.linspace(0.0, 1.0 / (2.0 * fodo.length / 299_792_458), n_turns // 2)
fft_tracking = 2.0 / n_turns * np.abs(fft(tracking_data[:, 0, -1])[:n_turns // 2])
main_freq = freq[np.argmax(fft_tracking)]

plt.subplot(2, 2, 1)
for i in range(n_particles):
    plt.plot(tracking_data[:, 0, i], tracking_data[:, 1, i], 'o')

plt.xlabel('x / mm')
plt.ylabel('x\'')

plt.subplot(2, 2, 2)
plt.plot(freq, fft_tracking)
plt.xlabel('Freq / Hz')
plt.ylabel('Fourier transform')
plt.axvline(x=main_freq, color='k')

plt.subplot(2, 2, 3)
plt.plot(matrix_tracking.orbit_position, tracking_data[:, 0, -1])
plt.xlabel('horizontal offset / x')
plt.ylabel('orbit position / s')

matrix_tracking = ap.MatrixTracking(fodo, particles, turns=n_turns, position=None)
tracking_data = matrix_tracking.particle_trajectories

plt.subplot(2, 2, 4)
plt.plot(matrix_tracking.orbit_position, tracking_data[:, 0, -1], linewidth=0.5)
plt.xlabel('horizontal offset / x')
plt.ylabel('orbit position / s')

plt.tight_layout()
plt.savefig('/tmp/tracking.pdf')

# Example 2: Plot particle trajectory`
x_width = 0.02
n_turns = 15
dist = ap.create_particle_distribution(20, x_dist='uniform', x_width=x_width)
matrix_tracking = ap.MatrixTracking(fodo, dist, turns=n_turns, position=None)
twiss = ap.Twiss(fodo)

fig, ax = plt.subplots()
ax.plot(matrix_tracking.orbit_position, matrix_tracking.x, linewidth=0.5)
beam_size = np.sqrt(twiss.beta_x) * (x_width / 2 / sqrt(twiss.beta_x[0]))

ax.axvline(x=0, color='k', linestyle='--', linewidth=0.5)
for i in range(n_turns):
    s = twiss.s + fodo.length * i
    ax.plot(s, beam_size, 'k--', s, -beam_size, 'k--', linewidth=0.5)
    ax.axvline(x=fodo.length * (i + 1), color='k', linestyle='--', linewidth=0.5)

fig.tight_layout()
fig.savefig('/tmp/tracking_2.pdf')
