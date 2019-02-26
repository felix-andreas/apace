import elements as el
import os

filepath = os.path.expanduser(f'{el.ROOT_DIR}/../examples/lattices/FODO-lattice.json')
line = el.read_lattice_file_json(filepath)
fodo = line.cells["fodo"]
print(fodo.length)
Q1 = line.elements["Q1"]
B1 = line.elements["B1"]
lin = el.LinBeamDyn(line)


import matplotlib.pyplot as plt
from elements.plotting import plot_lattice

plot_lattice(lin, etax_scale=1, path="out.pdf")


