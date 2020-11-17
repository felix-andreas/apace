import click
import matplotlib.pyplot as plt

from . import __version__
from . import Lattice, Twiss
from .plot import TwissPlot


@click.group()
@click.version_option(__version__)
def cli():
    pass


@cli.command()
@click.argument("location")
@click.option("-o", "--output", required=False, type=click.Path(), help="Output path.")
@click.option("-i", "--interactive", required=False, multiple=True, type=(str, str))
@click.option("--ref-lattice", required=False, help="Path or URL to reference lattice.")
@click.option("-s", "--sections", required=False, multiple=True, type=(float, float))
@click.option("--y-min", required=False, type=float)
@click.option("--y-max", required=False, type=float)
def twiss(location, output, interactive, ref_lattice, sections, y_min, y_max):
    """Plot the Twiss parameter of the lattice at LOCATION (path or URL)."""
    lattice = Lattice.from_file(location)
    options = dict(twiss=Twiss(lattice), sections=sections, y_min=y_min, y_max=y_max)
    if interactive:  # TODO: interactive seems frozen
        options["pairs"] = (
            [(lattice[name], attr) for name, attr in interactive]
            if interactive
            else None
        )

    if ref_lattice:
        options["ref_twiss"] = Twiss(ref_lattice)

    TwissPlot(**options)
    if output is None:
        plt.show()
    else:
        plt.savefig(output)
