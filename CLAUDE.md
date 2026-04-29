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

# Build NotebookLM-friendly text bundles (build/notebooklm/*.txt)
make notebooklm
```

## Structure

```
source/
├��─ conf.py           # Sphinx configuration
├── index.rst         # Main page and top-level toctree
├── _ext/             # Custom extensions (dsm_lexer, pyi_signatures)
├── _static/          # CSS and images
├── _templates/       # Autosummary templates
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
- Code examples: prefer Python, verify against real API
- Directives: `{note}`, `{tip}`, `{warning}` for callouts
- After any file move or rename: `make clean && make html` (Sphinx caches old paths)

## Git Workflow

Commit format: `docs(section): Description`

Examples:
- `docs(python): add collections tutorial`
- `docs(tools): complete template model reference`
- `docs(dsm): fix function pool syntax examples`
