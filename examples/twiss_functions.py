import apace as ap
import matplotlib.pyplot as plt

D1 = ap.Drift('D1', length=0.55)
Q1 = ap.Quad('Q1', length=0.2, k1=1.2)
B1 = ap.Bend('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
Q2 = ap.Quad('Q2', length=0.4, k1=-1.2)
fodo = ap.Cell('fodo-cell', [Q1, D1, B1, D1, Q2, D1, B1, D1, Q1])
ring = ap.Cell('fodo-ring', [fodo] * 8)

twiss = ap.Twiss(ring)

plt.plot(twiss.s, twiss.beta_x)
