from functools import partial
import math
from random import randrange

import numpy as np
import pytest

import apace as ap

allclose_atol = partial(np.allclose, atol=1e-3)

_twiss = None
# Todo: test start_idx with start_idx=randrange(n_elements)
@pytest.fixture
def twiss(fodo_cell):
    # Todo: make sure twiss object is reuseds and avoid scope mismatch
    global _twiss
    if _twiss is None:
        _twiss = ap.Twiss(fodo_cell, steps_per_element=1)
    return _twiss


# Todo: use fodo-cell instead of ring for faster tests
def test_optical_functions(twiss):
    """reference values from madx"""
    assert allclose_atol((9.818, 9.358, 7.068), twiss.beta_x[:3])
    assert allclose_atol((7.068, 9.358, 9.818), twiss.beta_x[-3:])
    assert allclose_atol((1.238, 1.331, 2.130), twiss.beta_y[:3])
    assert allclose_atol((2.130, 1.331, 1.238), twiss.beta_y[-3:])
    assert allclose_atol((0.000, 2.262, 1.902), twiss.alpha_x[:3])
    assert allclose_atol((-1.902, -2.262, 0.000), twiss.alpha_x[-3:])
    assert allclose_atol((-0.000, -0.473, -0.979), twiss.alpha_y[:3])
    assert allclose_atol((0.979, 0.473, 0.000), twiss.alpha_y[-3:])
    assert allclose_atol((3.419, 3.337, 2.889), twiss.eta_x[:3])
    assert allclose_atol((2.889, 3.337, 3.419), twiss.eta_x[-3:])
    assert allclose_atol((0.000, -0.814, -0.814), twiss.eta_x_dds[:3])
    assert allclose_atol((0.814, 0.814, -0.000), twiss.eta_x_dds[-3:])


# TODO: get ref value for emittance
def test_optical_parameters(fodo_cell):
    """Reference values from elegant"""
    # TODO: twiss should only be calculated once!
    twiss = ap.Twiss(fodo_cell, energy=1000, steps_per_meter=20)
    assert math.isclose(0.237, twiss.tune_x, abs_tol=1e-3)
    assert math.isclose(0.317, twiss.tune_y, abs_tol=1e-3)
    # TODO: fix chromaticity has different value than madx or elegant
    # elegant: dnux/dp: -0.0927, dnuy/dp: -0.2438
    #    madx:     dq1: -0.158 ,     dq2: -0.131
    # assert math.isclose(-0.158, twiss.chromaticity_x, abs_tol=1e-3)
    # assert math.isclose(-0.131, twiss.chromaticity_y, abs_tol=1e-3)
    assert math.isclose(0.317, twiss.alpha_c, abs_tol=1e-3)
    assert math.isclose(1.902, twiss.i1, abs_tol=1e-3)
    assert math.isclose(0.206, twiss.i2, abs_tol=1e-3)
    assert math.isclose(0.054, twiss.i3, abs_tol=1e-3)
    assert math.isclose(-0.003, twiss.i4, abs_tol=1e-3)
    assert math.isclose(0.070, twiss.i5, abs_tol=1e-3)


ONE_TURN_MATRIX = np.array(
    [
        [+0.79784474, -5.91866399, +0.00000000, +0.00000000, +0.00000000, +0.69110258],
        [+0.06140639, +0.79784474, +0.00000000, +0.00000000, +0.00000000, -0.20992831],
        [+0.00000000, +0.00000000, -0.96872070, -0.30710998, +0.00000000, +0.00000000],
        [+0.00000000, +0.00000000, +0.20051513, -0.96872070, +0.00000000, +0.00000000],
        [+0.20992831, -0.69110258, +0.00000000, +0.00000000, +1.00000000, -15.9342232],
        [+0.00000000, +0.00000000, +0.00000000, +0.00000000, +0.00000000, +1.00000000],
    ]
)


# TODO: use one-turn matrix of fodo_cell
def test_one_turn_matrix(fodo_ring):
    # ony true if one turn matrix is calculated from pos = 0
    twiss = ap.Twiss(fodo_ring, start_idx=0)
    assert np.allclose(ONE_TURN_MATRIX, twiss.one_turn_matrix)


def test_tune_fractional(twiss):
    # TODO: combine with 'test_one_turn_matrix'
    assert 0.2371 == round(twiss.tune_x_fractional, 4)
    assert 0.3175 == round(twiss.tune_y_fractional, 4)


def test_periodic_solution(twiss):
    assert twiss.stable
    assert twiss.stable_x
    assert twiss.stable_y

    q1 = twiss.lattice["Q1"]
    tmp_k1 = q1.k1
    q1.k1 = 0
    assert not twiss.stable
    assert not twiss.stable_x
    assert twiss.stable_y
    q1.k1 = tmp_k1

    q2 = twiss.lattice["Q2"]
    tmp_k1 = q2.k1
    q2.k1 = 0
    assert not twiss.stable
    assert twiss.stable_x
    assert not twiss.stable_y
    q2.k1 = tmp_k1


# TODO: test for all Twiss properties
def test_element_change(twiss):
    fodo_cell = twiss.lattice
    q1 = fodo_cell["Q1"]
    beta_x_initial = twiss.beta_x[0]
    tune_x_initial = twiss.tune_x
    q1.k1 += 0.25
    assert beta_x_initial != twiss.beta_x[0]
    assert tune_x_initial != twiss.tune_x
    q1.k1 -= 0.25  # set back to avoid failure of other tests
