import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "SQL Mock"
copyright = "2023, DeepL, Thomas Schmidt"
author = "DeepL, Thomas Schmidt"
release = "0.3.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary", "sphinx.ext.napoleon", "myst_parser"]

templates_path = ["_templates"]
exclude_patterns = []
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}


autodoc_inherit_docstrings = True
autosummary_generate = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_sidebars = {
    "**": [
        "globaltoc.html",
        "relations.html",  # needs 'show_related': True option to display
        "sourcelink.html",
        "searchbox.html",
    ]
}
html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "DeepLcom",  # Username
    "github_repo": "sql-mock",  # Repo name
    "github_version": "master",  # Version
    "conf_py_path": "/docsource/",  # Path in the checkout to the docs root
}
