# apace
[![Python Version](https://img.shields.io/pypi/pyversions/apace)](https://pypi.org/project/apace/)
[![PyPI](https://img.shields.io/pypi/v/apace.svg)](https://pypi.org/project/apace/)
[![CI](https://github.com/andreasfelix/apace/workflows/CI/badge.svg)](https://github.com/andreasfelix/apace/actions?query=workflow%3ACI)
[![Docs](https://readthedocs.org/projects/apace/badge/?version=latest)](https://apace.readthedocs.io)

**apace** is yet **a**nother **p**article **a**ccelerator **c**od**e** designed for the optimization of beam optics. It is available as Python package and aims to provide a convenient and straightforward API to make use of Python's numerous scientific libraries.


## Installing
Install and update using pip or pipenv:

```sh
pip install -U apace
```

## Requirements
- Python 3.6 or higher (CPython or PyPy)
- CFFI 1.0.0 or higher
- NumPy/SciPy
- Matplotlib


## A Simple Example
Import apace:
```python
import apace as ap
```

Create a ring consisting out of 8 FODO cells:
```python
d1 = ap.Drift('D1', length=0.55)
b1 = ap.Bend('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
q1 = ap.Quad('Q1', length=0.2, k1=1.2)
q2 = ap.Quad('Q2', length=0.4, k1=-1.2)
fodo = ap.Cell('FODO', [q1, d1, b1, d1, q2, d1, b1, d1, q1])
ring = ap.Cell('RING', [fodo] * 8)
```
 
Calculate the Twiss parameters:
```python
twiss = ap.Twiss(ring)
```

Plot horizontal and vertical beta functions using matplotlib:
```python
import matplotlib.pyplot as plt
plt.plot(twiss.s, twiss.beta_x, twiss.beta_y, twiss.eta_x)
```

## License
[GNU General Public License v3.0](https://github.com/andreasfelix/apace/blob/master/LICENSE)

