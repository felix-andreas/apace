import apace as ap
from apace.plot import plot_twiss, draw_lattice
import matplotlib.pyplot as plt

import os

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, "data", "lattices", "fodo_ring.json")


def test_plot():
    lattice = ap.Lattice.from_file(file_path)
    twiss = ap.Twiss(lattice)
    plot_twiss(twiss)
    draw_lattice(lattice)
    plt.tight_layout()
    plt.savefig("/tmp/apace_test_plot.pdf")
