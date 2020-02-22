import click
import matplotlib.pyplot as plt

from . import __version__
from . import Lattice, Twiss
from .plot import twiss_plot


@click.group()
@click.version_option(__version__)
def cli():
    pass


@cli.command()
@click.argument("location")
@click.option("-o", "--output", required=False, type=click.Path(), help="Output path.")
@click.option("--ref-lattice", required=False, help="Path or URL to reference lattice.")
@click.option("-s", "--sections", required=False, multiple=True, type=(float, float))
@click.option("--y-min", required=False, type=float)
@click.option("--y-max", required=False, type=float)
def twiss(location, output, ref_lattice, sections, y_min, y_max):
    """Plot the Twiss parameter for the lattice at LOCATION (path or URL)."""
    lattice = Lattice.from_file(location)
    twiss = Twiss(lattice)
    ref_twiss = Twiss(ref_lattice) if ref_lattice is not None else None
    twiss_plot(twiss, ref_twiss=ref_twiss, sections=sections, y_min=y_min, y_max=y_max)
    if output is None:
        plt.show()
    else:
        plt.savefig(output)
