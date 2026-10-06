# Templated Features

A project does not pick templates; it picks **features**. The pack's `features.json` is the
map between the two: per target, each feature names the templates it renders and the
features it requires. Templates stay flat in one directory per target (`cpp/`, `python/`,
`typescript/`), and the selection is expressed one level up.

A project names its features in its `kibo.toml`, and
[kibo-project](../kibo/kibo-project.md) does the rest: it resolves the closure, renders each
template, writes the embedded definitions and copies the runtime, as `features.json`
declares. Calling the jar by hand is covered in [Command-line usage](../kibo/usage.md).

## The catalogue

### C++

The `requires` of the C++ features was measured, not decided: it is the `#include` graph of
the generated C++, interface and build unioned, since asking for a feature means compiling it.

| Feature | What it gives | Requires | Templates |
|---|---|---|---|
| `Base` | The type system and everything that cannot be pulled apart from it. Data, Codec, Model and AnyConcept include one another in both directions; there is no cut. | — | `data`, `codec`, `model`, `any_concept` (`.hpp` and `.cpp` each) |
| `Fields` | The name and the path of every field, as constants: code that handles structures through the dynamic API gets completion instead of a string it can misspell. Selectable alone; `Attachments` builds its typed field setters on it. | — | `fields` |
| `Attachments` | The attachments a unit declares, read and written in memory or in a database. | `Base`, `Fields` | `attachments` |
| `Pool` | A function pool, server side: the functions the application implements, and the pool that registers them. | `Base` | `pool` |
| `PoolRemote` | A function pool, client side: `Remote`, which calls the pool through a service. Selectable without `Pool`, so a client does not link the functions only a server implements. | `Base` | `remote` |

Every C++ file lands in the target's output directory, flat. A file rendered once per DSM
namespace is named `<infrastructure>_<unit>_<template>`, a file rendered once for the model
`<infrastructure>_<template>`, a file rendered once per pool `<infrastructure>_<pool>_<template>`.
For a model named `features` with one namespace `Demo` and one pool `Tools`:

| Feature | Files |
|---|---|
| `Base` | `features_demo_data`, `features_demo_model`, `features_demo_codec`, `features_codec`, `features_any_concept` (`.hpp`, `.cpp`), and `features_resources.hpp` |
| `Fields` | `features_demo_fields` |
| `Attachments` | `features_demo_attachments` |
| `Pool` | `features_tools_pool` |
| `PoolRemote` | `features_tools_remote` |

### Python

| Feature | What it gives | Requires | Templates |
|---|---|---|---|
| `Base` | The package: its entry point, the types each namespace declares, the attachments, and the container bindings the model mentions. | — | `__init__.py`, `data.py`, `attachments.py`, `containers.py` |
| `Pool` | A function pool and its client edge. Most projects have none: a pool is a service surface, not a consequence of having a model. | `Base` | `pool/__init__.py`, `pool.py` |
| `Wheel` | What makes the package installable, and therefore typed. | `Base` | `pyproject.toml`, `py.typed` |

The package is the directory `<output>/<infrastructure>/`. `Base` renders `__init__.py` at
its root (`definitions()`, the units) and in each unit, `<unit>/data.py`,
`<unit>/attachments.py` and `containers.py`; `Pool` renders `<pool>/__init__.py` and
`<pool>/pool.py` (`Pool` and `Remote`). `Wheel` is the one feature whose two files do not land
beside the modules: `py.typed` goes inside the package, `pyproject.toml` one level up, at the
target's output. Without `py.typed` a type checker reports `Stub file not found` and every
annotation of the package is invisible; without `pyproject.toml`, `pip install` refuses the
directory. See [Python Wheels](wheels.md).

### TypeScript

| Feature | What it gives | Requires | Templates |
|---|---|---|---|
| `Base` | The package: its entry point, the types each namespace declares, the attachments, and the container bindings the model mentions. | — | `index.ts`, `definitions.ts`, `data.ts`, `attachments.ts`, `containers.ts` |
| `Pool` | A function pool and its client edge. Most projects have none: a pool is a service surface, not a consequence of having a model. | `Base` | `pool/index.ts`, `pools.ts`, `pool.ts` |
| `Package` | What makes the package buildable and installable: `package.json` and `tsconfig.json`, at the package root, the sources staying in `src/`. | `Base` | `package.json`, `tsconfig.json` |

The sources are the directory `<output>/src/`. `Base` renders `index.ts` at its root and in
each unit, `definitions.ts`, `<unit>/data.ts`, `<unit>/attachments.ts` and `containers.ts`;
`Pool` renders `pools.ts` (every pool, one namespace each) and `<pool>/index.ts`,
`<pool>/pool.ts` (`Remote`). `Package` renders `package.json` and `tsconfig.json` at the
target's output, the package root. See [npm Packages](node.md).

## Resolving a selection

`resolve.py`, beside `features.json`, walks `requires` depth first and returns the closure,
dependencies first, then the templates of that closure, deduplicated, in order. A name the
target does not declare is refused with the list of those it does; a cycle is refused.

```
$ ./resolve.py cpp Attachments
features : Base Fields Attachments
  data.cpp.stg
  data.hpp.stg
  codec.cpp.stg
  codec.hpp.stg
  model.cpp.stg
  model.hpp.stg
  any_concept.cpp.stg
  any_concept.hpp.stg
  fields.cpp.stg
  fields.hpp.stg
  attachments.cpp.stg
  attachments.hpp.stg
```

From Python, `resolve.closure("cpp", ["Attachments"])` gives the feature names and
`resolve.templates("cpp", ["Attachments"])` the template paths. kibo-project does the same
walk, and `kibo_project.py plan` shows it, with where each template lands — `sources` for the
directory the templates render into, `root` for the target's output itself:

```
[python] python -n features -> /…/python
    features: Base, Wheel
    python/__init__.py.stg                   sources
    python/data.py.stg                       sources
    python/attachments.py.stg                sources
    python/containers.py.stg                 sources
    python/pyproject.toml.stg                root
    python/py.typed.stg                      sources
[typescript] typescript -n features -> /…/typescript
    features: Base, Package
    typescript/index.ts.stg                  sources
    typescript/definitions.ts.stg            sources
    typescript/data.ts.stg                   sources
    typescript/attachments.ts.stg            sources
    typescript/containers.ts.stg             sources
    typescript/package.json.stg              root
    typescript/tsconfig.json.stg             root
```

## What sits beside the templates

Besides the features, `features.json` declares what a tool driving kibo needs to know of the
pack, so that the tool carries no knowledge of its own:

- `generator.kibo` — the oldest kibo exposing the Template Model the templates consume,
  `>=2.0.2`. A floor: a later kibo exposing the same Template Model renders them too.
- `layout`, per target — where the templates render, below the target's output (`sources`),
  which templates render at the output itself (`root`), the `runtime` copied beside the
  sources, and the embedded definitions (`resources`) with their encoding.
- `reserved`, per target and per family of names — the names the pack's own code takes: the
  members every generated class inherits from the runtime's proxy, which a field would mask
  (`wrap_value`, `copy`, `type` in Python; `wrapValue`, `equals`, `toJSON` in TypeScript), and
  the modules at the package's root, which a namespace or a pool would replace (`containers`,
  `definitions`, `resources`, `pools`). A DSM name meeting one stops the generation, saying how
  to spell it otherwise for that target — {doc}`../kibo/kibo-project`.
- `validation`, per target — the checks run once a target is written. C++ needs none: its
  compiler refuses invalid code and says why. Python and TypeScript can run code a name has
  broken without a word, so Python is imported, every structure built and the package checked
  with `mypy --strict`; TypeScript is checked with `tsc --noEmit`. A check whose tool is not
  found fails.

| Target | `sources` | `root` | `runtime` | `resources` |
|---|---|---|---|---|
| `cpp` | the output | — | — | `<infrastructure>_resources.hpp`, a byte array `<infrastructure>_resources_definitions` |
| `python` | `<infrastructure>` | `pyproject.toml` | `python/runtime` copied as `_codegen` | `resources.py`, base64 of the zlib-compressed definitions, `B64_DEFINITIONS` |
| `typescript` | `src` | `package.json`, `tsconfig.json` | `typescript/runtime` copied as `_codegen` | `resources.ts`, base64 of the definitions, `B64_DEFINITIONS` |

The runtime and the embedded definitions go **with** a feature: `"with": "Base"` for both, in
every target. They are written beside the templates of the feature that reads them, so a
target that does not render `Base` — the client side of a pool, rendered with
`with_requirements = false` — gets neither.

The runtime belongs to the pack, not to dsviper: the proxy base, the registry that wraps and
unwraps values, the container views (`Sequence`, `Mapping`, `Ordered`, `Optional`,
`Variant`) and the attachment accessor, written once and copied into every generated package
(`_codegen/` in Python: `proxy.py`, `container.py`, `attachment.py`; `src/_codegen/` in
TypeScript: `proxy.ts`, `container.ts`, `attachment.ts`, `registry.ts`, `value.ts`). It
versions with the templates that call it. The embedded definitions are decoded once by the
package's `definitions()`, or by `codec::definitions()` in C++.

## A project's own features

A project can add its features to the pack's selection: a manifest of the same shape as
`features.json`, whose templates sit beside it (`<manifest dir>/<language>/<template>`), and
whose features may require the pack's. A feature name the pack already declares is refused.

```json
{
  "cpp": {
    "Report": {
      "doc": "A report of every structure the model declares.",
      "templates": ["report.md.stg"],
      "requires": ["Fields"]
    }
  }
}
```

`resolve.py` takes it with `--with` (repeatable), and from Python with
`extra=[...]`:

```
$ ./resolve.py cpp Report --with my-templates/features.json
features : Fields Report
  fields.cpp.stg
  fields.hpp.stg
  report.md.stg
```

In a project, kibo-project reads the manifests listed in `[generator] manifests`, paths
relative to the project file:

```toml
[generator]
templates = "2"
manifests = ["my-templates/features.json"]

[target.cpp]
features = ["Report"]
output = "report"
```

A third-party template writes its own header: its licence and the runtime it needs are its
author's to state. The templates such a manifest names read the
[Template Model](../kibo/template_model.md), as the pack's do.

## Picking a feature set

A selection is a target of the project's `kibo.toml`; name the features you want and the
closure follows. This project renders the C++ with attachments and a function pool on both
sides, the Python package as an installable wheel, and the TypeScript package with its
manifest:

```toml
[project]
definitions = "definitions"
infrastructure = "features"

[generator]
templates = "2"

[target.cpp]
features = ["Attachments", "Pool", "PoolRemote"]
output = "cpp/generated"

[target.python]
features = ["Base", "Pool", "Wheel"]
output = "python"

[target.typescript]
features = ["Base", "Pool", "Package"]
output = "typescript"
```

Common selections:

| Use | Target | Features |
|---|---|---|
| Types and the codec only | `cpp` | `Base` |
| Typed data stored in a database | `cpp` | `Attachments` (pulls in `Base` and `Fields`) |
| Field names for code that uses the dynamic API | `cpp` | `Fields` |
| A service: server and client in one binary | `cpp` | `Attachments`, `Pool`, `PoolRemote` |
| A client of a service, in another binary | `cpp` | `PoolRemote`, with `with_requirements = false` beside a target that renders `Base` |
| Python sources inside an application | `python` | `Base` (add `Pool` if the model has pools) |
| An installable Python package | `python` | `Base`, `Wheel` (and `Pool`) |
| A buildable TypeScript package | `typescript` | `Base`, `Package` (and `Pool`) |

Several targets of one language — a server and its client, say — name each target for what it
produces and state its `language`; see [the project file](../kibo/kibo-project.md#the-project-file).

(features-from-1-2)=
## Where the 1.2 features went

The 1.2 pack had one feature per template directory. Kibo 2's pack has fewer, larger
features; some of the 1.2 ones are merged, others are gone because the runtime now covers
them:

| 1.2 feature | In 2.0 |
|---|---|
| `Data`, `Model` | Merged into `Base`: the types and their identity in the definitions cannot be pulled apart from the codec. The field names and paths `Model` carried (1.2's `Field` and `Path`) are the `Fields` feature: `Field::S::f` becomes `fields::S::f`, a `std::string_view`, and `Path::S::f()` becomes `fields::S::fPath()`. |
| `ValueType` | Absorbed into `Base` (the unit's `model` file); in Python and TypeScript, into `containers` and the package entry point, with `definitions()`. |
| `Stream`, `ValueCodec` | Removed: the static layer is the runtime's, and the codec generated in `Base` bridges the C++ types to a `Value` through it. |
| `Json`, `ValueHasher` | Removed: JSON, XML and a hexdigest are one runtime call on what `codec::encode` returns. |
| `Database` | Removed: the runtime's `Viper::Database` has the surface, and the attachments take a database as well as a state. |
| `FunctionPool`, `AttachmentFunctionPool` | `Pool`, which renders every function pool and attachment function pool, server side. |
| `FunctionPoolRemote`, `AttachmentFunctionPoolRemote` | `PoolRemote`, the client side. |
| `AttachmentFunctionPool_Attachments` | Removed. Code written ahead uses the generated attachments (`Graph::selection::unionVertexKeys` in C++, `attachments.Graph.selection.union_vertex_keys` in Python); a session without generation uses the runtime directly, with the constants `Definitions.inject()` gives and an `AttachmentMutating`. |
| `Python` | Removed: `Definitions.inject()` computes the same constants — the model's types, attachments and field paths — from the definitions at run time, into an embedded Python module. |
| `Test`, `TestApp` | Removed from the pack: they test the generator, not an application, and stay with the laboratory, [devkit-codegen-test](https://github.com/digital-substrate/devkit-codegen-test). |
| `package` (the Python package directory) | Python `Base`, with `Pool` for the pools. `database_attachments`, `path`, `value_type` and `definitions` are absorbed into the attachments, the package entry point and `containers`; field paths are not exposed, the typed field operations cover them. 1.2's `wheel/pyproject.toml` is the `Wheel` feature. |
| TypeScript `project/` | The `Package` feature, the counterpart of Python's `Wheel`. |

The surface the features generate changed too — one module per namespace, attachments grouped
by concept, Python names in snake_case; code written against the 1.2 output migrates as the
pack's `CHANGELOG.md` says (2.0.0, *Migrating from 1.2*).
