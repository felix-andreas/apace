import numpy as np
from ..classes import Bend, Quad

matrix_size = 5

def get_transfer_matrices(elements, matrix_array):
    for element in elements:
        pos = element.positions  # pos in matrix array
        nkicks = element.n_kicks
        # Quads
        if isinstance(element, Quad) and element.k1:  # Quad with k = 0 -> Drift
            sqk = np.sqrt(np.absolute(element.k1))
            om = sqk * element.step_size
            sin = np.sin(om)
            cos = np.cos(om)
            sinh = np.sinh(om)
            cosh = np.cosh(om)
            if element.k1 > 0:  # k > horizontal focussing
                matrix_array[pos] = np.matrix([[cos, 1 / sqk * sin, 0, 0, 0],
                                               [-sqk * sin, cos, 0, 0, 0],
                                               [0, 0, cosh, 1 / sqk * sinh, 0],
                                               [0, 0, sqk * sinh, cosh, 0],
                                               [0, 0, 0, 0, 1]])
            else:  # k < vertical focussing
                matrix_array[pos] = np.matrix([[cosh, 1 / sqk * sinh, 0, 0, 0],
                                               [sqk * sinh, cosh, 0, 0, 0],
                                               [0, 0, cos, 1 / sqk * sin, 0],
                                               [0, 0, -sqk * sin, cos, 0],
                                               [0, 0, 0, 0, 1]])
        # Bends
        elif isinstance(element, Bend) and element.angle:  # Bend with angle = 0 -> Drift
            sin = np.sin(element.step_size / element.radius)
            cos = np.cos(element.step_size / element.radius)
            matrix_array[pos] = np.array([[cos, element.radius * sin, 0, 0, element.radius * (1 - cos)],
                                          [-1 / element.radius * sin, cos, 0, 0, sin],
                                          [0, 0, 1, element.step_size, 0],
                                          [0, 0, 0, 1, 0],
                                          [0, 0, 0, 0, 1]])
            if element.e1:
                tanR1 = np.tan(element.e1) / element.radius
                MEB1 = np.identity(matrix_size)
                MEB1[1, 0], MEB1[3, 2] = tanR1, -tanR1
                matrix_array[pos[::nkicks]] = np.dot(matrix_array[pos[0]], MEB1)
            if element.e2:
                tanR2 = np.tan(element.e2) / element.radius
                MEB2 = np.identity(matrix_size)
                MEB2[1, 0], MEB2[3, 2] = tanR2, -tanR2
                matrix_array[pos[nkicks - 1::nkicks]] = np.dot(MEB2, matrix_array[pos[-1]])
        # Drifts and others
        else:
            matrix = np.identity(matrix_size)
            matrix[0, 1] = matrix[2, 3] = element.step_size
            matrix_array[pos] = matrix
