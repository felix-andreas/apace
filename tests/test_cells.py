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


def test_add_remove_objects():
    e1 = ap.Element('e1', length=1)
    e2 = ap.Element('e2', length=1)
    cell = ap.Cell('cell')
    cell_2 = ap.Cell('Main Cell', [cell] * 2)

    assert 0 == cell_2.length

    cell.add(e1)
    assert [e1] == cell.tree
    assert 2 == cell_2.length

    cell.add(e2, pos=-1)
    assert [e2, e1] == cell.tree
    assert 4 == cell_2.length

    cell.add([e1, e2], pos=0)  # add list
    assert [e1, e2, e2, e1] == cell.tree
    assert 8 == cell_2.length

    cell.add((e1,), pos=-2)  # add tuple
    assert [e1, e2, e1, e2, e1] == cell.tree
    assert 10 == cell_2.length

    cell.remove(2)
    assert [e1, e2, e2, e1] == cell.tree
    assert 8 == cell_2.length

    cell.remove(-3, 2)
    assert [e1, e1] == cell.tree
    assert 4 == cell_2.length
