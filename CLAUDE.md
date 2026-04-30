# CLAUDE.md

## Project Overview

DevKit Documentation — Sphinx documentation for the dsviper ecosystem. Covers the DSM
language, Python API, Kibo code generator, and the developer toolchain.

This repo is the **source of truth** for all public documentation. The generated HTML
is integrated into the DevKit website for online access.

## Build Commands

```bash
# Prerequisites (includes dsviper for API reference generation)
pip install -r requirements.txt

# Build HTML
make html

# Clean rebuild (required after restructuring files)
make clean && make html

# Live preview
pip install sphinx-autobuild
sphinx-autobuild source build/html

# Quality gates
make doctest    # run all `{doctest}` examples (519 tests today)
make linkcheck  # validate every external URL
make coverage   # list dsviper symbols not referenced by autodoc/autosummary
make check      # run the three above in sequence — exits non-zero on first failure
                # (suitable for a git pre-commit hook)

# Build NotebookLM-friendly Markdown bundles (build/notebooklm/*.md)
make notebooklm

# Build a release-ready offline doc archive (build/dist/devkit-1.2-doc.zip)
make distzip

# Build a release-ready PDF (build/dist/devkit-1.2-doc.pdf)
# Requires BasicTeX + tex-gyre + gnu-freefont; uses xelatex.
make pdf
```

## Structure

```
source/
├��─ conf.py           # Sphinx configuration
├── index.rst         # Main page and top-level toctree
├── _ext/             # Custom extensions (dsm_lexer, pyi_signatures)
├── _static/          # CSS and images
├── _templates/       # Autosummary templates
├── _fixtures/        # Test fixtures consumed by `make doctest` (Tuto/model.dsm)
├── concepts/         # Viper architecture, philosophy, patterns
├── dsm/              # DSM language reference
├── python/           # Python guide + auto-generated API reference
└── tools/            # Toolchain (Kibo, dsm_util, IDE plugins, templates)

tools/
└── build_notebooklm.py  # Bundles Sphinx text output into NotebookLM sources
```

## Documentation Language

All documentation content must be written in **English**.

## Custom Extensions

### dsm_lexer
Pygments lexer for DSM syntax highlighting. Use ` ```dsm ` in Markdown code blocks.

### pyi_signatures
Extracts type hints from the installed `dsviper` package and injects them into
autodoc-generated API pages. Resolves inherited methods via class hierarchy.

## Conventions

- Use MyST Markdown (`.md`) for content pages, reStructuredText (`.rst`) for toctrees
- Code examples: prefer Python, wrap runnable snippets in ` ```{doctest} ` so
  `make doctest` validates them against the real `dsviper` runtime. The Tuto
  fixture (`source/_fixtures/Tuto/model.dsm`) is pre-loaded and `db`,
  `_tuto_defs`, `TUTO_*` are in scope via `doctest_global_setup` in `conf.py`.
- **Tuto fixture is mirrored** in the `dsm-samples` repo at
  `/Volumes/DigitalSubstrate/dsm-samples/Tuto/model.dsm`. Whenever you edit
  one, copy the change to the other in the same PR, otherwise the
  doc-tested model and the canonical sample drift apart.
- Doctest gotchas: continuation lines (`... `) inside an argument list
  conflict with the global `ELLIPSIS` flag — keep multi-arg calls on a
  single line. `commit_mutations()` does not auto-advance an implicit
  current commit; capture the returned id explicitly. `inject(<dict>)`
  does not wire the same type-bridge as `inject()` (no-arg → `__main__`).
- Directives: `{note}`, `{tip}`, `{warning}` for callouts
- After any file move or rename: `make clean && make html` (Sphinx caches old paths)

## Distribution Artifacts

`build/dist/` collects release-ready artifacts:

| Target           | Output                                | Notes                                       |
|------------------|---------------------------------------|---------------------------------------------|
| `make distzip`   | `devkit-<version>-doc.zip` (~8 MB)    | Multi-page HTML, full nav + search          |
| `make pdf`       | `devkit-<version>-doc.pdf` (~3 MB)    | xelatex, ~400 pages, complete API reference |

`DOC_VERSION` defaults to `1.2`; override from the environment if needed.

## Git Workflow

Commit format: `docs(section): Description`

Examples:
- `docs(python): add collections tutorial`
- `docs(tools): complete template model reference`
- `docs(dsm): fix function pool syntax examples`
