import apace as ap
from apace.plot import plot_twiss, draw_elements, draw_sub_lattices
import matplotlib.pyplot as plt

import os

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, "data", "lattices", "fodo_ring.json")


def test_plot():
    lattice = ap.load_lattice(file_path)
    twiss = ap.Twiss(lattice)
    fig, _ = plot_twiss(twiss)
    draw_elements(lattice)
    draw_sub_lattices(lattice)
    fig.savefig("/tmp/out.pdf")

