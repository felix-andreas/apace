# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from pathlib import Path
from datetime import datetime

base_path = Path(__file__).resolve().parent
about: dict = {}
exec((base_path / "../apace/__about__.py").read_text(), about)

# -- Project information -----------------------------------------------------
# https://stackoverflow.com/questions/56336234/build-fail-sphinx-error-contents-rst-not-found
master_doc = "index"

project = about["__title__"]
copyright = "%d %s" % (datetime.now().year, about["__author__"])
author = about["__author__"]

# The short X.Y version
version = about["__version__"]
# The full version, including alpha/beta/rc tags
release = about["__version__"]

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = []

# AutoAPI
extensions.append("autoapi.extension")
autoapi_dirs = [base_path / "../apace"]
autoapi_root = "reference"
autoapi_options = ["members", "undoc-members"]
autoapi_add_toctree_entry = False
autoapi_template_dir = "_templates/autoapi"
# # noinspection SpellCheckingInspection
# autoapi_python_class_content = 'both'
# autoapi_include_summaries = True
autoapi_generate_api_docs = True

# Markdown support
# extensions.append('m2r')
extensions.append("recommonmark")
# source_suffix = ['.rst', '.md']

# Auto section label
# extensions.append('sphinx.ext.autosectionlabel')

# Sphinx-gallery
extensions.append("sphinx_gallery.gen_gallery")
sphinx_gallery_conf = {
    "examples_dirs": "../examples",  # path to your example scripts
    "gallery_dirs": "examples",  # path to where to save gallery generated output
    "backreferences_dir": False,
    "filename_pattern": "/",  # plot all Python files
}

# Intersphinx
extensions.append("sphinx.ext.intersphinx")
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": (
        "https://docs.scipy.org/doc/numpy/",
        None,
    ),  # TODO: check how sparse did it
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
}

# Support for NumPy and Google style docstrings
extensions.append("sphinx.ext.napoleon")

# Enable search-as-you-type feature for docs hosted by RTD
extensions.append("sphinx_search.extension")

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"
# html_theme = "press"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
