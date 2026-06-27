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
	'sphinxext.opengraph',
	'dsm_lexer',
	'pyi_signatures',
	'sphinx_js',
]

# --- Node API reference (sphinx-js + TypeDoc) ---------------------------------
# Mirrors how the Python API reference consumes the installed `dsviper` wheel:
# the `@digitalsubstrate/dsviper` npm package supplies the TypeScript
# declarations (`index.d.ts`), which sphinx-js feeds to TypeDoc to generate the
# `dsviper-node/api/` pages. The package is installed at the repo root via
# `npm install` (see the root package.json) — required before `make html`, just
# as `pip install dsviper` is required for the Python reference.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
_NODE_BINDING = os.path.join(
	_REPO_ROOT, 'node_modules', '@digitalsubstrate', 'dsviper')
js_language = 'typescript'
root_for_relative_js_paths = _NODE_BINDING
js_source_path = os.path.join(_NODE_BINDING, 'index.d.ts')
jsdoc_tsconfig_path = os.path.join(_REPO_ROOT, 'tsconfig.typedoc.json')

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

# Workaround for a Sphinx 8.2.3 coverage-builder bug. The "modules specified
# in coverage_modules but not documented" branch of
# _determine_py_coverage_modules (sphinx/ext/coverage.py) calls
# logger.warning() with a positional arg but no `%s` in the message →
# TypeError in the logging handler: a non-fatal but alarming traceback in
# every build log. The cross-check it guards is also meaningless here: our API
# reference is generated with autosummary, which documents objects
# (dsviper.CommitDatabase, …) without emitting any `py:module` directive, so
# the builder's seen_modules is always empty and the check always "fails". We
# keep coverage_modules (it drives the object-level python.txt report we rely
# on) and reimplement the helper to drop only the seen/specified
# reconciliation. Remove once the upstream warning is fixed.
import sphinx.ext.coverage as _sphinx_coverage
from sphinx.locale import __ as _cov_gettext


def _determine_py_coverage_modules(coverage_modules, seen_modules,
                                   ignored_module_exps, py_undoc):
    if not coverage_modules:
        return sorted(seen_modules)
    modules = set()
    for mod_name in coverage_modules:
        try:
            modules |= _sphinx_coverage._load_modules(mod_name, ignored_module_exps)
        except ImportError as err:
            _sphinx_coverage.logger.warning(
                _cov_gettext('module %s could not be imported: %s'),
                mod_name, err)
            py_undoc[mod_name] = {'error': err}
    return sorted(modules)


_sphinx_coverage._determine_py_coverage_modules = _determine_py_coverage_modules

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

# sphinxext-opengraph: emit <meta name="description"> + Open Graph tags
# from the first paragraph after each page's H1. Same heuristic as
# tools/build_llms_txt.py — pages are already shaped for this.
ogp_site_url = html_baseurl
ogp_site_name = "DevKit Documentation"
ogp_description_length = 200
ogp_type = "website"

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
