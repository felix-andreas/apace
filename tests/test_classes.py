import apace as ap
import pytest


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
    e0 = ap.Element("e0", length=1)
    e1 = ap.Element("e1", length=1)
    e2 = ap.Element("e2", length=1)
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
    assert [1, 5] == l1.indices[l0]


def test_print_tree():
    print()
    drift = ap.Drift("D", length=1)
    nested1 = ap.Lattice("nested1", [drift, drift])
    nested2 = ap.Lattice("nested2", [drift, nested1, drift])
    nested3 = ap.Lattice("nested3", [drift, nested2, drift])
    nested4 = ap.Lattice("nested4", 2 * [nested3])
    nested4.print_tree()
