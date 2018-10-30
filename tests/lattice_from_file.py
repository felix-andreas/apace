from elements.linbeamdyn import Latticedata, twissdata, create_matrix
from elements.plotting import plotTwiss
from elements.readlatticefile import readfile

import plotly
plotly.io.orca.config.executable = '/home/felix/miniconda3/bin/orca'
plotly.io.orca.config.save()

lattice = readfile("../lattices/BII_2016-06-10_user_Sym_noID_DesignLattice1996.lte")
latticedata = Latticedata(lattice)
twiss = twissdata(latticedata)
plotTwiss(twiss, lattice, path = 'test.pdf')
import matplotlib.pyplot as plt
import matplotlib as mpl
print(mpl.__version__)
plt.plot(twiss.s, twiss.betax)
plt.plot(twiss.s, twiss.betay)
plt.plot(twiss.s, twiss.etax)
plt.xlim((0,60))
plt.savefig('test2.pdf')