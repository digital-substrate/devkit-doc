# Naming

Three names appear across the documentation and they refer to different
things.

## DevKit

*What you download.*

The Digital Substrate Python toolkit, distributed as a single ZIP. It bundles:

- `kibo` — the code generator
- `kibo-template-viper` — the template pack that targets the viper runtime
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

## Viper C++

*The C++ engine behind dsviper.*

Distributed under commercial license.
[Contact us](https://devkit.digitalsubstrate.io/contact/) for access to
the C++ runtime.

**Documentation scope.** This site describes the architecture and uses
C++ snippets to illustrate the engine layer where relevant. A complete
C++ API reference — headers, integration patterns — is delivered alongside 
the runtime under commercial license, not mirrored here.
