import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid_spec
from collections.abc import Iterable

colors = {"Bend": "#ffc425", "Quad": '#d11141', "Sext": "#00b159", "Drift": "#FFFFFF"}
fs = 10
c_map = mpl.cm.Set1


def paint_lattice(ax, main_cell, x_min, x_max, y_min, y_max, annotate_elements, annotate_cells):
    # TODO: height should depend on plot_height, not on y_max!!!
    y_span = y_max - y_min
    rec_height = y_span / 16

    start = end = 0
    n_elements = len(main_cell.lattice)
    for i, element in enumerate(main_cell.lattice):
        end += element.length
        next_element = main_cell.lattice[i + 1] if i < n_elements - 1 else None
        if element != next_element:
            if end > x_min and start < x_max and element.type != "Drift":
                rec_length = (end if end < x_max else x_max) - (start if start > x_min else x_min)
                rectangle = plt.Rectangle((start if start > x_min else x_min, y_max - rec_height / 2), rec_length,
                                          rec_height, fc=colors[element.type], clip_on=False, zorder=10)
                ax.add_patch(rectangle)

            if start > x_min and end < x_max and element.type != "Drift":
                if annotate_elements:
                    sign, va = (1, "bottom") if element.type == "Quad" else (-1, "top")
                    ax.annotate(element.name, xy=((start + end) / 2, y_max + sign * 0.6 * rec_height), fontsize=fs,
                                va=va, ha='center', annotation_clip=False, zorder=11)

            start = end

    if annotate_cells:
        y0 = y_max - y_span / 8
        pos = 0
        for cell in main_cell.tree:
            if cell.type == "Cell" and cell.length > 0.05 * main_cell.length:
                x0 = pos + cell.length / 2
                ax.annotate(cell.name, xy=(x0, y0), fontsize=fs, va='top', ha='center', clip_on=True, zorder=102)
            pos += cell.length


def plot_twiss(ax, twiss, line_style='solid', line_width=1.3, alpha=1.0, eta_x_scale=10):
    ax.plot(twiss.s, twiss.eta_x * eta_x_scale, color=c_map(2 / 9), linewidth=line_width, linestyle=line_style,
            alpha=alpha)
    ax.plot(twiss.s, twiss.beta_y, color=c_map(1 / 9), linewidth=line_width, linestyle=line_style, alpha=alpha)
    ax.plot(twiss.s, twiss.beta_x, color=c_map(0 / 9), linewidth=line_width, linestyle=line_style, alpha=alpha)


def set_limits(ax, main_cell, x_min=None, x_max=None, y_min=None, y_max=None):
    x_min = x_min if x_min else 0
    x_max = x_max if x_max else main_cell.length
    y_lim = ax.get_ylim()
    y_min = y_min if y_min else -0.5
    y_max = y_max if y_max else 1.1 * y_lim[1]
    ax.set_xlim([x_min, x_max])
    ax.set_ylim([y_min, y_max])
    return x_min, x_max, y_min, y_max


def set_grid(ax, main_cell, x_min, x_max, y_min, y_max, N_xticks, N_yticks):
    ax.xaxis.grid(which='minor', linestyle='dotted')
    ax.yaxis.grid(alpha=0.5, zorder=0, linestyle='dotted')
    if N_xticks:
        lin = np.linspace(x_min, x_max, N_xticks)
        cell_length_list = [0]
        cell_length_list.extend([cell.length for cell in main_cell.tree])
        pos_tick = np.add.accumulate(cell_length_list) if not (x_min and x_max) else lin
        ax.set_xticks(pos_tick, minor=True)
        ax.set_xticks(lin)
    if N_yticks:
        ax.set_yticks(np.arange(int(y_min), int(y_max), N_yticks))
    ax.set_xlabel('orbit position $s$/m')


def annotate_info(main_cell, twiss, eta_x_scale=10):
    # fig = plt.gcf()
    ax = plt.gca()
    margin = 0.02
    fs = 15

    ax.annotate(main_cell.name, xy=(1 - margin, 1 - margin), xycoords='figure fraction', va='top', ha='right',
                fontsize=fs)
    # annolist_string1 = f"$Q_x$: {twiss.Qx:.2f} ({twiss.Qx_freq:.0f} kHz)   $Q_y$: {twiss.Qy:.2f} ({twiss.Qy_freq:.0f} kHz)   $\\alpha_C$: {twiss.alphac:.2e}"
    # fig.annotate(annolist_string1, xy=(start, height_1), xycoords='figure fraction', va='center', ha='left', fontsize=fs)

    # r = fig.canvas.get_renderer()
    string = ['$\\beta_x$/m', '$\\beta_y$/m', f'$\\eta_x$/{100 / eta_x_scale:.0f}cm']
    w = margin

    for i, s in enumerate(string):
        plt.annotate(s, xy=(w, 1 - margin), xycoords='figure fraction', color=mpl.cm.Set1(i / 9), fontsize=fs, va="top",
                     ha="left")
        w += len(s) * 0.005

    # space = 0
    # x_min, x_max = ax.get_xlim()
    # for i, s in enumerate(string):
    #     t = ax.annotate(s, xy=(w, 1 - margin), xycoords='figure fraction', color=mpl.cm.Set1(i / 9), fontsize=fs, va="top", ha="left")
    #     transf = ax.transData.inverted()
    #     bb = t.get_window_extent(renderer=r)
    #     bb = bb.transformed(transf)
    #     w = w + (bb.x_max - bb.x_min) / (x_max - x_min) + space


def plot_full(ax,
              twiss,
              main_cell=None,
              x_min=None, x_max=None, y_min=None, y_max=None,
              N_xticks=17, N_yticks=4,
              annotate_elements=True, annotate_cells=True,
              line_style="solid", line_width=1.3,
              ref_twiss=None,
              ref_line_style="dashed", ref_line_width=2.5,
              eta_x_scale=10,
              overwrite=False):
    if overwrite:
        ax.clear()

    if ref_twiss:
        plot_twiss(ax, ref_twiss, line_style=ref_line_style, line_width=ref_line_width, alpha=0.5)

    plot_twiss(ax, twiss, line_style=line_style, line_width=line_width, eta_x_scale=eta_x_scale)
    if main_cell:
        x_min, x_max, y_min, y_max = set_limits(ax, main_cell, x_min, x_max, y_min, y_max)
        set_grid(ax, main_cell, x_min, x_max, y_min, y_max, N_xticks, N_yticks)
        paint_lattice(ax, main_cell, x_min, x_max, y_min, y_max, annotate_elements, annotate_cells)


def plot_lattice(twiss,
                 main_cell=None,
                 main=True,
                 fig_size=(16, 9),
                 sections=None,
                 y_min=None, y_max=None,
                 eta_x_scale=10,
                 ref_twiss=None,
                 path=None):
    fig = plt.figure(figsize=fig_size)  # , constrained_layout=True)
    height_ratios = [2, 7] if (main and sections) else [1]
    main_grid = grid_spec.GridSpec(len(height_ratios), 1, figure=fig, height_ratios=height_ratios)

    if main:
        ax = fig.add_subplot(main_grid[0])
        plot_full(ax, twiss, main_cell, ref_twiss=ref_twiss, y_min=y_min, y_max=y_max, annotate_elements=False,
                  eta_x_scale=eta_x_scale)

    if sections:
        if isinstance(sections, str) or not isinstance(sections[0], Iterable): sections = [sections]

        N_sections = len(sections)
        rows, cols = find_optimal_grid(N_sections)
        sub_grid = grid_spec.GridSpecFromSubplotSpec(rows, cols, subplot_spec=main_grid[-1])
        for i, section in enumerate(sections):
            ax = fig.add_subplot(sub_grid[i])

            if isinstance(section, str):
                pass  # TODO: implement cell_start + cell_end
            else:
                x_min, x_max = section[0], section[1]

            plot_full(ax, twiss, main_cell, ref_twiss=ref_twiss, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,
                      annotate_elements=True, N_xticks=None)

    fig.tight_layout()
    fig.subplots_adjust(top=0.93)
    annotate_info(main_cell, twiss, eta_x_scale=eta_x_scale)
    if path: fig.savefig(path)
    return fig


def find_optimal_grid(N):
    rows, cols = 1, 1
    while rows * cols < N:
        cols += 1
        rows, cols = cols, rows

    return (rows, cols) if cols >= rows else (cols, rows)
