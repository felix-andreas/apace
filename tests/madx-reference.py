"""Generate tests for optical functions using reference values from madx/cpymad"""

from pathlib import Path
from cpymad.madx import Madx
import latticejson
from latticejson.convert import to_madx
import numpy as np

madx = Madx()
madx.options.info = False
madx.command.beam(particle="electron", energy=1.0, charge=-1)
lattice_path = Path(__file__).parent.parent / "data/lattices/fodo_cell.json"
lattice = to_madx(latticejson.load(lattice_path))
madx.input(lattice)
twiss = madx.twiss(chrom=True)


print("\ntest_optical_functions")  # for 0:3 and -4:-1 because s[-1] == s[-2]
for name, madx_name in (
    ("beta_{}", "bet"),
    ("alpha_{}", "alf"),
    ("eta_{}", "d"),
    ("eta_{}_dds", "dp"),
    # ("psi", "mu"),
):
    for u in "x", "y":
        if u == "y" and name.startswith("eta"):
            continue
        value = getattr(twiss, madx_name + u)
        for mask, mask2 in (slice(3), "[:3]"), (slice(-4, -1), "[-3:]"):
            tmp = f"({', '.join(np.char.mod('%.3f', value[mask]))})"
            print(f"    assert allclose_atol({tmp}, twiss.{name.format(u)}{mask2})")

print("\ntest_synchrotron_radiation_integrals")
for name, madx_name in [
    ("tune_x", "q1"),
    ("tune_y", "q2"),
    ("chromaticity_x", "dq1"),
    ("chromaticity_y", "dq2"),
    ("alpha_c", "alfa"),
] + [(f"i{i}", f"synch_{i}") for i in range(1, 6)]:
    value = getattr(twiss.summary, madx_name)
    print(f"    assert math.isclose({value:.3f}, twiss.{name}, abs_tol=1e-3)")
