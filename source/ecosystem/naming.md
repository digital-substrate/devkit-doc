# DevKit, dsviper, Viper — what's what

Three names appear across the documentation and they refer to different
things. This page is the canonical disambiguation; other sections should link
here rather than re-explain.

## DevKit

*What you download.*

The Digital Substrate Python toolkit, distributed as a single ZIP. It bundles:

- `dsviper` — the Python runtime
- `kibo` — the code generator
- `kibo-template-viper` — the template that targets the viper runtime
- `dsviper-tools` — CLI utilities (`dsm_util`) and GUI editors (`cdbe.py`,
  `dbe.py`, `commit_database_server.py`, `commit_admin.py`)
- offline documentation

Versioning tracks ecosystem releases (e.g. `1.2.x`). Distribution and
download from the website (digitalsubstrate.io).

## dsviper

*What runs in your Python apps.*

The Python runtime — a strongly typed Python API over the Viper C++ engine. It
carries the type system, value system, commit DAG, database tier,
serialization, and RPC, and exposes them as Python classes and functions.

Distribution:

- **PyPI** — `pip install dsviper`. Fine if you only need the runtime.
- **DevKit ZIP** — bundled, alongside the toolchain. Use this if you also
  want kibo, the editors, or offline docs.

Both paths give you the same dsviper.

## Viper

*The C++ engine behind dsviper.*

The metadata-driven C++ runtime that dsviper wraps. Carries the actual
implementation of the type system, commit DAG, and database engine.

Currently **not** distributed standalone — used internally and through
dsviper. If a C++-side or alternate-language public binding ships in the
future, it would consume Viper directly.

## How they layer

In practice:

- You write Python code that imports `dsviper`.
- `dsviper` calls into Viper under the hood (C++ through Python bindings).
- You install one or both via **DevKit** (the bundle) or **PyPI** (for
  `dsviper` alone).

Most developers only deal with **dsviper** in code and **DevKit** as a
download path. Viper is the layer below — usually not touched directly today.

## Other names you'll meet

These three are the *distribution* names. The ecosystem also has component
names and domain vocabulary:

- **DSM**, **Kibo**, **kibo-template-viper**, **dsviper-tools**,
  **dsviper-components** — components in their own right. See
  [value-chains](value-chains.md).
- **attachment**, **commit DAG**, **function pool**, **blob**, … — domain
  terms. See the [glossary](glossary.md).
