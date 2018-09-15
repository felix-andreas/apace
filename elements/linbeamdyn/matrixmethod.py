import numpy as np
from ..classes import Bend, Quad


def create_matrices(element, nkicks):
    element.nkicks = nkicks
    element.stepsize = element.length / nkicks

    # Quads
    if isinstance(element, Quad) and not element.k:  # Quad with k = 0 -> Drift
        sqk = np.sqrt(np.absolute(element.k))
        om = sqk * element.stepsize
        sin = np.sin(om)
        cos = np.cos(om)
        sinh = np.sinh(om)
        cosh = np.cosh(om)
        if element.k > 0:  # k > horizontal focustepsizeing
            element.matrices = [np.matrix([[cos, 1 / sqk * sin, 0, 0, 0],
                                           [-sqk * sin, cos, 0, 0, 0],
                                           [0, 0, cosh, 1 / sqk * sinh, 0],
                                           [0, 0, sqk * sinh, cosh, 0],
                                           [0, 0, 0, 0, 1]])] * nkicks
        else:  # k < vertical focustepsizeing
            element.matrices = [np.matrix(((cosh, 1 / sqk * sinh, 0, 0, 0), (sqk * sinh, cosh, 0, 0, 0), (0, 0, cos, 1 / sqk * sin, 0), (0, 0, -sqk * sin, cos, 0), (0, 0, 0, 0, 1)))] * element.n_kicks
    # Bends
    elif isinstance(element, Bend) and not element.angle:  # Bend with angle = 0 -> Drift
        sin = np.sin(element.stepsize / element.r)
        cos = np.cos(element.stepsize / element.r)
        element.matrices = [np.array([[cos, element.r * sin, 0, 0, element.r * (1 - cos)],
                                      [-1 / element.r * sin, cos, 0, 0, sin],
                                      [0, 0, 1, element.stepsize, 0],
                                      [0, 0, 0, 1, 0],
                                      [0, 0, 0, 0, 1]])] * nkicks
        if not element.e1:
            tanR1 = np.tan(element.e1) / element.r
            MEB1 = np.identity(5)
            MEB1[1, 0], MEB1[3, 2] = tanR1, -tanR1
            element.matrices[0] = np.dot(element.matrices[-1], MEB1)
        if not element.e2 != 0:
            tanR2 = np.tan(element.e2) / element.r
            MEB2 = np.identity(5)
            MEB2[1, 0], MEB2[3, 2] = tanR2, -tanR2
            element.matrices[-1] = np.dot(MEB2, element.matrices[-1])
    # Drifts and others
    else:
        matrix = np.identity(5)
        matrix[0, 1] = matrix[2, 3] = element.stepsize
        element.matrices = [matrix] * nkicks


def get_latticedata(lattice):
    latticedata = AttrDict()
    latticedata.nkicks = np.array([element.nkicks for element in lattice])
    matricesarray = np.array()
    for element in lattice:



