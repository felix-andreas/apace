from pathlib import Path
import numpy as np
import apace as ap
from apace.tracking_integration import Tracking
from apace.plot import draw_lattice
import matplotlib.pyplot as plt


def test_quadrupole():
    d1 = ap.Drift("D1", length=5)
    d2 = ap.Drift("D2", length=0.2)
    q = ap.Quadrupole("Q1", length=0.2, k1=1.5)
    s = ap.Sextupole("S1", length=0.4, k2=1000)
    # s = ap.Drift("S1", length=0.4)
    lattice = ap.Lattice("Lattice", [d2, q, d2, s, d1])

    distribution = ap.distribution(
        5, x_dist="uniform", x_width=0.0002, delta_dist="uniform", delta_width=0.2
    )
    tracking = Tracking(lattice)
    s, trajectory = tracking.track(distribution)
    _, ax = plt.subplots(figsize=(20, 5))
    ax.plot(s, trajectory[:, 0])
    plt.ylim(-0.0002, 0.0002)
    draw_lattice(lattice, draw_sub_lattices=False)
    plt.savefig("/tmp/test_quadrupole.pdf")
