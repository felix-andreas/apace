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

    cell_1 = ap.Lattice("Lattice", [])
    cell_2 = ap.Lattice("Lattice", [])

    with pytest.raises(ap.AmbiguousNameError):
        ap.Lattice("Lattice", [cell_1, cell_2])
