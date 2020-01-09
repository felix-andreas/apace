import numpy as np
from math import inf
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid_spec
from collections.abc import Iterable
from .classes import Drift, Dipole, Quadrupole, Sextupole, Lattice

FONT_SIZE = 10
C_MAP = plt.cm.get_cmap("Set1")
COLORS = {Drift: None, Dipole: "#ffc425", Quadrupole: "#d11141", Sextupole: "#00b159"}


# TODO: docstring
def draw_elements(
    lattice,
    ax=None,
    annotate_elements=False,
    annotate_lattices=False,
    x_min=-inf,
    x_max=inf,
):
    if ax is None:
        ax = plt.gca()

    y_min, y_max = ax.get_ylim()
    y_span = y_max - y_min
    rec_height = y_span / 16

    start = end = 0
    arrangement = lattice.arrangement
    for element, next_element in zip(arrangement, arrangement[1:] + [None]):
        end += element.length
        if element is next_element:
            continue

        if end > x_min and start < x_max and not isinstance(element, Drift):
            rec_length = min(end, x_max) - max(start, x_min)
            rectangle = plt.Rectangle(
                (start if start > x_min else x_min, y_max - rec_height / 2),
                rec_length,
                rec_height,
                fc=COLORS[type(element)],
                clip_on=False,
                zorder=10,
            )
            ax.add_patch(rectangle)

        if start > x_min and end < x_max and not isinstance(element, Drift):
            if annotate_elements:
                sign, va = (
                    (1, "bottom") if isinstance(element, Quadrupole) else (-1, "top")
                )
                ax.annotate(
                    element.name,
                    xy=((start + end) / 2, y_max + sign * 0.6 * rec_height),
                    fontsize=FONT_SIZE,
                    va=va,
                    ha="center",
                    annotation_clip=False,
                    zorder=11,
                )

        start = end


# TODO: docstring
def draw_sub_lattices(lattice, ax=None, min_size=0.05):
    if ax is None:
        ax = plt.gca()

    y_min, y_max = ax.get_ylim()
    y_span = y_max - y_min
    y0 = y_max - y_span / 8
    pos = 0
    for obj in lattice.tree:
        pos += obj.length
        if isinstance(obj, Lattice) and obj.length > min_size * lattice.length:
            x0 = pos - obj.length / 2
            ax.annotate(
                obj.name,
                xy=(x0, y0),
                fontsize=FONT_SIZE,
                va="top",
                ha="center",
                clip_on=True,
                zorder=102,
            )
    # TODO: draw grid


def plot_twiss(
    twiss, ax=None, line_style="solid", line_width=1.3, alpha=1.0, eta_x_scale=10
):
    if ax is None:
        fig, ax = plt.subplots()

    ax.plot(
        twiss.s,
        twiss.eta_x * eta_x_scale,
        color=C_MAP(2 / 9),
        linewidth=line_width,
        linestyle=line_style,
        alpha=alpha,
        label="$\\beta_x$/m",
    )
    ax.plot(
        twiss.s,
        twiss.beta_y,
        color=C_MAP(1 / 9),
        linewidth=line_width,
        linestyle=line_style,
        alpha=alpha,
        label="$\\beta_y$/m",
    )
    ax.plot(
        twiss.s,
        twiss.beta_x,
        color=C_MAP(0 / 9),
        linewidth=line_width,
        linestyle=line_style,
        alpha=alpha,
        label="$\\eta_x$/10cm",
    )

    return fig, ax


def set_limits(ax, lattice, x_min=None, x_max=None, y_min=None, y_max=None):
    x_min = x_min if x_min else 0
    x_max = x_max if x_max else lattice.length
    y_lim = ax.get_ylim()
    y_min = y_min if y_min else -0.5
    y_max = y_max if y_max else 1.1 * y_lim[1]
    ax.set_xlim((x_min, x_max))
    ax.set_ylim((y_min, y_max))
    return x_min, x_max, y_min, y_max


def set_grid(ax, lattice, x_min, x_max, y_min, y_max, n_x_ticks, n_y_ticks):
    ax.xaxis.grid(which="minor", linestyle="dotted")
    ax.yaxis.grid(alpha=0.5, zorder=0, linestyle="dotted")
    if n_x_ticks:
        lin = np.linspace(x_min, x_max, n_x_ticks)
        lattice_length_list = [0]
        lattice_length_list.extend([lattice.length for lattice in lattice.tree])
        pos_tick = (
            np.add.accumulate(lattice_length_list) if not (x_min and x_max) else lin
        )
        ax.set_xticks(pos_tick, minor=True)
        ax.set_xticks(lin)
    if n_y_ticks:
        ax.set_yticks(np.arange(int(y_min), int(y_max), n_y_ticks))
    ax.set_xlabel("orbit position $s$/m")


def annotate_info(lattice, twiss, eta_x_scale=10):
    # fig = plt.gcf()
    ax = plt.gca()
    margin = 0.02
    fs = 15

    ax.annotate(
        lattice.name,
        xy=(1 - margin, 1 - margin),
        xycoords="figure fraction",
        va="top",
        ha="right",
        fontsize=fs,
    )

    # annolist_string1 = f"$Q_x$: {twiss.Qx:.2f} ({twiss.Qx_freq:.0f} kHz)   $Q_y$: {twiss.Qy:.2f} " \
    #                    f"({twiss.Qy_freq:.0f} kHz)   $\\alpha_C$: {twiss.alphac:.2e}"
    # fig.annotate(annolist_string1, xy=(start, height_1),
    #              xycoords='figure fraction', va='center', ha='left', fontsize=fs)
    # r = fig.canvas.get_renderer()

    string = ["$\\beta_x$/m", "$\\beta_y$/m", f"$\\eta_x$/{100 / eta_x_scale:.0f}cm"]
    w = margin

    for i, s in enumerate(string):
        plt.annotate(
            s,
            xy=(w, 1 - margin),
            xycoords="figure fraction",
            color=C_MAP(i / 9),
            fontsize=fs,
            va="top",
            ha="left",
        )
        w += len(s) * 0.005

    # space = 0
    # x_min, x_max = ax.get_xlim()
    # for i, s in enumerate(string):
    #     t = ax.annotate(s, xy=(w, 1 - margin), xycoords='figure fraction',
    #                            color=mpl.cm.Set1(i / 9), fontsize=fs, va="top", ha="left")
    #     transform = ax.transData.inverted()
    #     bb = t.get_window_extent(renderer=r)
    #     bb = bb.transformed(transform)
    #     w = w + (bb.x_max - bb.x_min) / (x_max - x_min) + space


def _twiss_plot_section(
    twiss,
    ax=None,
    lattice=None,
    x_min=None,
    x_max=None,
    y_min=None,
    y_max=None,
    n_x_ticks=17,
    n_y_ticks=4,
    annotate_elements=True,
    annotate_lattices=True,
    line_style="solid",
    line_width=1.3,
    ref_twiss=None,
    ref_line_style="dashed",
    ref_line_width=2.5,
    eta_x_scale=10,
    overwrite=False,
):
    if overwrite:
        ax.clear()

    if ref_twiss:
        plot_twiss(
            ref_twiss, ax, ref_line_style, ref_line_width, alpha=0.5,
        )

    plot_twiss(twiss, ax, line_style, line_width, eta_x_scale)
    if lattice:
        x_min, x_max, y_min, y_max = set_limits(ax, lattice, x_min, x_max, y_min, y_max)
        set_grid(ax, lattice, x_min, x_max, y_min, y_max, n_x_ticks, n_y_ticks)
        draw_elements(
            lattice, ax, annotate_elements, annotate_lattices, x_min, x_max,
        )


def twiss_plot(
    twiss,
    lattice=None,
    main=True,
    fig_size=(16, 9),
    sections=None,
    y_min=None,
    y_max=None,
    eta_x_scale=10,
    ref_twiss=None,
    path=None,
):
    fig = plt.figure(figsize=fig_size)  # , constrained_layout=True)
    height_ratios = [2, 7] if (main and sections) else [1]
    main_grid = grid_spec.GridSpec(
        len(height_ratios), 1, figure=fig, height_ratios=height_ratios
    )

    if main:
        ax = fig.add_subplot(main_grid[0])
        _twiss_plot_section(
            ax,
            twiss,
            lattice,
            ref_twiss=ref_twiss,
            y_min=y_min,
            y_max=y_max,
            annotate_elements=True,
            eta_x_scale=eta_x_scale,
        )

    if sections:
        if isinstance(sections, str) or not isinstance(sections[0], Iterable):
            sections = [sections]

        N_sections = len(sections)
        rows, cols = find_optimal_grid(N_sections)
        sub_grid = grid_spec.GridSpecFromSubplotSpec(
            rows, cols, subplot_spec=main_grid[-1]
        )
        for i, section in enumerate(sections):
            ax = fig.add_subplot(sub_grid[i])

            if isinstance(section, str):
                pass  # TODO: implement cell_start + cell_end
            else:
                x_min, x_max = section[0], section[1]

            _twiss_plot_section(
                ax,
                twiss,
                lattice,
                ref_twiss=ref_twiss,
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                annotate_elements=True,
                n_x_ticks=None,
            )

    fig.tight_layout()
    fig.subplots_adjust(top=0.93)
    annotate_info(lattice, twiss, eta_x_scale=eta_x_scale)
    if path:
        fig.savefig(path)

    return fig


def find_optimal_grid(N):
    rows, cols = 1, 1
    while rows * cols < N:
        cols += 1
        rows, cols = cols, rows

    return (rows, cols) if cols >= rows else (cols, rows)
