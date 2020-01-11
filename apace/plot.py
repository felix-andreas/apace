import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as grid_spec
from matplotlib.path import Path
import numpy as np
from enum import Enum
from math import inf
from collections.abc import Iterable
from .classes import Drift, Dipole, Quadrupole, Sextupole, Octupole, Lattice


class Color:
    RED = "crimson"
    GREEN = "mediumseagreen"
    BLUE = "dodgerblue"
    YELLOW = "gold"
    ORANGE = "darkorange"
    MAGENTA = "darkmagenta"
    WHITE = "white"
    BLACK = "black"


ELEMENT_COLOR = {
    Drift: Color.BLACK,
    Dipole: Color.YELLOW,
    Quadrupole: Color.RED,
    Sextupole: Color.GREEN,
    Octupole: Color.BLUE,
}

FONT_SIZE = 8


def draw_lattice(
    lattice,
    ax=None,
    draw_elements=True,
    annotate_elements=True,
    draw_sub_lattices=True,
    annotate_sub_lattices=True,
    x_min=-inf,
    x_max=inf,
):
    """Draw elements of a lattice to a matplotlib axes

    :param lattice: lattice which gets drawn
    :type lattice: ap.Lattice
    :param ax: matplotlib axes, if not provided use current axes
    :type ax: matplotlib.axes, optional
    :param annotate_elements: whether to display the names of elments, defaults to False
    :type annotate_elements: bool, optional
    :param draw_sub_lattices: Whether to show the start and end position of the sub lattices,
                        defaults to True
    :type draw_sublattices: bool, optional
    :param x_min: minimum position from which elements get drawn, defaults to -inf
    :type x_min: float, optional
    :param x_max: maximum position to which elements get drawn, defaults to inf
    :type x_max: float, optional
    """
    if ax is None:
        ax = plt.gca()

    y_min, y_max = ax.get_ylim()
    y_span = y_max - y_min
    rec_height = y_span / 32

    if draw_elements:
        start = end = 0
        arrangement = lattice.arrangement
        for element, next_element in zip(arrangement, arrangement[1:] + [None]):
            end += element.length
            if element is next_element:
                continue

            if isinstance(element, Drift) or start > x_max or end < x_min:
                start = end
                continue

            rec_length = min(end, x_max) - max(start, x_min)
            rectangle = plt.Rectangle(
                (start if start > x_min else x_min, y_max - rec_height / 2),
                rec_length,
                rec_height,
                fc=ELEMENT_COLOR[type(element)],
                clip_on=False,
                zorder=10,
            )
            ax.add_patch(rectangle)

            if annotate_elements:
                sign, va = (
                    (1, "bottom") if isinstance(element, Quadrupole) else (-1, "top")
                )
                ax.annotate(
                    element.name,
                    xy=((start + end) / 2, y_max + sign * 0.75 * rec_height),
                    fontsize=FONT_SIZE,
                    ha="center",
                    va=va,
                    annotation_clip=False,
                    zorder=11,
                )

            start = end

    if draw_sub_lattices:
        length_list = [0]
        length_list.extend(obj.length for obj in lattice.tree)
        position_list = np.add.accumulate(length_list)
        ax.set_xticks(position_list)
        ax.grid(axis="x", linestyle="--")

    if annotate_sub_lattices:
        y0 = y_max - 3 * rec_height
        end = 0
        for obj in lattice.tree:
            end += obj.length
            if not isinstance(obj, Lattice):
                continue

            x0 = end - obj.length / 2
            ax.annotate(
                obj.name,
                xy=(x0, y0),
                fontsize=FONT_SIZE,
                fontstyle="oblique",
                alpha=0.5,
                va="center",
                ha="center",
                clip_on=True,
                zorder=102,
            )


def plot_twiss(
    twiss,
    ax=None,
    line_style="solid",
    line_width=1.3,
    alpha=1.0,
    eta_x_scale=10,
    show_legend=True,
):
    if ax is None:
        _, ax = plt.subplots()

    ax.plot(
        twiss.s,
        twiss.beta_x,
        color=Color.RED,
        linewidth=line_width,
        linestyle=line_style,
        alpha=alpha,
        zorder=3,
        label="$\\beta_x$/m",
    )
    ax.plot(
        twiss.s,
        twiss.beta_y,
        color=Color.BLUE,
        linewidth=line_width,
        linestyle=line_style,
        alpha=alpha,
        zorder=2,
        label="$\\beta_y$/m",
    )
    ax.plot(
        twiss.s,
        twiss.eta_x * eta_x_scale,
        color=Color.GREEN,
        linewidth=line_width,
        linestyle=line_style,
        alpha=alpha,
        zorder=1,
        label=f"$\\eta_x$/{100 / eta_x_scale:.0f}cm",
    )

    if show_legend:
        ax.legend(
            loc="lower left",
            bbox_to_anchor=(0.0, 1.05),
            ncol=10,
            borderaxespad=0,
            frameon=False,
        )

    ax.set_xlabel("Orbit Position $s$ / m")

    return ax


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


def annotate_info(lattice, twiss, ax=None):
    # fig = plt.gcf()
    if ax is None:
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

    x = margin
    y = 1 - margin
    for line in ax.get_lines():
        label = line.get_label()
        plt.annotate(
            label,
            xy=(x, y),
            xycoords="figure fraction",
            color=line.get_color(),
            fontsize=fs,
            va="top",
            ha="left",
        )
        x += len(label) * 0.005

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
        draw_lattice(lattice, ax, annotate_elements, x_min, x_max)


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
            twiss,
            ax,
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

    fig.suptitle(lattice.name)
    fig.tight_layout()
    fig.subplots_adjust(top=0.93)
    # annotate_info(lattice, twiss)
    if path:
        fig.savefig(path)

    return fig


def find_optimal_grid(N):
    rows, cols = 1, 1
    while rows * cols < N:
        cols += 1
        rows, cols = cols, rows

    return (rows, cols) if cols >= rows else (cols, rows)


def floor_plan(lattice, ax=None, start_angle=0):
    if ax is None:
        ax = plt.gca()

    ax.set_aspect("equal")
    current_angle=start_angle

    end = np.zeros(2)
    codes = [Path.MOVETO, Path.LINETO]
    i = 0
    for element in lattice.arrangement:
        i += 1
        color = ELEMENT_COLOR[type(element)]
        start = end.copy()
        length = element.length
        line_width = 0.5 if isinstance(element, Drift) else 3
        try:
            angle = element.angle
        except AttributeError:
            angle = 0

        if angle == 0:
            end[0] += length * np.cos(current_angle)
            end[1] += length * np.sin(current_angle)
            line = patches.PathPatch(
                Path((start, end), codes), color=color, linewidth=line_width
            )
        else:
            tmp_angle = current_angle + np.pi / 2
            radius = length / angle
            tmp = radius * np.array([np.cos(tmp_angle), np.sin(tmp_angle)])
            # if angle < 0:
            #     tmp = - tmp
            center = start + tmp

            vec = radius * np.array([np.sin(angle), 1 - np.cos(angle)])
            sin = np.sin(current_angle)
            cos = np.cos(current_angle)
            rot = np.array([[cos, -sin], [sin, cos]])
            end += rot @ vec
            diameter = 2 * radius
            if angle > 0:
                line = patches.Arc(
                    center,
                    width=diameter,
                    height=diameter,
                    angle=-90,
                    theta1=current_angle * 180 / np.pi,
                    theta2=(current_angle + angle) * 180 / np.pi,
                    color=color,
                    linewidth=line_width,
                )
            else:
                line = patches.Arc(
                    center,
                    width=diameter,
                    height=diameter,
                    angle=-90+(angle * 180 / np.pi),
                    theta1=current_angle * 180 / np.pi,
                    theta2=(current_angle - angle) * 180 / np.pi,
                    color=color,
                    linewidth=line_width,
                )
            current_angle += angle

            for point in start, end:
                ax.add_patch(
                    patches.PathPatch(
                        Path((point, center), codes), color="gray", linestyle="--", linewidth=0.5
                    )
                )

        ax.add_patch(line)

    lim = lattice.length / 5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-2, 2 * lim)
