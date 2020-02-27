import apace as ap
from apace.plot import plot_twiss, draw_lattice, floor_plan
import matplotlib.pyplot as plt


def test_draw_lattice(fodo_ring, tmp_path, plots):
    twiss = ap.Twiss(fodo_ring)
    _, ax = plt.subplots()
    plot_twiss(twiss, ax=ax)
    draw_lattice(fodo_ring)
    if plots:
        plt.tight_layout()
        plt.savefig(tmp_path / "test_draw_lattice.pdf")


def test_floor_plan(fodo_ring, tmp_path, plots):
    _, ax = plt.subplots()
    ax = floor_plan(fodo_ring, ax=ax)
    ax.invert_yaxis()
    if plots:
        plt.tight_layout()
        plt.savefig(tmp_path / "apace_test_floor_plan.pdf")
