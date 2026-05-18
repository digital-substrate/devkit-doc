# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime
import doctest
import os
import sys
sys.path.insert(0, os.path.abspath('./_ext'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DevKit'
copyright = f'2025–{datetime.date.today().year}, Digital Substrate · Prose under CC-BY 4.0, code samples under MIT'
author = 'Digital Substrate'
release = '1.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
	'sphinx.ext.duration',
	'sphinx.ext.doctest',
	'sphinx.ext.autodoc',
	'sphinx.ext.autosummary',
	'sphinx.ext.coverage',
	'myst_parser',
	'sphinx_copybutton',
	'sphinx_sitemap',
	'dsm_lexer',
	'pyi_signatures',
]

templates_path = ['_templates']
exclude_patterns = ['_fixtures']

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = True

# Copy-button: strip Python REPL and shell prompts so the copied snippet is
# directly executable.
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True

# Doctest defaults: ELLIPSIS lets `...` match arbitrary output (handy for
# non-deterministic values like UUIDs and the host/pid prefix on ViperError
# messages); IGNORE_EXCEPTION_DETAIL ignores the exception message text so
# doctests survive harmless wording changes; NORMALIZE_WHITESPACE is forgiving
# about line wrapping in expected output.
doctest_default_flags = (
    doctest.ELLIPSIS
    | doctest.IGNORE_EXCEPTION_DETAIL
    | doctest.NORMALIZE_WHITESPACE
)

# Global doctest setup: load the bundled Tuto fixture model and inject its
# generated constants (TUTO_A_USER_LOGIN, TUTO_S_LOGIN, …) so Zone 2
# examples can use them without depending on a Kibo-generated package.
_FIXTURE_TUTO = os.path.join(os.path.dirname(__file__), '_fixtures', 'Tuto')
# Coverage builder: report which symbols of `dsviper` are not referenced by
# any autodoc/autosummary directive in the doc.
coverage_modules = ['dsviper']
coverage_show_missing_items = True

doctest_global_setup = f'''
from dsviper import *
_builder = DSMBuilder.assemble({_FIXTURE_TUTO!r})
_report, _dsm_defs, _tuto_defs = _builder.parse()
_tuto_defs.inject(globals())

def _new_tuto_db():
    """Fresh in-memory CommitDatabase pre-populated with Tuto definitions."""
    _db = CommitDatabase.create_in_memory()
    _db.extend_definitions(_tuto_defs)
    return _db

db = _new_tuto_db()
'''



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ['custom.css']

# Canonical URL — published on GitHub Pages at docs.digitalsubstrate.io
# (Sphinx emits <link rel="canonical"> tags so duplicate hosts are
# deprioritised by search engines).
html_baseurl = 'https://docs.digitalsubstrate.io/'

# Files copied verbatim to the root of build/html/.
# - CNAME tells GitHub Pages which custom domain to serve.
# - llms.txt follows the emerging convention (https://llmstxt.org) so LLM
#   agents crawling docs.digitalsubstrate.io discover the corpus structure.
# - robots.txt advertises the sitemap and the agent-readable surface
#   (llms.txt / llms-full.txt / version.json on the sister site).
html_extra_path = ['_static/CNAME', '_static/llms.txt', '_static/robots.txt']

# sphinx-sitemap: generate build/html/sitemap.xml from html_baseurl.
# Single-locale doc — disable the per-locale subtree to keep URLs flat.
sitemap_locales = [None]
sitemap_url_scheme = "{link}"

# Furo theme options
html_theme_options = {
    'navigation_with_keys': True,
    'sidebar_hide_name': False,
}

# MyST parser settings - limit auto-generated TOC depth from headings
myst_heading_anchors = 3  # Generate anchors for h1-h3 only

# -- LaTeX / PDF output ------------------------------------------------------
# xelatex handles Unicode natively (the doc uses box-drawing characters in
# ASCII diagrams), unlike pdflatex.
latex_engine = 'xelatex'

# `xindy` is not shipped with BasicTeX on macOS — fall back to the
# bundled `makeindex` instead.
latex_use_xindy = False


# -- Build hooks -------------------------------------------------------------

def setup(app):
    """Emit build/html/llms-full.txt at the end of every successful html build.

    Keeping the emission inside the Sphinx pipeline means anyone running
    plain `make html` (or the CI that publishes docs.digitalsubstrate.io)
    gets the llms-full.txt companion automatically — no extra Makefile
    target to forget.
    """
    _tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              os.pardir, "tools"))
    if _tools_dir not in sys.path:
        sys.path.insert(0, _tools_dir)
    import build_llms_full

    def _emit_llms_full(app, exception):
        if exception is not None:
            return
        if app.builder.name != "html":
            return
        from pathlib import Path
        out_path = Path(app.outdir) / "llms-full.txt"
        size = build_llms_full.write(out_path)
        print(f"wrote {out_path} ({size} bytes)")

    app.connect("build-finished", _emit_llms_full)
