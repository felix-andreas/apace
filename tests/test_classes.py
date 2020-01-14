import numpy as np
from math import pi
import pytest
import apace as ap


def test_length_changed():
    drift = ap.Drift("Drift", length=1)
    cell_1 = ap.Lattice("Cell1", [drift, drift])
    cell_2 = ap.Lattice("Cell2", [cell_1, cell_1])
    cell_3 = ap.Lattice("Cell3", [cell_2, cell_2])
    initial_length = cell_3.length
    for i in range(2, 10):
        drift.length += 1
        print("TEST:", drift.length, cell_3.length)
        assert i * initial_length == cell_3.length


def test_unique_names():
    drift_1 = ap.Drift("Drift", length=1)
    drift_2 = ap.Drift("Drift", length=2)

    with pytest.raises(ap.AmbiguousNameError):
        ap.Lattice("Lattice", [drift_1, drift_2])

    cell_1 = ap.Lattice("cell", [])
    cell_2 = ap.Lattice("cell", [])

    with pytest.raises(ap.AmbiguousNameError):
        ap.Lattice("Lattice", [cell_1, cell_2])


def test_indices():
    e0 = ap.Drift("e0", length=1)
    e1 = ap.Drift("e1", length=1)
    e2 = ap.Drift("e2", length=1)
    l0 = ap.Lattice("l0", (e0, e1, e2))
    assert [0] == l0.indices[e0]
    assert [1] == l0.indices[e1]
    assert [2] == l0.indices[e2]

    l1 = ap.Lattice("l1", (e0, l0, e1, l0, e2))
    # e0, e0, e1, e2, e1, e0, e1, e2, e2
    #  0,  1,  2,  3,  4,  5,  6,  7,  8
    assert [0, 1, 5] == l1.indices[e0]
    assert [2, 4, 6] == l1.indices[e1]
    assert [3, 7, 8] == l1.indices[e2]


def test_attribute_arrays():
    angle = pi / 8
    k1 = 2
    dipole = ap.Dipole("d", length=2, angle=angle)
    quad = ap.Quadrupole("q", length=1, k1=k1)
    lattice = ap.Lattice("Lattice", (dipole, quad))
    assert np.array_equal([angle, 0], lattice.angle_array)
    assert np.array_equal([0, k1], lattice.k1_array)

    angle = pi / 4
    k1 = 4
    dipole.angle = angle
    quad.k1 = k1
    assert np.array_equal([angle, 0], lattice.angle_array)
    assert np.array_equal([0, k1], lattice.k1_array)
