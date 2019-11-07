Command line tool
*****************

**apace** also has a simple command line tool which gets automatically installed when installing with pip. This tool is currently work in progress, but the calculation of the Twiss parameter should already be functioning.

Installing the CLI
==================

The **apace-cli** should be already available if apace was installed using pip. It can  be invoked from the command line via::

    apace

Getting Help
============

To get help use the :code:`--help` flag,

.. code::

    apace --help

which should output something like this:

.. code:: text

    usage: apace [-h] [--version] {help,twiss,convert} ...

    This is the apace CLI.

    positional arguments:
      {help,twiss,convert}
        help                Get help
        twiss               plot or save twiss functions to file
        convert             convert lattice files.

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit




The twiss subcommand
====================

Plot Twiss parameter for a given lattice:

.. code:: sh

    apace twiss path/to/lattice.json

Other options:

.. code::

    usage: apace twiss [-h] [-o OUTPUT_PATH] [-v] [-q] [-show]
                       [-ref REF_LATTICE_PATH] [-y_min Y_MIN] [-y_max Y_MAX]
                       [-s SECTIONS] [-pos POSITIONS] [-m MULTI_KNOB]
                       path [path ...]

    positional arguments:
      path                  Path to lattice file or directory with lattice files.

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT_PATH, --output_path OUTPUT_PATH
                            Output path for plot
      -v, --verbose         Verbose
      -q, --quiet           Quiet
      -show, --show_plot    show interactive plot
      -ref REF_LATTICE_PATH, --ref_lattice_path REF_LATTICE_PATH
                            Path to reference lattice
      -y_min Y_MIN          Min Y-value
      -y_max Y_MAX          Max Y-value
      -s SECTIONS, --sections SECTIONS
                            Plot Twiss parameter at given sections. Can be a
                            2-tuple (START, END), the name of the section or
                            sequence those '[(START, END), SECTION_NAME, ...]'.
      -pos POSITIONS, --positions POSITIONS
                            Print Twiss parameter at given positions. Can be a
                            number, a 2-tuple (START, END), a section name or
                            sequence of those.
      -m MULTI_KNOB, --multi_knob MULTI_KNOB
                            Multi-knob (Assumes plot)




