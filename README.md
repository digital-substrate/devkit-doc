# DevKit Documentation

Sphinx documentation for the [dsviper](https://pypi.org/project/dsviper/) ecosystem:
DSM language, Python API, Kibo code generator, and developer toolchain.

The generated HTML is published at <https://docs.digitalsubstrate.io/>.

## Prerequisites

```bash
pip install -r requirements.txt
```

This installs Sphinx, the Furo theme, MyST parser, and `dsviper` (required by the
`pyi_signatures` extension to extract API type hints from the installed package).

The Node API reference needs the TypeScript declarations as well:

```bash
npm install
```

### Building against the bindings under development

Both API references are generated from the **installed** binding, not from this
repository: `autosummary` reads the `dsviper` package, and `sphinx-js` runs
TypeDoc over `node_modules/@digitalsubstrate/dsviper`. On a tag build that is
what you want — the published documentation describes the published packages.

While improving documentation it is the opposite of what you want. Docstrings
you have just written live in the binding repositories, and a build against the
last release cannot see them. Point both at the working copies:

```bash
# Python — editable install of the wheel
pip install -e ../com.digitalsubstrate.viper/dsviper_wheel

# Node — the npm equivalent, a symlink into node_modules
(cd ../com.digitalsubstrate.viper/dsviper_node && npm link)
npm link @digitalsubstrate/dsviper
```

Neither touches `requirements.txt`, `package.json` or `package-lock.json`, so
CI still installs the published packages with `pip install -r` and `npm ci`.

You do not have to remember. Every build prints which binding it read:

```
[bindings] Python 1.2.26       from …/com.digitalsubstrate.viper/dsviper_wheel/dsviper
[bindings] Node   1.2.11-dev.0 from …/com.digitalsubstrate.viper/dsviper_node
```

and `make check` refuses to pass when the binding repository is sitting beside
this one and the build is reading something else:

```bash
make bindings-check     # on its own
```

That gate exists because a build against a stale binding is not obviously
wrong — it renders, every link resolves, and the pages look finished while
describing the previous release. It happened twice in one session, once per
binding, and nothing warned either time.

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

## Quality gates

```bash
make doctest    # run all `{doctest}` examples against the live dsviper runtime
make linkcheck  # validate every external URL
make coverage   # list dsviper symbols not referenced by autodoc/autosummary
make check      # run the three above; exits non-zero on first failure
```

`make.bat` exposes the same targets on Windows.

## Distribution artifacts

```bash
make distzip        # build/dist/devkit-<version>-doc.zip — multi-page HTML archive
make pdf            # build/dist/devkit-<version>-doc.pdf — ~400-page PDF (xelatex)
make notebooklmzip  # build/dist/devkit-<version>-notebooklm.zip — Markdown bundles for LLMs / agents
```

`DOC_VERSION` defaults to `1.2`; override from the environment if needed.

### PDF prerequisites

The `pdf` target uses `xelatex`. Install a TeX distribution:

| Platform | Recommended                                                     |
|----------|-----------------------------------------------------------------|
| macOS    | BasicTeX + `tex-gyre` + `gnu-freefont` (Homebrew)               |
| Linux    | TeX Live (`texlive-xetex`, `texlive-fonts-extra`)               |
| Windows  | [MiKTeX](https://miktex.org/) — auto-installs missing packages on first run, or TeX Live for Windows |

## Structure

```
devkit-doc/
├── source/
│   ├── conf.py                 # Sphinx configuration
│   ├── index.rst               # Main page and top-level toctree
│   ├── _ext/                   # Custom extensions (dsm_lexer, pyi_signatures)
│   ├── _static/                # CSS and images
│   ├── _templates/             # Autosummary templates
│   ├── _fixtures/              # Doctest fixtures (Tuto/model.dsm)
│   ├── ecosystem/              # Cross-cutting ecosystem narrative
│   ├── dsm/                    # DSM language reference
│   ├── kibo/                   # Kibo code generator
│   ├── kibo-template-viper/    # Kibo first-party templates
│   ├── dsviper/                # dsviper Python API
│   ├── dsviper-tools/          # Database / CommitDatabase tooling
│   ├── dsviper-components/     # Qt Widgets / QML component library
│   ├── commit-apps/            # cdbe, dsviper-ge, dsviper-ge-qml, dsviper-web-cdbe
│   └── legal/                  # License and legal content
├── tools/
│   └── build_notebooklm.py     # Bundles Sphinx output into NotebookLM .md
├── Makefile                    # macOS/Linux
├── make.bat                    # Windows
└── requirements.txt            # Python dependencies
```

## Custom Extensions

### dsm_lexer

Pygments lexer for DSM syntax highlighting in code blocks.

### pyi_signatures

Extracts type hints from the installed `dsviper` package (`.pyi` stub file) and
injects them into autodoc-generated API documentation. Supports inheritance lookup.

## License

Dual-licensed: **CC-BY 4.0** for prose, **MIT** for code samples and Sphinx machinery. See [LICENSE](LICENSE).
