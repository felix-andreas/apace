#%%
import matplotlib.pyplot as plt
import apace as ap
from apace.tracking_integration import Tracking
from apace.plot import draw_lattice, twiss_plot

lattice = ap.Lattice.from_file(
    "/home/felix/Git/nobeam/lattices/b2_stduser_2019_05_07.json"
)
twiss = ap.Twiss(lattice)
print(twiss.tune_x)

quads = {"3": [], "4": [], "5": []}
for element in lattice.elements:
    if isinstance(element, ap.Quadrupole):
        name1 = element.name[1]
        if name1.isdigit() and int(name1) >= 3:
            quads[element.name[1]].append(element)

step = 0.001
while (abs((twiss.tune_x % 1) - 1 / 3)) > 0.25:
    # for q3 in quads["3"]:
    #     q3.k1 += step
    for q4 in quads["4"]:
        q4.k1 += -step
    # for q5 in quads["5"]:
    #     q5.k1 += -step

    print(twiss.tune_x)

fig = twiss_plot(twiss)
fig.savefig("test_twiss.pdf")
exit()

#%%


x_width = 0.001
n_turns = 10
dist = ap.distribution(10, x_dist="uniform", x_center=0.0005, x_width=0.001)
tracking = Tracking(lattice)
s, trajectroy = tracking.track(dist, n_turns=n_turns, max_step=0.01, watchers=[0])
s_all, t_all = tracking.track(dist, n_turns=n_turns, max_step=0.01)
tracking_mat = ap.MatrixTracking(lattice, dist, watch_points=[0], turns=n_turns)
x_mat, x_dds_mat = tracking_mat.x, tracking_mat.x_dds

#%%

fig, (ax1, ax2) = plt.subplots(nrows=2)
ax1 = plt.subplot(211)

ax1.plot(s_all, t_all[:, 0])
draw_lattice(
    lattice,
    draw_sub_lattices=False,
    annotate_elements=False,
    annotate_sub_lattices=False,
)

ax2 = plt.subplot(223)
ax2.plot(trajectroy[:, 0], trajectroy[:, 1], "o")
ax2.set_xlim(-2 * x_width, 2 * x_width)

ax3 = plt.subplot(224)
ax3.plot(x_mat, x_dds_mat, "o")

plt.savefig("test.pdf")


# %%
