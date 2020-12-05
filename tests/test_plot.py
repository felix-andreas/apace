import pytest
import apace as ap
from apace.plot import (
    plot_twiss,
    draw_elements,
    draw_sub_lattices,
    floor_plan,
    TwissPlot,
)
import matplotlib.pyplot as plt

# TODO: maybe it is better to use a fixture (e.g. save_plots) instead of a maker
#       this way the plotting functions are still tested, but nothing is written to disk
@pytest.mark.slow
def test_draw_elements(fodo_ring, test_output_dir):
    twiss = ap.Twiss(fodo_ring)
    fig, ax = plt.subplots()
    plot_twiss(ax, twiss)
    draw_elements(ax, fodo_ring, location="top")
    draw_sub_lattices(ax, fodo_ring)
    fig.tight_layout()
    fig.savefig(test_output_dir / "test_draw_elements.svg")


@pytest.mark.slow
def test_TwissPlot(fodo_ring, test_output_dir):
    twiss = ap.Twiss(fodo_ring)
    TwissPlot(twiss).fig.savefig(test_output_dir / "test_TwissPlot.svg")


@pytest.mark.slow
def test_floor_plan(fodo_ring, test_output_dir):
    _, ax = plt.subplots()
    ax = floor_plan(fodo_ring, ax=ax)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(test_output_dir / "test_floor_plan.svg")
