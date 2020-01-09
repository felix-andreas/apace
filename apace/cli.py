import argparse
import ast
import io
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from .__about__ import __version__
from .io import read_lattice_file_json
from .twiss import Twiss
from .plot import twiss_plot
from .classes import Quadrupole


def main():
    parser = argparse.ArgumentParser(description="This is the apace CLI.")
    parser.add_argument("--version", action="version", version=str(__version__))
    subparsers = parser.add_subparsers(dest="subparser")

    subparsers.add_parser("help", help="Get help")

    parser_plot = subparsers.add_parser(
        "twiss", help="plot or save twiss functions to file"
    )
    parser_plot.set_defaults(func=plot)
    parser_plot.add_argument(
        "path",
        nargs="+",
        type=str,
        help="Path to lattice file or directory with lattice files.",
    )
    parser_plot.add_argument(
        "-o", "--output_path", type=str, help="Output path for plot"
    )
    parser_plot.add_argument("-v", "--verbose", action="store_true", help="Verbose")
    parser_plot.add_argument("-q", "--quiet", action="store_true", help="Quiet")
    parser_plot.add_argument(
        "-show", "--show_plot", action="store_true", help="show interactive plot"
    )
    parser_plot.add_argument(
        "-ref", "--ref_lattice_path", type=str, help="Path to reference lattice"
    )
    parser_plot.add_argument("-y_min", type=int, help="Min Y-value")
    parser_plot.add_argument("-y_max", type=int, help="Max Y-value")
    parser_plot.add_argument(
        "-s",
        "--sections",
        type=str,  # should be own argument for print twiss parameter
        help="Plot Twiss parameter at given sections. "
        "Can be a 2-tuple (START, END), the name of the section "
        "or sequence those '[(START, END), SECTION_NAME, ...]'.",
    )

    parser_plot.add_argument(
        "-pos",
        "--positions",
        type=str,  # should be own argument for print twiss parameter
        help="Print Twiss parameter at given positions. "
        "Can be a number, a 2-tuple (START, END), a section name or sequence of those.",
    )
    parser_plot.add_argument(
        "-m", "--multi_knob", type=str, help="Multi-knob (Assumes plot)"
    )

    parser_lattice = subparsers.add_parser("convert", help="convert lattice files.")
    parser_lattice.set_defaults(func=convert_lattice)

    args = parser.parse_args()

    if len(sys.argv) < 2 or args.subparser == "help":
        parser.print_help()
        return

    if args.sections:  # TODO: only check if func == plot
        args.sections = ast.literal_eval(args.sections)
        if is_section(args.sections):  # check if sections is list/tuple of sections
            args.sections = [args.sections]
        elif not (
            isinstance(args.sections, (tuple, list))
            and all(is_section(x) for x in args.sections)
        ):
            raise Exception(
                "Section argument is not valid! "
                "Must be string (section_name), tuple (x_min, x_max) or list of these."
            )

    if args.positions:  # TODO: only check if func == plot
        args.positions = ast.literal_eval(args.positions)
        if isinstance(args.positions, (int, float)):
            args.positions = [args.positions]
        elif not (
            isinstance(args.positions, (tuple, list))
            and all(isinstance(x, (int, float, tuple, list)) for x in args.positions)
        ):
            raise Exception(
                "Position argument is not valid! "
                "Must be string (section_name), tuple (x_min, x_max), a number or list of these."
            )

    args.func(args)


def plot(args):
    if args.multi_knob:
        plot_multi_knob_quads(args)
    else:
        plot_multiple(args)


def is_section(x):
    return isinstance(x, str) or (
        isinstance(x, (list, tuple))
        and len(x) == 2
        and all(isinstance(y, (int, float)) for y in x)
    )


def print_twiss_array(s, twiss_array):
    io_string = io.StringIO()
    width = 10
    np.savetxt(
        io_string,
        np.column_stack((s, twiss_array.T)),
        fmt=f"%{width}.3f",
        delimiter=",",
        header=",  ".join(
            f"{x:>{width - 2}}"
            for x in (
                "s",
                "beta_x",
                "beta_y",
                "alpha_x",
                "alpha_y",
                "gamma_x",
                "gamma_y",
                "eta_x",
                "dds_eta_x",
            )
        ),
    )

    output = io_string.getvalue()
    print(output)


def plot_multiple(args):
    path_list = args.path
    ref_path = os.path.abspath(args.ref_lattice_path) if args.ref_lattice_path else None

    lattice_files = []
    for path in path_list:
        abs_path = os.path.abspath(path)

        if os.path.isfile(abs_path):
            lattice_files.append(abs_path)
        elif os.path.isdir(abs_path):
            for sub_path, sub_dirs, files in os.walk(abs_path):
                files.sort()
                lattice_files.extend(
                    [
                        os.path.join(abs_path, sub_path, file)
                        for file in files
                        if file.endswith(".json")
                    ]
                )
        else:
            raise Exception(f"There is no {abs_path}!")

    figs = []
    for file_path in lattice_files:
        main_lattice = read_lattice_file_json(file_path)
        twiss = Twiss(main_lattice)

        if args.verbose:
            print(
                f"Name: {main_lattice.name}\n"
                f"Description: {main_lattice.description}\n"
                f"Length: {main_lattice.length}\n"
                f"Number of elements: {len(main_lattice.arrangement)}\n"
                f"Number of independent elements: {len(main_lattice.elements)}\n"
                f"Horizontal Tune: {twiss.tune_x:.3f}\n"
                f"Vertical Tune: {twiss.tune_y:.3f}\n",
            )

        if args.positions:
            tmp_mask = [
                np.searchsorted(twiss.s, position) for position in args.positions
            ]
            tmp_mask = tuple(
                slice(x[0], x[1] + 1) if isinstance(x, np.ndarray) else x
                for x in tmp_mask
            )
            mask = np.r_[tmp_mask]
            print_twiss_array(twiss.s[mask], twiss.twiss_array.T[mask].T)

        if args.output_path or args.show_plot:
            ref_main_lattice = read_lattice_file_json(ref_path) if ref_path else None
            ref_twiss = Twiss(ref_main_lattice) if ref_main_lattice else None
            fig = twiss_plot(
                twiss,
                main_lattice,
                ref_twiss=ref_twiss,
                sections=args.sections,
                y_min=args.y_min,
                y_max=args.y_max,
            )
            figs.append(fig)

    if args.output_path:
        with PdfPages(args.output_path) as pdf:
            for fig in figs:
                pdf.savefig(fig)

    if args.show_plot:
        plt.show()


def plot_multi_knob_quads(args):
    lattice1 = read_lattice_file_json(args.path[0])
    lattice2 = read_lattice_file_json(args.multi_knob)
    lattice_out = read_lattice_file_json(args.path[0])
    ref_path = os.path.abspath(args.ref_lattice_path) if args.ref_lattice_path else None

    if lattice1.elements.keys() != lattice2.elements.keys():
        raise Exception("The lattices have not the same magnets!")
    diff_magnets = {}
    for name in lattice1.elements.keys():
        e1, e2 = lattice1.elements[name], lattice2.elements[name]
        if isinstance(e1, Quadrupole) and e1.k1 != e2.k1:
            diff_magnets[name] = (e1.k1, e2.k1)

    with PdfPages(args.output_path) as pdf:
        for i in np.linspace(0, 1, 11):
            lattice_out.name = f"{lattice1.name} vs {lattice2.name} | {i:.2f}"
            for element, values in diff_magnets.items():
                lattice_out.elements[element].k1 = values[0] * i + (1 - i) * values[1]

            ref_main_lattice = read_lattice_file_json(ref_path) if ref_path else None
            ref_twiss = Twiss(ref_main_lattice) if ref_main_lattice else None
            twiss_plot(
                Twiss(lattice_out),
                ref_twiss=ref_twiss,
                sections=args.sections,
                y_min=args.y_min,
                y_max=args.y_max,
            )
            pdf.savefig()


def convert_lattice(args):
    return NotImplemented


if __name__ == "__main__":
    main()
