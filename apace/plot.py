import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as grid_spec
from matplotlib.widgets import Slider, Button
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, VPacker
from matplotlib.path import Path
from matplotlib.ticker import AutoMinorLocator, ScalarFormatter
import numpy as np
from math import inf
from collections.abc import Iterable
from .classes import Base, Drift, Dipole, Quadrupole, Sextupole, Octupole, Lattice


FONT_SIZE = 8


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


OPTICAL_FUNCTIONS = {
    "beta_x": (r"$\beta_x$/m", Color.RED),
    "beta_y": (r"$\beta_y$/m", Color.BLUE),
    "eta_x": (r"$\eta_x$/m", Color.GREEN),
    "psi_x": (r"$\psi_x$", Color.YELLOW),
    "psi_y": (r"$\psi_y$", Color.ORANGE),
    "alpha_x": (r"$\alpha_x$", Color.MAGENTA),
    "alpha_y": (r"$\alpha_y$", Color.BLACK),
}


def draw_lattice(
    lattice,
    ax=None,
    x_min=-inf,
    x_max=inf,
    location="top",
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

    y0 = -rect_height / 2
    if location == "top":
        y0 += y_max
    elif location == "bottom":
        y0 += y_min

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
                (start if start > x_min else x_min, y0),
                rec_length,
                rect_height,
                fc=ELEMENT_COLOR[type(element)],
                clip_on=False,
                zorder=10,
            )
            ax.add_patch(rectangle)

            center = (start + end) / 2
            if annotate_elements and x_min < center < x_max:
                sign, va = (
                    (1, "bottom") if isinstance(element, Quadrupole) else (-1, "top")
                )
                ax.annotate(
                    element.name,
                    xy=(center, y0 + sign * 0.75 * rect_height),
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
        ticks = position_list[i_min : i_max + 1]
        ax.set_xticks(ticks)
        if len(ticks) < 5:
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.xaxis.set_minor_formatter(ScalarFormatter())
        ax.grid(linestyle="--")

    if annotate_sub_lattices:
        y0_anno = y0 - 3 * rect_height
        end = 0
        for obj in lattice.tree:
            end += obj.length
            if not isinstance(obj, Lattice):
                continue

            x0 = end - obj.length / 2
            ax.annotate(
                obj.name,
                xy=(x0, y0_anno),
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
    twiss_functions=("beta_x", "beta_y", "eta_x"),
    *,
    scales={"eta_x": 10},
    ax=None,
    line_style="solid",
    line_width=1.3,
    alpha=1.0,
    show_ylabels=False,
):
    if ax is None:
        ax = plt.gca()
    if scales is None:
        scales = {}

    text_areas = []
    for i, function in enumerate(twiss_functions):
        value = getattr(twiss, function)
        scale = scales.get(function, "")
        label, color = OPTICAL_FUNCTIONS[function]
        label = str(scale) + label
        ax.plot(
            twiss.s,
            value if scale == "" else scale * value,
            color=color,
            linewidth=line_width,
            linestyle=line_style,
            alpha=alpha,
            zorder=10 - i,
            label=label,
        )
        text_areas.append(TextArea(label, textprops=dict(color=color, rotation=90)))

    ax.set_xlabel("Orbit Position $s$ / m")
    if show_ylabels:
        ax.add_artist(
            AnchoredOffsetbox(
                loc=8,
                child=VPacker(children=text_areas, align="bottom", pad=0, sep=10),
                pad=0.0,
                frameon=False,
                bbox_to_anchor=(-0.08, 0.3),
                bbox_transform=ax.transAxes,
                borderpad=0.0,
            )
        )
    return ax


def _twiss_plot_section(
    twiss,
    ax=None,
    x_min=None,
    x_max=None,
    y_min=None,
    y_max=None,
    annotate_elements=True,
    annotate_lattices=True,
    line_style="solid",
    line_width=1.3,
    ref_twiss=None,
    ref_line_style="dashed",
    ref_line_width=2.5,
    scales={"eta_x": 10},
    overwrite=False,
):
    if overwrite:
        ax.clear()
    if ref_twiss:
        plot_twiss(
            ref_twiss,
            ax=ax,
            line_style=ref_line_style,
            line_width=ref_line_width,
            alpha=0.5,
        )

    plot_twiss(
        twiss, ax=ax, line_style=line_style, line_width=line_width, scales=scales
    )
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


# TODO:
#   * make sub_class of figure
#   * add attribute which defines which twiss parameters are plotted
#   * add twiss_functions argument similar to plot_twiss
class TwissPlot:
    """Convenience class to plot twiss parameters

    :param Twiss twiss: The name of the object.
    :param tuple: List of sections to plot. Can be either (min, max), "name" or object.
    :type tuple: List[Union[Tuple[float, float], str, Base]
    :param y_max float: Maximum y-limit
    :param y_min float: Minimum y-limit
    :param main bool: Wheter to plot whole ring or only given sections
    :param scales Dict[str, int]: Optional scaling factors for optical functions
    :param Twiss ref_twiss: Reference twiss values. Will be plotted as dashed lines.
    :param pairs: List of (element, attribute)-pairs to create interactice sliders for.
    :type pairs: List[Tuple[Element, str]]
    """

    def __init__(
        self,
        twiss,
        twiss_functions=("beta_x", "beta_y", "eta_x"),
        *,
        sections=None,
        y_min=None,
        y_max=None,
        main=True,
        scales={"eta_x": 10},
        ref_twiss=None,
        pairs=None,
    ):
        self.fig = plt.figure()
        self.twiss = twiss
        self.lattice = twiss.lattice
        self.twiss_functions = twiss_functions
        self.scales = scales
        height_ratios = [4, 14] if (main and sections) else [1]
        main_grid = grid_spec.GridSpec(
            len(height_ratios), 1, self.fig, height_ratios=height_ratios
        )
        self.axs_sections = []  # TODO: needed for update function

        if pairs:
            fig_sliders, axs = plt.subplots(nrows=len(pairs))
            if not isinstance(axs, Iterable):
                axs = (axs,)
            self.sliders = []
            for ax, (element, attribute) in zip(axs, pairs):
                initial_value = getattr(element, attribute)
                label = f"{element.name} {attribute}"
                slider = Slider(ax, label, -5, 5, initial_value)
                slider.on_changed(
                    lambda value, element=element, attribute=attribute: (
                        setattr(element, attribute, value),
                        self.update(),
                    )
                )
                self.sliders.append(slider)  # prevent garbage collection

        if main:
            self.ax_main = self.fig.add_subplot(main_grid[0])
            _twiss_plot_section(
                self.twiss,
                self.ax_main,
                ref_twiss=ref_twiss,
                y_min=y_min,
                y_max=y_max,
                annotate_elements=False,
                scales=scales,
            )

        if sections:
            n_sections = len(sections)
            rows, cols = find_optimal_grid(n_sections)
            sub_grid = grid_spec.GridSpecFromSubplotSpec(rows, cols, main_grid[1])
            self.axs_sections = [
                self.fig.add_subplot(sub_grid[i]) for i in range(len(sections))
            ]
            for i, section in enumerate(sections):
                if isinstance(section, (str, Base)):
                    obj = self.lattice[section] if isinstance(section, str) else section
                    index = self.lattice.indices[obj][0]
                    x_min = sum(obj.length for obj in self.lattice.arrangement[:index])
                    x_max = x_min + obj.length
                else:
                    x_min, x_max = section

                _twiss_plot_section(
                    self.twiss,
                    self.axs_sections[i],
                    ref_twiss=ref_twiss,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    annotate_elements=True,
                    scales=scales,
                )

        handles, labels = self.fig.axes[0].get_legend_handles_labels()
        self.fig.legend(handles, labels, loc="upper left", ncol=10, frameon=False)
        self.fig.suptitle(twiss.lattice.name, ha="right", x=0.98)
        self.fig.tight_layout()

    def update(self):
        twiss = self.twiss
        for ax in [self.ax_main] + self.axs_sections:
            for line, function in zip(ax.lines, self.twiss_functions):
                data = getattr(twiss, function)
                scale = self.scales.get(function)
                if scale is not None:
                    data *= scale
                line.set_data(twiss.s, data)
        self.fig.canvas.draw_idle()


def find_optimal_grid(n):
    rows, cols = 1, 1
    while rows * cols < n:
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

    return ax
