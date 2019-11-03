import apace as ap
import matplotlib.pyplot as plt

d1 = ap.Drift('D1', length=0.55)
b1 = ap.Bend('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
q1 = ap.Quad('Q1', length=0.2, k1=1.2)
q2 = ap.Quad('Q2', length=0.4, k1=-1.2)
fodo = ap.Cell('FODO', [q1, d1, b1, d1, q2, d1, b1, d1, q1])
ring = ap.Cell('RING', [fodo] * 8)

twiss = ap.Twiss(ring)

plt.plot(twiss.s, twiss.beta_x, twiss.s, twiss.beta_y)
plt.show()
