import os

import apace as ap

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, 'data', 'lattices', 'fodo_ring.json')
fodo = ap.load_lattice(file_path)


def test_attributes():
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


def test_save_lattice():
    path = '/tmp/tmp_lattice.json'
    ap.save_lattice(fodo, path)
    lattice = ap.load_lattice(path)
    assert fodo.length == lattice.length
    assert len(fodo.elements) == len(lattice.elements)
    assert len(fodo.cells) == len(lattice.cells)
