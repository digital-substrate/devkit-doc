# Naming

A handful of names appear across the documentation and refer to different
things. The relationship at the centre: one C++ engine — **Viper C++** —
exposed to application code through two language **bindings** over the same
runtime and the same on-disk format: **dsviper** for Python and
**`@digitalsubstrate/dsviper`** for Node.js. The **DevKit** is what you
download.

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

The **Python** binding — a strongly typed Python API over the Viper C++ engine.
It carries the type system, value system, mutation DAG, database tier,
serialization, and RPC, and exposes them as Python classes and functions.

**Distribution.** dsviper is published exclusively on
`PyPI <https://pypi.org/project/dsviper/>`_ (``pip install dsviper``). It is
*not* bundled in the DevKit ZIP — the ZIP carries the toolchain (Kibo,
kibo-template-viper, dsviper-tools); installing dsviper itself
is a separate ``pip`` step.

dsviper is the **Python** binding; a Node.js binding over the same engine is
published separately as `@digitalsubstrate/dsviper` (below).

## @digitalsubstrate/dsviper

*What runs in your Node.js apps.*

The **Node.js** binding — a native addon over the same Viper C++ engine as the
Python `dsviper`, exposing the same runtime and the same on-disk format. It
covers the dynamic API (runtime type and value systems, definitions, commit
tier) with Java-like value semantics (`equals` / `hash` / `compare`, no
operator overloading). See {doc}`../dsviper-node/index`.

**Distribution.** Published on npm as `@digitalsubstrate/dsviper`
(`npm install @digitalsubstrate/dsviper`), shipped as prebuilt native binaries.
Note that the two bindings differ by registry: the Python package is the bare
`dsviper` on PyPI, the Node package is scoped `@digitalsubstrate/dsviper` on
npm. They share the runtime, not the package name. Like the Python `dsviper`,
it is not bundled in the DevKit ZIP, and it is covered by the same commercial
license as the engine.

## Viper C++

*The C++ engine behind dsviper.*

Distributed under commercial license.
[Contact us](https://devkit.digitalsubstrate.io/contact/) for access to
the C++ runtime.

**Documentation scope.** This site describes the architecture and uses
C++ snippets to illustrate the engine layer where relevant. A complete
C++ API reference — headers, integration patterns — is delivered alongside 
the runtime under commercial license, not mirrored here.
