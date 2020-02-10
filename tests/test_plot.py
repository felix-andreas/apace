import apace as ap
from apace.plot import plot_twiss, draw_lattice, floor_plan
import matplotlib.pyplot as plt

import os

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, "data", "lattices", "fodo_ring.json")
lattice = ap.Lattice.from_file(file_path)
twiss = ap.Twiss(lattice)


def test_draw_lattice():
    _, ax = plt.subplots()
    plot_twiss(twiss, ax=ax)
    draw_lattice(lattice)
    plt.tight_layout()
    plt.savefig("/tmp/apace_test_draw_lattice.pdf")


def test_floor_plan():
    _, ax = plt.subplots()
    ax = floor_plan(lattice, ax=ax)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig("/tmp/apace_test_floor_plan.pdf")
