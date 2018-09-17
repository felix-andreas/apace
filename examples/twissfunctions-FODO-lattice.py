import elements as el
from elements.linbeamdyn import Latticedata, twissdata
from elements.plotting import plotTwiss
D1 = el.Drift('D1', l=0.55)
Q1 = el.Quad('Q1', l=0.2, k1=1.2)
B1 = el.Bend('B1', l=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
Q2 = el.Quad('Q2', l=0.4, k1=-1.2)
FODO = el.Line('fodo-cell', [Q1, D1, B1, D1, Q2, D1, B1, D1, Q1])
interFODO = el.Line('inter-Fodo', [FODO] * 10)
ring = el.Mainline('fodo-ring', [FODO])

latticedata = Latticedata(ring)
twiss = twissdata(latticedata)
plotTwiss(twiss, ring, path = 'test.pdf')
