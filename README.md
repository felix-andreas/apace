<img src="images/icons/svg/logo.svg" width="64" height="64" align="left"/>

# apace
Depends on Python 3.7 

## Usage
import apace
```python
import apace as ap
```

### Linear Beam Dynamics
Import the linear beam dynamics module:
```python
from apace.linbeamdyn import LinBeamDyn
```

Create a ring consting out of FODO cells:  
```python
D1 = ap.Drift('D1', length=0.55)
Q1 = ap.Quad('Q1', length=0.2, k1=1.2)
B1 = ap.Bend('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
Q2 = ap.Quad('Q2', length=0.4, k1=-1.2)
fodo = ap.Line('fodo-cell', [Q1, D1, B1, D1, Q2, D1, B1, D1, Q1])
ring = ap.Mainline('fodo-ring', [fodo] * 8)
```

Get twiss parameters:
```python
twiss = ap.Twiss(ring)
```


Plot twissfunctions:
```python
plot(twiss.s, twiss.beta_x, twiss.beta_y, twiss.eta_x)
```
