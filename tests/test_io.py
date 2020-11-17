import apace as ap

# TODO: fix linter/mypy erros
# https://stackoverflow.com/questions/59187502/mypy-dict-containing-instances-of-different-subclasses
def test_attributes(fodo_cell):
    fodo_ring = ap.Lattice("fodo-ring", 8 * [fodo_cell])
    d1 = fodo_ring["D1"]
    assert isinstance(d1, ap.Drift)
    assert 0.55 == fodo_ring["D1"].length

    b1: ap.Dipole = fodo_ring["B1"]
    assert isinstance(b1, ap.Dipole)
    assert 0.392701 == fodo_ring["B1"].angle
    assert 0.1963505 == fodo_ring["B1"].e1
    assert 0.1963505 == fodo_ring["B1"].e2
    assert 1.5 == fodo_ring["B1"].length

    q1 = fodo_ring["Q1"]
    assert isinstance(q1, ap.Quadrupole)
    assert 0.2 == fodo_ring["Q1"].length
    assert 1.2 == fodo_ring["Q1"].k1

    q2 = fodo_ring["Q2"]
    assert isinstance(q2, ap.Quadrupole)
    assert 0.4 == fodo_ring["Q2"].length
    assert -1.2 == fodo_ring["Q2"].k1

    fodo_cell = fodo_ring["FODO"]
    assert isinstance(fodo_cell, ap.Lattice)
    assert 6.0 == fodo_cell.length

    assert isinstance(fodo_ring, ap.Lattice)
    assert 48 == fodo_ring.length


def test_serialize_lattice(fodo_ring):
    fodo_reload = ap.Lattice.from_dict(fodo_ring.as_dict())
    assert fodo_ring.length == fodo_reload.length
    assert len(fodo_ring.elements) == len(fodo_reload.elements)
    assert len(fodo_ring.sub_lattices) == len(fodo_reload.sub_lattices)
