import numpy as np
from random import randrange
import apace as ap

# FODO circular accelerator from Klaus Wille Chapter 3.13.3
D1 = ap.Drift("D1", length=0.55)
Q1 = ap.Quadrupole("Q1", length=0.2, k1=1.2)
B1 = ap.Dipole("B1", length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
Q2 = ap.Quadrupole("Q2", length=0.4, k1=-1.2)
fodo = ap.Lattice("fodo-lattice", [Q1, D1, B1, D1, Q2, D1, B1, D1, Q1])
ring = ap.Lattice("fodo-ring", [fodo] * 8)

twiss = ap.Twiss(ring)  # a different start_idx should make no difference!
twiss.start_idx = randrange(twiss.n_kicks)


def test_beta():
    beta_x_start = twiss.beta_x[0]
    beta_x_end = twiss.beta_x[-1]
    beta_y_start = twiss.beta_y[0]
    beta_y_end = twiss.beta_y[-1]

    assert twiss.stable
    assert 9.8176 == round(beta_x_start, 4)
    assert 9.8176 == round(beta_x_end, 4)
    assert 1.2376 == round(beta_y_start, 4)
    assert 1.2376 == round(beta_y_end, 4)


def test_dispersion():
    eta_x_start = twiss.eta_x[0]
    eta_x_end = twiss.eta_x[-1]

    assert 3.4187 == round(eta_x_start, 4)
    assert 3.4187 == round(eta_x_end, 4)


def test_tune_integer():
    assert 2 == round(twiss.tune_x)  # depends on number of matrices
    assert 3 == round(twiss.tune_y)  # depends on number of matrices


def test_tune_fractional():
    assert 0.8970 == round(1 - twiss.tune_x_fractional, 4)
    assert 0.5399 == round(1 - twiss.tune_y_fractional, 4)


def test_element_change():
    beta_x_start = twiss.beta_x[0]
    tune_x_initial = twiss.tune_x
    Q1.k1 += 0.25
    assert beta_x_start != twiss.beta_x[0]
    assert tune_x_initial != twiss.tune_x
    Q1.k1 -= 0.25  # set back to avoid failure of other tests


def test_periodic_solution():
    assert twiss.stable
    assert twiss.stable_x
    assert twiss.stable_y

    tmp_k1 = Q1.k1
    Q1.k1 = 0
    assert not twiss.stable
    assert not twiss.stable_x
    assert twiss.stable_y
    Q1.k1 = tmp_k1

    tmp_k1 = Q2.k1
    Q2.k1 = 0
    assert not twiss.stable
    assert twiss.stable_x
    assert not twiss.stable_y
    Q2.k1 = tmp_k1


one_turn = np.array(
    [
        [+0.79784474, -5.91866399, +0.00000000, +0.00000000, +0.00000000, +0.69110258],
        [+0.06140639, +0.79784474, +0.00000000, +0.00000000, +0.00000000, -0.20992831],
        [+0.00000000, +0.00000000, -0.96872070, -0.30710998, +0.00000000, +0.00000000],
        [+0.00000000, +0.00000000, +0.20051513, -0.96872070, +0.00000000, +0.00000000],
        [+0.20992831, -0.69110258, +0.00000000, +0.00000000, +1.00000000, -15.9342232],
        [+0.00000000, +0.00000000, +0.00000000, +0.00000000, +0.00000000, +1.00000000],
    ]
)


def test_one_turn_matrix():  # ony true if one turn matrix is calculated from pos = 0
    twiss_idx_0 = ap.Twiss(ring, start_idx=0)
    assert np.allclose(one_turn, twiss_idx_0.one_turn_matrix)


def test_chromaticity():
    twiss = ap.Twiss(ring)
    print()
    print("chroma_x", twiss.chromaticity_x)
    print("chroma_y", twiss.chromaticity_y)
    # TODO: get reliable reference values
    # TODO: test if it changes when element changes


def test_alpha_c():
    twiss = ap.Twiss(ring)
    print()
    print("alpha_c", twiss.alpha_c)
    # TODO: get reliable reference values
    # TODO: test if it changes when element changes
