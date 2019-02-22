import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

colors = {"Bend": "#ffc425", "Quad": '#d11141', "Sext": "#00b159", "Drift": "#FFFFFF"}
fs = 9
cmap = mpl.cm.Set1


def paint_lattice(ax, maincell, xmin, xmax, ymin, ymax, annotate_elements, annotate_cells):
    yspan = ymax - ymin
    rec_height = yspan / 16

    start = end = 0
    n_elements = len(maincell.lattice)
    for i, element in enumerate(maincell.lattice):
        end += element.length
        next_element = maincell.lattice[i + 1] if i < n_elements - 1 else None
        if element != next_element:
            if end > xmin and start < xmax and element.type != "Drift":
                rec_length = (end if end < xmax else xmax) - (start if start > xmin else xmin)
                rectangle = plt.Rectangle((start if start > xmin else xmin, ymax - rec_height / 2), rec_length, rec_height, fc=colors[element.type], clip_on=False, zorder=10)
                ax.add_patch(rectangle)

            if start > xmin and end < xmax and element.type != "Drift":
                if annotate_elements:
                    sign, va = (1, "bottom") if element.type == "Quad" else (-1, "top")
                    ax.annotate(element.name, xy=((start + end) / 2, ymax + sign * 0.6 * rec_height), fontsize=fs, va=va, ha='center', annotation_clip=False, zorder=11)

            start = end

    if annotate_cells:
        y0 = ymax - yspan / 12
        pos = 0
        for cell in maincell.tree:
            if cell.type == "Cell" and cell.length > 0.05 * maincell.length:
                x0 = pos + cell.length / 2
                ax.annotate(cell.name, xy=(x0, y0), fontsize=fs, va='center', ha='center', clip_on=True, zorder=102)
            pos += cell.length


def plot_twiss(ax, twiss, linestyle="solid", linewidth=1.3, alpha=1):
    ax.plot(twiss.s, twiss.etax * 10, color=cmap(2 / 9), linewidth=linewidth, linestyle=linestyle, alpha=alpha)
    ax.plot(twiss.s, twiss.betay, color=cmap(1 / 9), linewidth=linewidth, linestyle=linestyle, alpha=alpha)
    ax.plot(twiss.s, twiss.betax, color=cmap(0 / 9), linewidth=linewidth, linestyle=linestyle, alpha=alpha)

def set_limits(ax, maincell, xmin=None, xmax=None, ymin=None, ymax=None):
    xmin = xmin if xmin else 0
    xmax = xmax if xmax else maincell.length
    ylim = ax.get_ylim()
    ymin = ymin if ymin else -0.5
    ymax = ymax if ymax else 1.1 * ylim[1]
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    return xmin, xmax, ymin, ymax

def set_grid(ax, maincell, xmin, xmax, ymin, ymax, N_xticks, N_yticks):
    ax.xaxis.grid(which='minor', linestyle='dotted')
    ax.yaxis.grid(alpha=0.5, zorder=0, linestyle='dotted')
    linspace = np.linspace(xmin, xmax, N_xticks)
    cell_length_list = [0]
    cell_length_list.extend([cell.length for cell in maincell.tree])
    pos_tick = np.add.accumulate(cell_length_list) if not (xmin and xmax) else linspace
    ax.set_xticks(pos_tick, minor=True)
    ax.set_xticks(linspace)
    ax.set_yticks(np.arange(int(ymin), int(ymax), N_yticks))
    ax.set_xlabel('orbit position $s$/m')


def plot_full(ax,
              linbeamdyn,
              xmin=None, xmax=None, ymin=None, ymax=None,
              N_xticks=17, N_yticks=4,
              annotate_elements=True, annotate_cells=True,
              linestyle="solid", linewidth=1.3,
              ref_twiss=None,
              ref_linestyle="dashed", ref_linewidth=2.5,
              path=None, overwrite=False):

    maincell = linbeamdyn.maincell

    ax.clear() if overwrite else ...
    plot_twiss(ax, ref_twiss, linestyle=ref_linestyle, linewidth=ref_linewidth, alpha=0.5) if ref_twiss else ...
    plot_twiss(ax, linbeamdyn.twiss, linestyle=linestyle, linewidth=linewidth)
    xmin, xmax, ymin, ymax = set_limits(ax, maincell, xmin, xmax, ymin, ymax)
    set_grid(ax, maincell, xmin, xmax, ymin, ymax, N_xticks, N_yticks)
    paint_lattice(ax, maincell, xmin, xmax, ymin, ymax, annotate_elements, annotate_cells)

    if path: plt.savefig(path)
