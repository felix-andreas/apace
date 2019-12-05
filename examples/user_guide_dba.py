import math
import apace as ap

drift = ap.Drift(name='Drift', length=2.25)
quad = ap.Quadrupole(name='Quadrupole', length=1, k1=0.8)
bend = ap.Dipole('Dipole', length=1, angle=math.pi / 16)
dba_lattice = ap.Lattice('DBA Lattice', [drift, bend, drift, quad, drift, bend, drift])
dba_ring = ap.Lattice('DBA Ring', [dba_lattice] * 16)
