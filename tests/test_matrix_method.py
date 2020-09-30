import numpy as np
import apace as ap


def test_angle_k1(fodo_cell):
    b1 = fodo_cell["B1"]
    q1 = fodo_cell["Q1"]
    matrix_method = ap.MatrixMethod(fodo_cell)
    b1_indices = matrix_method.element_indices[b1]
    q1_indices = matrix_method.element_indices[q1]
    assert np.all(b1.k0 == matrix_method.k0[b1_indices])
    assert np.all(q1.k1 == matrix_method.k1[q1_indices])
    assert np.all(0 == matrix_method.k1[b1_indices])
    assert np.all(0 == matrix_method.k0[q1_indices])
