import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections.abc import Iterable

colors = {"Bend": "#ffc425", "Quad": '#d11141', "Sext": "#00b159", "Drift": "#FFFFFF"}
fs = 10
cmap = mpl.cm.Set1


def paint_lattice(ax, main_cell, xmin, xmax, ymin, ymax, annotate_elements, annotate_cells):
    # TODO: height should depented on plot_height, not on y_max!!!
    yspan = ymax - ymin
    rec_height = yspan / 16

    start = end = 0
    n_elements = len(main_cell.lattice)
    for i, element in enumerate(main_cell.lattice):
        end += element.length
        next_element = main_cell.lattice[i + 1] if i < n_elements - 1 else None
        if element != next_element:
            if end > xmin and start < xmax and element.type != "Drift":
                rec_length = (end if end < xmax else xmax) - (start if start > xmin else xmin)
                rectangle = plt.Rectangle((start if start > xmin else xmin, ymax - rec_height / 2), rec_length,
                                          rec_height, fc=colors[element.type], clip_on=False, zorder=10)
                ax.add_patch(rectangle)

            if start > xmin and end < xmax and element.type != "Drift":
                if annotate_elements:
                    sign, va = (1, "bottom") if element.type == "Quad" else (-1, "top")
                    ax.annotate(element.name, xy=((start + end) / 2, ymax + sign * 0.6 * rec_height), fontsize=fs,
                                va=va, ha='center', annotation_clip=False, zorder=11)

            start = end

    if annotate_cells:
        y0 = ymax - yspan / 8
        pos = 0
        for cell in main_cell.tree:
            if cell.type == "Cell" and cell.length > 0.05 * main_cell.length:
                x0 = pos + cell.length / 2
                ax.annotate(cell.name, xy=(x0, y0), fontsize=fs, va='top', ha='center', clip_on=True, zorder=102)
            pos += cell.length


def plot_twiss(ax, twiss, linestyle="solid", linewidth=1.3, alpha=1.0, etax_scale=10):
    ax.plot(twiss.s, twiss.eta_x * etax_scale, color=cmap(2 / 9), linewidth=linewidth, linestyle=linestyle, alpha=alpha)
    ax.plot(twiss.s, twiss.beta_y, color=cmap(1 / 9), linewidth=linewidth, linestyle=linestyle, alpha=alpha)
    ax.plot(twiss.s, twiss.beta_x, color=cmap(0 / 9), linewidth=linewidth, linestyle=linestyle, alpha=alpha)


def set_limits(ax, main_cell, xmin=None, xmax=None, ymin=None, ymax=None):
    xmin = xmin if xmin else 0
    xmax = xmax if xmax else main_cell.length
    ylim = ax.get_ylim()
    ymin = ymin if ymin else -0.5
    ymax = ymax if ymax else 1.1 * ylim[1]
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    return xmin, xmax, ymin, ymax


def set_grid(ax, main_cell, x_min, x_max, y_min, y_max, N_xticks, N_yticks):
    ax.xaxis.grid(which='minor', linestyle='dotted')
    ax.yaxis.grid(alpha=0.5, zorder=0, linestyle='dotted')
    if N_xticks:
        linspace = np.linspace(x_min, x_max, N_xticks)
        cell_length_list = [0]
        cell_length_list.extend([cell.length for cell in main_cell.tree])
        pos_tick = np.add.accumulate(cell_length_list) if not (x_min and x_max) else linspace
        ax.set_xticks(pos_tick, minor=True)
        ax.set_xticks(linspace)
    if N_yticks:
        ax.set_yticks(np.arange(int(y_min), int(y_max), N_yticks))
    ax.set_xlabel('orbit position $s$/m')


def annotate_info(main_cell, twiss, etax_scale=10):
    fig = plt.gcf()
    ax = plt.gca()
    margin = 0.02
    fs = 15

    ax.annotate(main_cell.name, xy=(1 - margin, 1 - margin), xycoords='figure fraction', va='top', ha='right',
                fontsize=fs)
    # annolist_string1 = f"$Q_x$: {twiss.Qx:.2f} ({twiss.Qx_freq:.0f} kHz)   $Q_y$: {twiss.Qy:.2f} ({twiss.Qy_freq:.0f} kHz)   $\\alpha_C$: {twiss.alphac:.2e}"
    # fig.annotate(annolist_string1, xy=(start, height_1), xycoords='figure fraction', va='center', ha='left', fontsize=fs)

    r = fig.canvas.get_renderer()
    string = ['$\\beta_x$/m', '$\\beta_y$/m', f'$\\eta_x$/{100 / etax_scale:.0f}cm']
    w = margin

    for i, s in enumerate(string):
        plt.annotate(s, xy=(w, 1 - margin), xycoords='figure fraction', color=mpl.cm.Set1(i / 9), fontsize=fs, va="top",
                     ha="left")
        w += len(s) * 0.005

    # space = 0
    # xmin, xmax = ax.get_xlim()
    # for i, s in enumerate(string):
    #     t = ax.annotate(s, xy=(w, 1 - margin), xycoords='figure fraction', color=mpl.cm.Set1(i / 9), fontsize=fs, va="top", ha="left")
    #     transf = ax.transData.inverted()
    #     bb = t.get_window_extent(renderer=r)
    #     bb = bb.transformed(transf)
    #     w = w + (bb.xmax - bb.xmin) / (xmax - xmin) + space


def plot_full(ax,
              twiss,
              main_cell=None,
              x_min=None, x_max=None, y_min=None, y_max=None,
              N_xticks=17, N_yticks=4,
              annotate_elements=True, annotate_cells=True,
              line_style="solid", linewidth=1.3,
              ref_twiss=None,
              ref_linestyle="dashed", ref_linewidth=2.5,
              etax_scale=10,
              overwrite=False):
    if overwrite: ax.clear()
    if ref_twiss: plot_twiss(ax, ref_twiss, linestyle=ref_linestyle, linewidth=ref_linewidth, alpha=0.5)
    plot_twiss(ax, twiss, linestyle=line_style, linewidth=linewidth, etax_scale=etax_scale)
    if main_cell:
        x_min, x_max, y_min, y_max = set_limits(ax, main_cell, x_min, x_max, y_min, y_max)
        set_grid(ax, main_cell, x_min, x_max, y_min, y_max, N_xticks, N_yticks)
        paint_lattice(ax, main_cell, x_min, x_max, y_min, y_max, annotate_elements, annotate_cells)




def plot_lattice(twiss,
                 main_cell=None,
                 main=True,
                 figsize=(16, 9),
                 sections=None,
                 ymin=None, ymax=None,
                 etax_scale=10,
                 ref_twiss=None,
                 path=None):
    fig = plt.figure(figsize=figsize)  # , constrained_layout=True)
    height_ratios = [2, 7] if (main and sections) else [1]
    main_grid = gridspec.GridSpec(len(height_ratios), 1, figure=fig, height_ratios=height_ratios)

    if main:
        ax = fig.add_subplot(main_grid[0])
        plot_full(ax, twiss, main_cell, ref_twiss=ref_twiss, y_min=ymin, y_max=ymax, annotate_elements=False,
                  etax_scale=etax_scale)

    if sections:
        if isinstance(sections, str) or not isinstance(sections[0], Iterable): sections = [sections]

        N_sections = len(sections)
        rows, cols = find_optimal_grid(N_sections)
        sub_grid = gridspec.GridSpecFromSubplotSpec(rows, cols, subplot_spec=main_grid[-1])
        for i, section in enumerate(sections):
            ax = fig.add_subplot(sub_grid[i])

            if isinstance(section, str):
                pass  # TODO: implement cell_start + cell_end
            else:
                xmin, xmax = section[0], section[1]

            plot_full(ax, twiss, main_cell, ref_twiss=ref_twiss, x_min=xmin, x_max=xmax, y_min=ymin, y_max=ymax,
                      annotate_elements=True, N_xticks=None)

    fig.tight_layout()
    fig.subplots_adjust(top=0.93)
    annotate_info(main_cell, twiss, etax_scale=etax_scale)
    if path: fig.savefig(path)
    return fig


def find_optimal_grid(N):
    rows, cols = 1, 1
    while rows * cols < N:
        cols += 1
        rows, cols = cols, rows

    return (rows, cols) if cols >= rows else (cols, rows)
