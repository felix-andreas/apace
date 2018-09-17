import numpy as np
from ..classes import Bend, Quad
from ..utils import Structure

matrix_size = 5


def create_matrix(element, matrix_array, stepsize_array):
    pos = element.pos  # pos in matrix array
    nkicks = element.nkicks
    stepsize_array[pos] = element.stepsize
    # Quads
    if isinstance(element, Quad) and element.k:  # Quad with k = 0 -> Drift
        sqk = np.sqrt(np.absolute(element.k))
        om = sqk * element.stepsize
        sin = np.sin(om)
        cos = np.cos(om)
        sinh = np.sinh(om)
        cosh = np.cosh(om)
        if element.k > 0:  # k > horizontal focustepsizeing
            matrix_array[pos] = np.matrix([[cos, 1 / sqk * sin, 0, 0, 0],
                                           [-sqk * sin, cos, 0, 0, 0],
                                           [0, 0, cosh, 1 / sqk * sinh, 0],
                                           [0, 0, sqk * sinh, cosh, 0],
                                           [0, 0, 0, 0, 1]])
        else:  # k < vertical focustepsizeing
            matrix_array[pos] = np.matrix([[cosh, 1 / sqk * sinh, 0, 0, 0],
                                           [sqk * sinh, cosh, 0, 0, 0],
                                           [0, 0, cos, 1 / sqk * sin, 0],
                                           [0, 0, -sqk * sin, cos, 0],
                                           [0, 0, 0, 0, 1]])
    # Bends
    elif isinstance(element, Bend) and element.angle:  # Bend with angle = 0 -> Drift
        sin = np.sin(element.stepsize / element.r)
        cos = np.cos(element.stepsize / element.r)
        matrix_array[pos] = np.array([[cos, element.r * sin, 0, 0, element.r * (1 - cos)],
                                      [-1 / element.r * sin, cos, 0, 0, sin],
                                      [0, 0, 1, element.stepsize, 0],
                                      [0, 0, 0, 1, 0],
                                      [0, 0, 0, 0, 1]])
        if element.e1:
            tanR1 = np.tan(element.e1) / element.r
            MEB1 = np.identity(matrix_size)
            MEB1[1, 0], MEB1[3, 2] = tanR1, -tanR1
            matrix_array[pos[::nkicks]] = np.dot(matrix_array[pos[0]], MEB1)
        if element.e2:
            tanR2 = np.tan(element.e2) / element.r
            MEB2 = np.identity(matrix_size)
            MEB2[1, 0], MEB2[3, 2] = tanR2, -tanR2
            matrix_array[pos[nkicks - 1::nkicks]] = np.dot(MEB2, matrix_array[pos[-1]])
    # Drifts and others
    else:
        matrix = np.identity(matrix_size)
        matrix[0, 1] = matrix[2, 3] = element.stepsize
        matrix_array[pos] = matrix


class Latticedata:
    def __init__(self, line):
        self.line = line
        self.create_matrix_array()

    def create_matrix_array(self):
        for element in self.line.lattice:  # set element pos to zero
            element.pos = []
        start = 1  # starts with 1 because 0th entry is identity matrix
        for element in self.line.lattice:
            end = start + element.nkicks
            element.pos.extend(list(range(start, end)))
            start = end
        self.steps = end
        self.matrix_array = np.empty((self.steps, matrix_size, matrix_size))
        self.matrix_array[0] = np.identity(matrix_size)
        self.stepsize = np.empty((self.steps))
        self.stepsize[0] = 0
        for element in self.line.elements:
            create_matrix(element, self.matrix_array, self.stepsize)
        self.s = np.add.accumulate(self.stepsize)
