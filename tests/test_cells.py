import apace as ap
import pytest


def test_length_changed():
    drift = ap.Drift('Drift', length=1)
    cell_1 = ap.Cell('Cell', [drift, drift])
    cell_2 = ap.Cell('Cell', [cell_1, cell_1])
    cell_3 = ap.Cell('Cell', [cell_2, cell_2])
    initial_length = cell_3.length
    for i in range(2, 10):
        drift.length += 1
        assert i * initial_length == cell_3.length


def test_unique_names():
    drift_1 = ap.Drift('Drift', length=1)
    drift_2 = ap.Drift('Drift', length=2)

    with pytest.raises(ap.AmbiguousNameError):
        ap.Cell('Cell', [drift_1, drift_2]).update_tree_properties()

    cell_1 = ap.Cell('Cell')
    cell_2 = ap.Cell('Cell')

    with pytest.raises(ap.AmbiguousNameError):
        ap.Cell('Cell', [cell_1, cell_2]).update_tree_properties()
