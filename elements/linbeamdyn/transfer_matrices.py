import numpy as np
from ..classes import Bend, Quad

MATRIX_SIZE = 6
IDENTITY = np.identity(MATRIX_SIZE)
C = 299_792_458 ** 2
C_SQUARED = C ** 2


def get_transfer_matrices(elements, matrix_array, velocity=C):
    for element in elements:
        pos = element.positions  # pos in matrix array
        n_kicks = element.n_kicks

        if isinstance(element, Quad) and element.k1:  # Quad with k != 0
            sqk = np.sqrt(np.absolute(element.k1))
            om = sqk * element.step_size
            sin = np.sin(om)
            cos = np.cos(om)
            sinh = np.sinh(om)
            cosh = np.cosh(om)
            if element.k1 > 0:  # k > horizontal focusing
                matrix_array[pos] = [
                    [cos, 1 / sqk * sin, 0, 0, 0, 0],
                    [-sqk * sin, cos, 0, 0, 0, 0],
                    [0, 0, cosh, 1 / sqk * sinh, 0, 0],
                    [0, 0, sqk * sinh, cosh, 0, 0],
                    [0, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 1]
                ]
            else:  # k < vertical focusing
                matrix_array[pos] = [
                    [cosh, 1 / sqk * sinh, 0, 0, 0, 0],
                    [sqk * sinh, cosh, 0, 0, 0, 0],
                    [0, 0, cos, 1 / sqk * sin, 0, 0],
                    [0, 0, -sqk * sin, cos, 0, 0],
                    [0, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 1]
                ]

        elif isinstance(element, Bend) and element.angle:  # Bend with angle != 0
            phi = element.step_size / element.radius
            sin = np.sin(phi)
            cos = np.cos(phi)
            radius = element.radius
            kappa_x = 1 / radius
            matrix_array[pos] = [
                [cos, element.radius * sin, 0, 0, 0, element.radius * (1 - cos)],
                [-kappa_x * sin, cos, 0, 0, 0, sin],
                [0, 0, 1, element.step_size, 0, 0],
                [0, 0, 0, 1, 0, 0],
                [-sin, (cos - 1) * radius, 0, 0, 1, (sin - phi) * radius],
                [0, 0, 0, 0, 0, 1]
            ]

            if element.e1:
                tan_r1 = np.tan(element.e1) / element.radius
                matrix_edge_1 = IDENTITY.copy()
                matrix_edge_1[1, 0], matrix_edge_1[3, 2] = tan_r1, -tan_r1
                matrix_array[pos[::n_kicks]] = np.dot(matrix_array[pos[0]], matrix_edge_1)

            if element.e2:
                tan_r2 = np.tan(element.e2) / element.radius
                matrix_edge_2 = IDENTITY.copy()
                matrix_edge_2[1, 0], matrix_edge_2[3, 2] = tan_r2, -tan_r2
                matrix_array[pos[n_kicks - 1::n_kicks]] = np.dot(matrix_edge_2, matrix_array[pos[-1]])

        else:  # Drifts and others
            matrix = IDENTITY.copy()
            matrix[0, 1] = matrix[2, 3] = element.step_size
            matrix_array[pos] = matrix

        if velocity < C:
            gamma = 1 / np.sqrt(1 - velocity ** 2 / C_SQUARED)
            matrix[4, 5] += element.step_size / gamma ** 2
