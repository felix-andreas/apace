from elements.linbeamdyn import LinBeamDyn
from elements.readlatticefile import readfile

import plotly
plotly.io.orca.config.executable = '/home/felix/miniconda3/bin/orca'
plotly.io.orca.config.save()

lattice = readfile("../lattices/BII_2016-06-10_user_Sym_noID_DesignLattice1996.lte")
latticedata = LinBeamDyn(lattice)
lattice.print_tree()