import elements as el
import os

if __name__ == '__main__':
    file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../examples/lattices/FODO-lattice.json')
    line = el.read_lattice_file_json(file_path)
    el.save_lattice_file_json(line)
    fodo = line.cells["fodo"]
    Q1 = line.elements["Q1"]
    B1 = line.elements["B1"]
    lin = el.LinBeamDyn(line)

