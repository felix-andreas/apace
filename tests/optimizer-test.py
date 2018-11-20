from elements.linbeamdyn import Latticedata, twissdata, get_transfer_matrices
from elements.lattice_file import read_lattice_file
from elements.optimzer import

lattice = read_lattice_file("../lattices/BII_2016-06-10_user_Sym_noID_DesignLattice1996.lte")
latticedata = Latticedata(lattice)