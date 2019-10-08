import elements as el

def test_io():
    file_path = 'tests/data/lattices/FODO-lattice.json'
    line = el.read_lattice_file_json(file_path)
    el.save_lattice_file_json(line)
    fodo = line.cells['fodo']
    Q1 = line.elements['Q1']
    B1 = line.elements['B1']
    lin = el.LinBeamDyn(line)

