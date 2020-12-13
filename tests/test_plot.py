import apace as ap
from apace.plot import (
    plot_twiss,
    draw_elements,
    draw_sub_lattices,
    floor_plan,
    TwissPlot,
)
import matplotlib.pyplot as plt


def test_draw_elements(fodo_ring, test_output_dir, plot):
    twiss = ap.Twiss(fodo_ring)
    fig, ax = plt.subplots()
    plot_twiss(ax, twiss)
    draw_elements(ax, fodo_ring, location="top")
    draw_sub_lattices(ax, fodo_ring)
    if plot:
        fig.tight_layout()
        fig.savefig(test_output_dir / "test_draw_elements.svg")


def test_TwissPlot(fodo_ring, test_output_dir, plot):
    twiss = ap.Twiss(fodo_ring)
    fig = TwissPlot(twiss).fig
    if plot:
        fig.savefig(test_output_dir / "test_TwissPlot.svg")


def test_floor_plan(fodo_ring, test_output_dir, plot):
    _, ax = plt.subplots()
    ax = floor_plan(ax, fodo_ring)
    ax.invert_yaxis()
    if plot:
        plt.tight_layout()
        plt.savefig(test_output_dir / "test_floor_plan.svg")
