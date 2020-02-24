import apace as ap
from apace.plot import plot_twiss, draw_lattice, floor_plan
import matplotlib.pyplot as plt


def test_draw_lattice(fodo_ring, tmp_path):
    twiss = ap.Twiss(fodo_ring)
    _, ax = plt.subplots()
    plot_twiss(twiss, ax=ax)
    draw_lattice(fodo_ring)
    plt.tight_layout()
    plt.savefig(tmp_path / "test_draw_lattice.pdf")


def test_floor_plan(fodo_ring, tmp_path):
    _, ax = plt.subplots()
    ax = floor_plan(fodo_ring, ax=ax)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(tmp_path / "apace_test_floor_plan.pdf")
