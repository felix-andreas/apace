"""
Twiss parameter of a FODO lattice
=================================

This example shows how to calulate and plot the Twiss parameter of a FOOD lattice.
"""

import numpy as np
from scipy.optimize import minimize
import apace as ap
import random

# OPTIONS
url = "https://raw.githubusercontent.com/NoBeam/lattices/master/b2_stduser_2019_05_07.json"
url = "/home/felix/Git/nobeam/lattices/b2_stduser_2019_05_07.json"
tune_x_target = 17.33
method = "Nelder-Mead"
max_value = 3

# SETUP
lattice = ap.Lattice.from_file(url)
b = lattice["B"]
b.e1 *= 0.25
b.e2 *= 0.25
twiss = ap.Twiss(lattice)
fit_elements = [
    element
    for element in lattice.elements
    if isinstance(element, ap.Quadrupole)
    and element.name[1].isdigit()
    and int(element.name[1]) >= 3
]
fit_elements = random.sample(fit_elements, 10)
print(fit_elements)
positions = np.linspace(0, lattice.length, 1000)
beta_x_ref = np.interp(positions, twiss.s, twiss.beta_x)
beta_y_ref = np.interp(positions, twiss.s, twiss.beta_y)

# FITNESS FUNCTION
def fitness_function(params):
    for param, element in zip(params, fit_elements):
        element.k1 = max(min(param, max_value), -max_value)

    if not twiss.stable:
        return float("inf")

    beta_x = np.interp(positions, twiss.s, twiss.beta_x)
    beta_y = np.interp(positions, twiss.s, twiss.beta_y)
    beta_x_beat = beta_x / beta_x_ref
    beta_y_beat = beta_y / beta_y_ref
    beta_x_beat[beta_x_beat < 1] = 1
    beta_y_beat[beta_y_beat < 1] = 1
    beta_x_beat **= 4
    beta_y_beat **= 4
    return np.mean([beta_x_beat, beta_y_beat]) + 1 * abs(twiss.tune_x - tune_x_target)


# MINIMIZE
print(f"Tune before {twiss.tune_x}")
n_iterations = 2
for i in range(n_iterations):
    start_values = np.array([element.k1 for element in fit_elements])
    if i == 0:
        initial_values = start_values

    res = minimize(fitness_function, initial_values, method=method)
    print(f"iteration: {i + 1}/{n_iterations}, result: {res.fun:.3f}")

print(f"Tune after {twiss.tune_x}")

# OUTPUT RESULTS
#%%
for element, initial_value in zip(fit_elements, initial_values):
    print(f"{element.name+'.k1':>9} = {element.k1:+.3f} ({initial_value:+.3f})")
print("\n")

from apace.plot import twiss_plot

ref_lattice = ap.Lattice.from_file(url)
ref_twiss = ap.Twiss(ref_lattice)
fig = twiss_plot(twiss, ref_twiss=ref_twiss)
fig.savefig("tune_bump.pdf")
