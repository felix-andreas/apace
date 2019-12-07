import os

import apace as ap

BASE_PATH = os.path.dirname(__file__)
FILE_PATH = os.path.join(BASE_PATH, "data", "lattices", "fodo_ring.json")


# TODO: fix linter/mypy erros
# https://stackoverflow.com/questions/59187502/mypy-dict-containing-instances-of-different-subclasses
def test_attributes():
    fodo = ap.load_lattice(FILE_PATH)
    d1 = fodo.elements["D1"]
    assert isinstance(d1, ap.Drift)
    assert 0.55 == fodo.elements["D1"].length

    b1: ap.Dipole = fodo.elements["B1"]
    assert isinstance(b1, ap.Dipole)
    assert 0.392701 == fodo.elements["B1"].angle
    assert 0.1963505 == fodo.elements["B1"].e1
    assert 0.1963505 == fodo.elements["B1"].e2
    assert 1.5 == fodo.elements["B1"].length

    q1 = fodo.elements["Q1"]
    assert isinstance(q1, ap.Quadrupole)
    assert 0.2 == fodo.elements["Q1"].length
    assert 1.2 == fodo.elements["Q1"].k1

    q2 = fodo.elements["Q2"]
    assert isinstance(q2, ap.Quadrupole)
    assert 0.4 == fodo.elements["Q2"].length
    assert -1.2 == fodo.elements["Q2"].k1

    fodo_cell = fodo.sub_lattices["FODO"]
    assert isinstance(fodo_cell, ap.Lattice)
    assert 6.0 == fodo_cell.length

    assert isinstance(fodo, ap.Lattice)
    assert 48 == fodo.length


def test_save_lattice():
    fodo = ap.load_lattice(FILE_PATH)
    path = "/tmp/tmp_lattice.json"
    ap.save_lattice(fodo, path)
    lattice = ap.load_lattice(path)
    assert fodo.length == lattice.length
    assert len(fodo.elements) == len(lattice.elements)
    assert len(fodo.sub_lattices) == len(lattice.sub_lattices)
