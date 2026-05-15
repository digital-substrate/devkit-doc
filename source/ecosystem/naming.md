# Naming

Three names appear across the documentation and they refer to different
things.

## DevKit

*What you download.*

The Digital Substrate Python toolkit, distributed as a single ZIP. It bundles:

- `kibo` — the code generator
- `kibo-template-viper` — the template that targets the viper runtime
- `dsviper-tools` — CLI utilities (`dsm_util`, `commit_database_server.py`,
   `commit_admin.py`) and two GUI editors: `cdbe.py` (Commit Database
   Editor, for `CommitDatabase`) and `dbe.py` (Database Editor, plain
   CRUD for the non-versioned `Database` backend)

The `dsviper` runtime is **not** bundled in the DevKit ZIP — it is installed
separately from PyPI (see below).

Versioning tracks ecosystem releases (e.g. `1.2.x`). Distribution and
download from the website (digitalsubstrate.io).

## dsviper

*What runs in your Python apps.*

The Python runtime — a strongly typed Python API over the Viper C++ engine. It
carries the type system, value system, commit DAG, database tier,
serialization, and RPC, and exposes them as Python classes and functions.

**Distribution.** dsviper is published exclusively on
`PyPI <https://pypi.org/project/dsviper/>`_ (``pip install dsviper``). It is
*not* bundled in the DevKit ZIP — the ZIP carries the toolchain (Kibo,
kibo-template-viper, dsviper-tools); installing dsviper itself
is a separate ``pip`` step.

## Viper

*The C++ engine behind dsviper.*

The metadata-driven C++ runtime that dsviper wraps. Carries the actual
implementation of the type system, commit DAG, and database engine.

Distributed under commercial license; NDA required before access.
[Contact Digital Substrate](https://devkit.digitalsubstrate.io/contact/)
to start the process. The Python wrapper `dsviper` carries the runtime
transparently for Python users (no NDA needed).

## How they layer

You write Python that imports `dsviper`; `dsviper` calls into Viper (C++)
through Python bindings. Install `dsviper` from PyPI; the DevKit ZIP gives
you the toolchain around it (Kibo, kibo-template-viper, dsviper-tools).

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
