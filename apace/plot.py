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
    x_min=-inf,
    x_max=inf,
    draw_elements=True,
    annotate_elements=True,
    draw_sub_lattices=True,
    annotate_sub_lattices=True,
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
    rect_height = y_span / 32

    if draw_elements:
        start = end = 0
        arrangement = lattice.arrangement
        for element, next_element in zip(arrangement, arrangement[1:] + [None]):
            end += element.length
            if element is next_element:
                continue

            if isinstance(element, Drift) or start >= x_max or end <= x_min:
                start = end
                continue

            rec_length = min(end, x_max) - max(start, x_min)
            rectangle = plt.Rectangle(
                (start if start > x_min else x_min, y_max - rect_height / 2),
                rec_length,
                rect_height,
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
                    xy=((start + end) / 2, y_max + sign * 0.75 * rect_height),
                    fontsize=FONT_SIZE,
                    ha="center",
                    va=va,
                    annotation_clip=False,
                    zorder=11,
                )

            start = end

    if draw_sub_lattices:
        length_gen = [0] + [obj.length for obj in lattice.tree]
        position_list = np.add.accumulate(length_gen)
        i_min = np.searchsorted(position_list, x_min)
        i_max = np.searchsorted(position_list, x_max)
        ax.set_xticks(position_list[i_min:i_max])
        ax.grid(linestyle="--")

    if annotate_sub_lattices:
        y0 = y_max - 3 * rect_height
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
    twiss, ax=None, line_style="solid", line_width=1.3, alpha=1.0, eta_x_scale=10,
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
        label=f"{eta_x_scale}$\\eta_x$/m",
    )

    ax.set_xlabel("Orbit Position $s$ / m")
    return ax


def _twiss_plot_section(
    twiss,
    ax=None,
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
        plot_twiss(ref_twiss, ax, ref_line_style, ref_line_width, alpha=0.5)

    plot_twiss(twiss, ax, line_style, line_width, eta_x_scale)
    if x_min is None:
        x_min = 0
    if x_max is None:
        x_max = twiss.lattice.length
    if y_min is None:
        y_min = -0.5
    if y_max is None:
        y_max = ax.get_ylim()[1]

    ax.set_xlim((x_min, x_max))
    ax.set_ylim((y_min, y_max))
    draw_lattice(twiss.lattice, ax, x_min, x_max, annotate_elements=annotate_elements)


# TODO: make sub_class of figure
# add attribute which defines which twiss parameters are plotted
def twiss_plot(
    twiss,
    main=True,
    fig_size=(16, 9),
    sections=None,
    y_min=None,
    y_max=None,
    eta_x_scale=10,
    ref_twiss=None,
    path=None,
):
    fig = plt.figure(figsize=fig_size)
    height_ratios = [2, 7] if (main and sections) else [1]
    main_grid = grid_spec.GridSpec(
        len(height_ratios), 1, fig, height_ratios=height_ratios
    )

    if main:
        ax = fig.add_subplot(main_grid[0])
        _twiss_plot_section(
            twiss,
            ax,
            ref_twiss=ref_twiss,
            y_min=y_min,
            y_max=y_max,
            annotate_elements=False,
            eta_x_scale=eta_x_scale,
        )

        ax.legend(
            loc="lower left",
            bbox_to_anchor=(0.0, 1.05),
            ncol=10,
            borderaxespad=0,
            frameon=False,
        )

    if sections:
        if isinstance(sections, str) or not isinstance(sections[0], Iterable):
            sections = [sections]

        n_sections = len(sections)
        rows, cols = find_optimal_grid(n_sections)
        sub_grid = grid_spec.GridSpecFromSubplotSpec(rows, cols, main_grid[-1])
        for i, section in enumerate(sections):
            ax = fig.add_subplot(sub_grid[i])

            if isinstance(section, str):
                raise NotImplementedError  # TODO: implement cell_start + cell_end
            else:
                x_min, x_max = section

            _twiss_plot_section(
                twiss,
                ax,
                ref_twiss=ref_twiss,
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                annotate_elements=True,
                n_x_ticks=None,
            )

    fig.suptitle(twiss.lattice.name, ha="right", x=0.9925)
    fig.tight_layout()
    # fig.subplots_adjust(top=0.93)
    if path:
        fig.savefig(path)

    return fig


def find_optimal_grid(N):
    rows, cols = 1, 1
    while rows * cols < N:
        cols += 1
        rows, cols = cols, rows

    return (rows, cols) if cols >= rows else (cols, rows)


def floor_plan(
    lattice, ax=None, start_angle=0, annotate_elements=True, direction="clockwise"
):
    if ax is None:
        ax = plt.gca()

    ax.set_aspect("equal")
    codes = [Path.MOVETO, Path.LINETO]
    current_angle = start_angle

    start = np.zeros(2)
    end = np.zeros(2)
    x_min = y_min = 0
    x_max = y_max = 0
    arrangement = lattice.arrangement
    arrangement_shifted = arrangement[1:] + arrangement[0:1]
    for element, next_element in zip(arrangement, arrangement_shifted):
        color = ELEMENT_COLOR[type(element)]
        length = element.length
        line_width = 0.5 if isinstance(element, Drift) else 3

        # TODO: refactor current angle
        angle = 0
        if isinstance(element, Dipole):
            angle = element.angle
            radius = length / angle
            vec = radius * np.array([np.sin(angle), 1 - np.cos(angle)])
            sin = np.sin(current_angle)
            cos = np.cos(current_angle)
            rot = np.array([[cos, -sin], [sin, cos]])
            end += rot @ vec

            angle_center = current_angle + np.pi / 2
            center = start + radius * np.array(
                [np.cos(angle_center), np.sin(angle_center)]
            )
            diameter = 2 * radius
            arc_angle = -90
            theta1 = current_angle * 180 / np.pi
            theta2 = (current_angle + angle) * 180 / np.pi
            if angle < 0:
                theta1, theta2 = theta2, theta1

            line = patches.Arc(
                center,
                width=diameter,
                height=diameter,
                angle=arc_angle,
                theta1=theta1,
                theta2=theta2,
                color=color,
                linewidth=line_width,
            )
            current_angle += angle
        else:
            end += length * np.array([np.cos(current_angle), np.sin(current_angle)])
            line = patches.PathPatch(
                Path((start, end), codes), color=color, linewidth=line_width
            )

        x_min = min(x_min, end[0])
        y_min = min(y_min, end[1])
        x_max = max(x_max, end[0])
        y_max = max(y_max, end[1])

        ax.add_patch(line)  # TODO: currently splitted elements get drawn twice
        if element is next_element:
            continue

        if annotate_elements and not isinstance(element, Drift):
            angle_center = (current_angle - angle / 2) + np.pi / 2
            sign = -1 if isinstance(element, Quadrupole) else 1
            center = (start + end) / 2 + sign * 0.5 * np.array(
                [np.cos(angle_center), np.sin(angle_center)]
            )
            ax.annotate(
                element.name,
                xy=center,
                fontsize=6,
                ha="center",
                va="center",
                # rotation=(current_angle * 180 / np.pi -90) % 180,
                annotation_clip=False,
                zorder=11,
            )

        start = end.copy()

    margin = 0.05 * max((x_max - x_min), (y_max - y_min))
    ax.set_xlim(x_min - margin, x_max + margin)
    ax.set_ylim(y_min - margin, y_max + margin)
    ax.axis("off")

    return ax
