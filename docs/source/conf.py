# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys

from m2r import MdInclude
from recommonmark.transform import AutoStructify

# -- Path setup --------------------------------------------------------------

module_path = os.path.abspath(os.path.join(__file__, '../../../src'))
sys.path.insert(0, module_path)
print(f"adding {module_path} which contains {os.listdir(module_path)}")


# -- Project information -----------------------------------------------------

project = 'personio-py'
copyright = '2020, Alexander Thamm GmbH'
author = 'Sebastian Straub'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.duration',
    'sphinx.ext.viewcode',
    'recommonmark',
]

# extension config

autosectionlabel_prefix_document = True

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'canonical_url': 'https://at-gmbh.github.io/personio-py/',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

html_context = {
    "display_github": True,
    "github_user": "at-gmbh",
    "github_repo": "personio-py",
    "github_version": "master",
    "conf_py_path": "/docs/source/",
}


def setup(app):
    # recommonmark & autostructify (enables fancy stuff like `eval_rst`)
    app.add_config_value('recommonmark_config', {
        'enable_eval_rst': True,
        'enable_auto_toc_tree': True,
    }, True)
    app.add_transform(AutoStructify)

    # m2r and mdinclude, allow us to reference markdown files in the root folder
    # all those settings are necessary because m2r has not been updated in a while...
    app.add_config_value('no_underscore_emphasis', False, 'env')
    app.add_config_value('m2r_parse_relative_links', False, 'env')
    app.add_config_value('m2r_anonymous_references', False, 'env')
    app.add_config_value('m2r_disable_inline_math', False, 'env')
    app.add_directive('mdinclude', MdInclude)
