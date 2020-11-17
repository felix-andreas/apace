"""
Tune Bump
=========

This example shows how to shift the tune using quadrupoles.
"""

#%%
# Imports
import numpy as np
from scipy.optimize import minimize
import apace as ap
import random

#%%
# OPTIONS
url = "https://raw.githubusercontent.com/NoBeam/lattices/master/b2_stduser_2019_05_07.json"
tune_x_target = 17.66
method = "Nelder-Mead"
max_value = 3

#%%
# SETUP
lattice = ap.Lattice.from_file(url)
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
s = np.linspace(0, lattice.length, 1000)
reference = [
    np.interp(s, twiss.s, value) for value in (twiss.beta_x, twiss.beta_y, twiss.eta_x)
]

#%%
# FITNESS FUNCTION
def fitness_function(params):
    for param, element in zip(params, fit_elements):
        element.k1 = max(min(param, max_value), -max_value)

    if not twiss.stable:
        return float("nan")

    values = twiss.beta_x, twiss.beta_x, twiss.eta_x
    means = []
    for value, value_ref in zip(values, reference):
        beat = (np.interp(s, twiss.s, value) / value_ref) ** 4
        np.clip(beat, 1, None, out=beat)
        means.append(np.mean(beat))
    return np.mean(means) + abs(twiss.tune_x - tune_x_target)


#%%
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
