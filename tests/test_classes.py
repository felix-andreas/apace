import os

import apace as ap
import pytest

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, 'data', 'lattices', 'FODO-lattice.json')
fodo = ap.read_lattice_file(file_path)


def test_unique_names():
    drift_1 = ap.Drift('Drift', length=1)
    drift_2 = ap.Drift('Drift', length=2)

    with pytest.raises(ap.AmbiguousNameError):
        ap.Cell('Cell', [drift_1, drift_2]).update_tree_properties()


    cell_1 = ap.Cell('Cell')
    cell_2 = ap.Cell('Cell')
    with pytest.raises(ap.AmbiguousNameError):
        ap.Cell('Cell', [cell_1, cell_2]).update_tree_properties()
