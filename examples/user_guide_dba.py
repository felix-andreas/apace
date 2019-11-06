import math
import apace as ap

drift = ap.Drift(name='Drift', length=2.25)
quad = ap.Quad(name='Quad', length=1, k1=0.8)
bend = ap.Bend('Bend', length=1, angle=math.pi / 16)
dba_cell = ap.Cell('DBA Cell', [drift, bend, drift, quad, drift, bend, drift])
dba_ring = ap.Cell('DBA Ring', [dba_cell] * 16)
