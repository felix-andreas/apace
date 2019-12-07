.. _quickstart:

==========
Quickstart
==========

A simple example on how to calculate the Twiss parameter for a FODO lattice.

Import apace::

    import apace as ap

Create a ring consisting of 8 FODO cells::

    d1 = ap.Drift('D1', length=0.55)
    b1 = ap.Dipole('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
    q1 = ap.Quadrupole('Q1', length=0.2, k1=1.2)
    q2 = ap.Quadrupole('Q2', length=0.4, k1=-1.2)
    fodo_cell = ap.Lattice('FODO', [q1, d1, b1, d1, q2, d1, b1, d1, q1])
    fodo_ring = ap.Lattice('RING', [fodo_cell] * 8)

Calculate the twiss parameters::

    twiss = ap.Twiss(ring)

Plot horizontal and vertical beta functions using matplotlib::

    import matplotlib.pyplot as plt
    plt.plot(twiss.s, twiss.beta_x, twiss.beta_y, twiss.eta_x)
    plt.show()

.. note::
    A FODO lattice is the simplest possible strong focusing lattice consisting out of a horizontal focusing quadrupole **(F)**, a drift space **(0)**, a horizontal defocusing quadrupole **(D)** and another drift space **(0)**.
