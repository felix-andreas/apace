import os
import apace as ap

import matplotlib.pyplot as plt

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, 'lattices', 'fodo_ring.json')
fodo = ap.load_lattice(file_path)
twiss = ap.Twiss(fodo)
plt.plot(twiss.s, twiss.beta_x)
plt.show()
# plt.savefig('out.pdf')
# lattice.print_tree()
# from apace import as_json
# print(as_json(lattice, indent=2))
