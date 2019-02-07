import elements as el
import os

if __name__ == '__main__':
    filepath = os.path.expanduser('~/git/elements/examples/lattices/FODO-lattice.json')
    line = el.read_lattice_file_json(filepath)
    el.save_lattice_file_json(line, "wosolldassein.json")
    fodo = line.cells["fodo"]
    Q1 = line.elements["Q1"]
    B1 = line.elements["B1"]
    lin = el.LinBeamDyn(line)

