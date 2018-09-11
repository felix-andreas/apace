import sys

sys.path.append('..')  # adds module to PYTHONPATH

import numpy as np
import elements as el

Q1 = el.Quad('Q1', length=2)
B1 = el.Bend('B1', length=1, angle=np.pi / 4)
Q2 = el.Quad('Q2', length=2)
D1 = el.Drift('D1', length=1)
FODO = el.Line('FODO-cell', [Q1, D1, B1, D1, Q2, D1, B1, D1])
idleline = el.Line('idle-line',  [])
ring = el.Line('FODO-ring',[FODO] * 4)

fig = el.plotting.floor_plan(ring)
fig.savefig('floorplan.pdf')