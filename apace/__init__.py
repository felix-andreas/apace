"""
apace: Another Particle Accelerator Code
========================================

**apace** is yet another particle accelerator code designed for the optimization of 
beam optics. It is available as Python package and aims to provide a convenient and 
straightforward API to make use of Python's numerous scientific libraries.

Documentation is available at: https://apace.readthedocs.io

Main Features
-------------

    - Serialize and deserialize lattice files into Python objects.
    - Fast calculation of Twiss parameter.
    - Tracking (Experimental non-linear tracking).
    - Matplotlib convenience functions to draw magnetic lattice.

"""

from .__about__ import __license__, __version__
from .classes import (
    Base,
    Element,
    Drift,
    Dipole,
    Quadrupole,
    Sextupole,
    Octupole,
    Lattice,
)
from .matrixmethod import MatrixMethod
from .twiss import Twiss
from .tracking_matrix import TrackingMatrix
from .distributions import distribution
from .utils import Signal
from .exceptions import AmbiguousNameError, UnstableLatticeError

__all__ = [
    "__version__",
    "__license__",
    "Base",
    "Element",
    "Drift",
    "Dipole",
    "Quadrupole",
    "Sextupole",
    "Octupole",
    "Lattice",
    "MatrixMethod",
    "Twiss",
    "distribution",
    "TrackingMatrix",
    "Signal",
    "AmbiguousNameError",
    "UnstableLatticeError",
]

#  (taken from httpx)
__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", __name__)
