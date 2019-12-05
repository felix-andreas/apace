import apace as ap
from apace.plot import plot_lattice
import matplotlib.pyplot as plt
import numpy as np

D1 = ap.Drift('D1', length=0.55)
d1 = ap.Drift('D1', length=0.55)
b1 = ap.Dipole('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
q1 = ap.Quadrupole('Q1', length=0.2, k1=1.2)
q2 = ap.Quadrupole('Q2', length=0.4, k1=-1.2)
fodo_cell = ap.Lattice('FODO', [q1, d1, b1, d1, q2, d1, b1, d1, q1])
fodo_ring = ap.Lattice('RING', [fodo_cell] * 8)


np.set_printoptions(precision=3)

twiss = ap.Twiss(fodo_ring, start_idx=0)
plot_lattice(twiss, ring)
plt.savefig('/tmp/twiss_plot.pdf')
