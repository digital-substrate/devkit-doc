# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('./_ext'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DevKit'
copyright = '2025, Digital Substrate'
author = 'Digital Substrate'
release = '1.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
	'sphinx.ext.duration',
	'sphinx.ext.doctest',
	'sphinx.ext.autodoc',
	'sphinx.ext.autosummary',
	'myst_parser',
	'sphinx_copybutton',
	'dsm_lexer',
	'pyi_signatures',
]

templates_path = ['_templates']
exclude_patterns = []

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = True

# Copy-button: strip Python REPL and shell prompts so the copied snippet is
# directly executable.
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ['custom.css']

# Furo theme options
html_theme_options = {
    'navigation_with_keys': True,
    'sidebar_hide_name': False,
}

# MyST parser settings - limit auto-generated TOC depth from headings
myst_heading_anchors = 3  # Generate anchors for h1-h3 only
