# DevKit Documentation

Sphinx documentation for the [dsviper](https://pypi.org/project/dsviper/) ecosystem:
DSM language, Python API, Kibo code generator, and developer toolchain.

The generated HTML is served on the DevKit website.

## Prerequisites

```bash
pip install -r requirements.txt
```

This installs Sphinx, the Furo theme, MyST parser, and `dsviper` (required by the
`pyi_signatures` extension to extract API type hints from the installed package).

## Build

```bash
make html          # macOS/Linux
make.bat html      # Windows
```

Output: `build/html/index.html`

## Development

```bash
# Clean rebuild
make clean && make html

# Live preview with auto-rebuild
pip install sphinx-autobuild
sphinx-autobuild source build/html
```

## Structure

```
devkit-doc/
├── source/
│   ├── conf.py           # Sphinx configuration
│   ├── index.rst         # Main page
│   ├── _ext/             # Custom extensions (DSM lexer, .pyi signatures)
│   ├── _static/          # CSS overrides
│   ├── _templates/       # Autosummary templates
│   ├── concepts/         # Viper architecture and design
│   ├── dsm/              # DSM language reference
│   ├── python/           # Python guide + API reference
│   └── tools/            # Toolchain (Kibo, dsm_util, IDE, templates)
├── Makefile              # macOS/Linux
├── make.bat              # Windows
└── requirements.txt      # Python dependencies
```

## Custom Extensions

### dsm_lexer

Pygments lexer for DSM syntax highlighting in code blocks.

### pyi_signatures

Extracts type hints from the installed `dsviper` package (`.pyi` stub file) and
injects them into autodoc-generated API documentation. Supports inheritance lookup.
