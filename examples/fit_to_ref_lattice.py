import elements as el
from elements.optimize import fit_twiss_to_ref_twiss
from elements.plotting import plot_full

main_cell = el.read_lattice_file_json("lattices/FODO-lattice_strong.json")
lin = el.LinBeamDyn(main_cell)
ref_main_cell = el.read_lattice_file_json("lattices/FODO-lattice.json")
ref_twiss = el.LinBeamDyn(ref_main_cell).get_twiss(interpolate=1000)

Q1 = main_cell.elements["Q1"]
Q2 = main_cell.elements["Q2"]

result = fit_twiss_to_ref_twiss([Q1, Q2], ["k1", "k1"], lin, ref_twiss)
print(result)

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
plot_full(ax, lin, ref_twiss=ref_twiss, path="out.pdf")
