import sys

sys.path.append('..')  # adds module to PYTHONPATH

import numpy as np
import elements as el

# from elements.linbeamdyn.twissfunctions import get_twissdata

Q1 = el.Quad('Q1', l=2, k1=1)
B1 = el.Bend('B1', l=1, angle=np.pi / 4)
Q2 = el.Quad('Q2', l=2, k1=-1)
D1 = el.Drift('D1', l=1)
FODO = el.Line('FODO-cell', [Q1, D1, B1, D1, Q2, D1, B1, D1])
idleline = el.Line('idle-line', [])
ring = el.Line('FODO-ring', [FODO] * 4)

print(D1.length)
# twisspara = get_twissdata(line)
