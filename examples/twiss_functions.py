import apace as ap
import matplotlib.pyplot as plt
import numpy as np

D1 = ap.Drift('D1', length=0.55)
Q1 = ap.Quad('Q1', length=0.2, k1=1.2)
B1 = ap.Bend('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
Q2 = ap.Quad('Q2', length=0.4, k1=-1.2)
fodo = ap.Cell('fodo-cell', [Q1, D1, B1, D1, Q2, D1, B1, D1, Q1])
ring = ap.Cell('fodo-ring', [fodo] * 8)

np.set_printoptions(precision=3)

twiss_0 = ap.Twiss(ring, start_idx=0)
twiss_1 = ap.Twiss(ring, start_idx=7)

mat = twiss_1.matrix_method.transfer_matrices[0]
m = twiss_1.accumulated_array[-1]

# print(twiss_0.initial_twiss[6], twiss_0.eta_x[0], twiss_0.eta_x[1])
# print(twiss_1.initial_twiss[6], twiss_1.eta_x[1], twiss_0.eta_x[1])
print(twiss_0.eta_x[-1])
print(twiss_0.eta_x_dds[0])
print(twiss_1.eta_x[1])
print(twiss_1.eta_x_dds[1])
#
# eta_x_dds0 = (m[1, 0] * m[0, 5] + m[1, 5] * (1 - m[0, 0])) / (2 - m[0, 0] - m[1, 1])
# eta_x0 = (m[0, 1] * eta_x_dds0 + m[0, 5]) / (1 - m[1, 1])

print(twiss_0.one_turn_matrix)
print(twiss_0.initial_twiss[6])
print(twiss_1.one_turn_matrix)
print(twiss_1.initial_twiss[6])

# print(twiss_1.accumulated_array[0])
# print(mat @ twiss_0.accumulated_array[-2])
# print(twiss_1.one_turn_matrix @ mat)
#
from apace.plot import plot_lattice
plot_lattice(twiss_1, ring)
plt.savefig('/tmp/twiss_plot.pdf')

