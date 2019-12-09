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
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("../apace"))
sys.path.insert(0, os.path.abspath(".."))
# noinspection PyUnresolvedReferences
from __about__ import __title__, __version__, __author__  # noqa: E402

# -- Project information -----------------------------------------------------
# https://stackoverflow.com/questions/56336234/build-fail-sphinx-error-contents-rst-not-found
master_doc = "index"

project = __title__
copyright = "%d %s" % (datetime.now().year, __author__)
author = __author__

# The short X.Y version
version = __version__
# The full version, including alpha/beta/rc tags
release = __version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = []

# AutoDoc
# extensions = ['sphinx.ext.autodoc']

# AutoAPI
extensions.append("autoapi.extension")
autoapi_dirs = [os.path.join("..", __title__)]
autoapi_root = "reference"
autoapi_options = ["members", "undoc-members"]
autoapi_add_toctree_entry = False
autoapi_template_dir = "_templates/autoapi"
# # noinspection SpellCheckingInspection
# autoapi_python_class_content = 'both'
# autoapi_include_summaries = True
autoapi_generate_api_docs = True

# sphinx-nbexamples
extensions.append("sphinx_nbexamples")
# TODO: build examples on apace-examples CI
# on_rtd = os.environ.get("READTHEDOCS", None) == "True"
# process_examples = not on_rtd
examples_dirs = ["../../axpace-examples"]
example_gallery_config = dict(
    urls="https://github.com/andreasfelix/apace-examples/blob/master",
    pattern=".+.ipynb",
)


# Auto summary
# extensions.append('sphinx.ext.autosummary')
# autosummary_generate = True
# autosummary_generate_overwrite = True
# autosummary_imported_members=True

# Markdown support
# extensions.append('m2r')
extensions.append("recommonmark")
# source_suffix = ['.rst', '.md']

# Auto section label
# extensions.append('sphinx.ext.autosectionlabel')

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
#
html_theme = "sphinx_rtd_theme"
# html_theme = 'press'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
