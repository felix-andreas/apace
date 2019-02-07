from elements.linbeamdyn import LinBeamDyn
from elements.lattice_file import read_lattice_file_json

import matplotlib.pyplot as plt

lattice = read_lattice_file_json("../../lattices/BII_2016-06-10_user_Sym_noID_DesignLattice1996.json")
lin = LinBeamDyn(lattice)
plt.plot(lin.twiss.s, lin.twiss.betax)
plt.savefig('asdfasd.pdf')
# lattice.print_tree()
print('hi')
from elements import as_json

print(as_json(lattice, indent=2))
