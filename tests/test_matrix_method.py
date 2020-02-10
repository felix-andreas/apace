import os
import numpy as np
import apace as ap

BASE_PATH = os.path.dirname(__file__)
FILE_PATH = os.path.join(BASE_PATH, "data", "lattices", "fodo_ring.json")


def test_angle_k1():
    lattice = ap.Lattice.from_file(FILE_PATH)
    b1 = lattice["B1"]
    q1 = lattice["Q1"]
    matrix_method = ap.MatrixMethod(lattice)
    b1_indices = matrix_method.element_indices[b1]
    q1_indices = matrix_method.element_indices[q1]
    assert np.all(b1.k0 == matrix_method.k0[b1_indices])
    assert np.all(q1.k1 == matrix_method.k1[q1_indices])
    assert np.all(0 == matrix_method.k1[b1_indices])
    assert np.all(0 == matrix_method.k0[q1_indices])
