import os

import elements as el

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, 'data', 'lattices', 'FODO-lattice.json')
fodo = el.read_lattice_file(file_path)


def test_save_lattice():
    path = '/tmp/tmp_lattice.json'
    el.save_lattice_file(fodo, path)
    lattice = el.read_lattice_file(path)
    assert fodo.length == lattice.length
    assert len(fodo.elements) == len(lattice.elements)
    assert len(fodo.cells) == len(lattice.cells)


def test_access_by_name():
    assert 0.55 == fodo.elements['D1'].length
    assert 0.2 == fodo.elements['Q1'].length
    assert 1.2 == fodo.elements['Q1'].k1
    assert 0.4 == fodo.elements['Q2'].length
    assert -1.2 == fodo.elements['Q2'].k1
    assert 1.5 == fodo.elements['B1'].length
    assert 0.392701 == fodo.elements['B1'].angle
    assert 0.1963505 == fodo.elements['B1'].e1
    assert 0.1963505 == fodo.elements['B1'].e2
    assert 6.0 == fodo.cells['fodo'].length
    assert 48 == fodo.length
