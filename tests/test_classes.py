import os

import apace as ap

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, 'data', 'lattices', 'FODO-lattice.json')
fodo = ap.read_lattice_file(file_path)


def test_uniqueness_of_names():
    drift_1 = ap.Drift('Drift', length=1)
    drift_2 = ap.Drift('Drift', length=2)
    lattice = ap.Cell(())


