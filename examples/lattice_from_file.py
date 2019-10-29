import os
import elements as el

import matplotlib.pyplot as plt

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, 'lattices', 'FODO-lattice.json')
fodo = el.read_lattice_file(file_path)
twiss = el.Twiss(fodo)
plt.plot(twiss.s, twiss.beta_x)
plt.show()
# plt.savefig('out.pdf')
# lattice.print_tree()
# from elements import as_json
# print(as_json(lattice, indent=2))
