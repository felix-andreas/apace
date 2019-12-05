import apace as ap
from apace.plot import plot_lattice
import matplotlib.pyplot as plt
import numpy as np

D1 = ap.Drift('D1', length=0.55)
Q1 = ap.Quadrupole('Q1', length=0.2, k1=1.2)
B1 = ap.Dipole('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
Q2 = ap.Quadrupole('Q2', length=0.4, k1=-1.2)
fodo = ap.Lattice('fodo-lattice', [Q1, D1, B1, D1, Q2, D1, B1, D1, Q1])
ring = ap.Lattice('fodo-ring', [fodo] * 8)

np.set_printoptions(precision=3)

twiss = ap.Twiss(ring, start_idx=0)
plot_lattice(twiss, ring)
plt.savefig('/tmp/twiss_plot.pdf')
