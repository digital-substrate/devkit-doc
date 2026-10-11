# Migrating a project

A kibo 1.2 project generates with a script: a `generate.py` of its own, or `dsm_util.py
create_python_package` / `create_node_package`. A kibo 2 project states its generation in a
`kibo.toml`, and [kibo-project](../kibo/kibo-project.md) runs it. This page turns the first into
the second.

The generated code changes too: code written against it moves as
[Migrating application code](application.md) says. A project that renders templates of its own
moves them as [Migrating a template pack](template-pack.md) says.

## Before you start

- Python 3.11 or later with `dsviper` (on Python 3.10, also `tomli`), and Java 17.
- `kibo_project.py`, the kibo 2 jar and the kibo-template-viper 2 pack. In the DevKit they are
  `tools/kibo_project.py`, `kibo-2/tools/kibo-2.*.jar` and `kibo-2/templates/`, where
  kibo-project finds them on its own. Elsewhere, set `KIBO_JAR` and `KIBO_TEMPLATES`
  ([Where the generator comes from](../kibo/kibo-project.md#where-the-generator-comes-from)).
- If the project has templates of its own, render their *before* now, while the kibo 1.2 jar,
  pack and `.dsm.json` are still in place ([the method](template-pack.md#the-method-a-diff-you-can-account-for)).
  Until those templates are migrated, a target that renders them fails its validation: leave
  their features out of the target's `features` at first, and add them once migrated.
- Then delete, or move aside, everything kibo 1.2 generated. A 1.2 module left in place still
  imports and hides a call not yet migrated.

## What the script did, and where it goes

A kibo 1.2 script does the same few things, whatever its length. Each has a line in
`kibo.toml`, or disappears.

| The script | In kibo 2 |
|---|---|
| `DSMBuilder.assemble(<path>)`, then `parse()` and a report check | `[project] definitions = "<path>"`: a `.dsm` file, a directory of them, or a list of either. Errors stop the generation. |
| writes `<name>.dsm.json` | Nothing: kibo-project writes it beside `kibo.toml`, named after `[project] infrastructure` whatever the targets set. Ignore it in version control. |
| `-n <name>` | `[project] infrastructure = "<name>"`. A target whose name differed (`Features` for C++, `features` for Python) sets its own `infrastructure`. |
| finds the jar and checks the pack's line | `[generator] templates = "2"`. `KIBO_JAR` and `KIBO_TEMPLATES` still override where they are found. |
| a list of template directories, one `java -jar` call each | `features = [...]` on a target: see [the table](#from-templates-to-features) below. |
| `-c cpp` / `-c python` | the target's name, `[target.cpp]`, `[target.python]`, `[target.typescript]`, or `language = "..."`. TypeScript was rendered with `-c python`; it is now its own target. |
| `-o <dir>` | `output = "<dir>"`, with the changes below. |
| writes `*_Resources.hpp`, `resources.py` or `resources.ts` | Nothing: the pack writes the embedded definitions, in the encoding it declares. Delete that code. |
| a second call for `wheel/pyproject.toml.stg` or `typescript/project` | the `Wheel` (Python) or `Package` (TypeScript) feature. The `pyproject.toml` it writes keeps the name, the version, the packages and the `dsviper` dependency; authors, maintainers, a readme, classifiers and keywords are the packager's to add. |
| `--cpp`, `--python`, `--typescript` flags | `kibo_project.py generate --target <name>`; with no `--target`, every target. |

Where each output lands changed:

| Target | kibo 1.2 `-o` | kibo 2 `output` |
|---|---|---|
| C++ | a directory of `<Name>_<Template>.hpp/.cpp` | a directory, flat: `<infrastructure>_<unit>_<template>.hpp/.cpp`, one set per DSM namespace, and `<infrastructure>_resources.hpp` |
| Python | the package directory itself (`python/features`) | the directory **above** the package: the package is `<output>/<infrastructure>/`, `pyproject.toml` (feature `Wheel`) lands at `<output>` |
| TypeScript | two calls: sources to `<root>/src`, `package.json` to `<root>` | the package root, once: sources go to `<output>/src`, `package.json` and `tsconfig.json` (feature `Package`) to `<output>` |

Setting a Python target's `output` to the old package directory nests the package one level
too deep (`python/features/features/`). The package directory is the `infrastructure` exactly as
written, not snake-cased: when the 1.2 package directory was not the `-n` name (`-n MetaProject`
into `.../metaproject`), set the target's `infrastructure` to the directory's name, the name the
package is imported by.

## From templates to features

kibo 1.2 rendered template directories; kibo 2 selects **features**, and a feature brings
the features it requires (`Attachments` brings `Paths`, which brings `Fields`). Some 1.2
directories merged, others are gone because the runtime now covers them.

| kibo 1.2 template directory | kibo 2 feature |
|---|---|
| C++ `Model`, `Data`, `ValueType` | `Base` (the field names and paths of `Model` are `Fields` and `Paths`) |
| C++ `Attachments` | `Attachments` |
| C++ `FunctionPool`, `AttachmentFunctionPool` | `Pool` (renders nothing for a model that declares no pool) |
| C++ `FunctionPoolRemote`, `AttachmentFunctionPoolRemote` | `PoolRemote` |
| C++ `Stream`, `ValueCodec` | none: the runtime's static layer, through the codec `Base` generates |
| C++ `Json`, `ValueHasher` | none: JSON, XML and a hexdigest are one runtime call on what `codec::encode` returns |
| C++ `Database` | none: `Viper::Database`; the attachments take a database as well as a state |
| C++ `AttachmentFunctionPool_Attachments` | none: the generated attachments, or `Definitions.inject()` with an `AttachmentMutating` |
| C++ `Python` | none: `Definitions.inject()` computes the same constants at run time |
| C++ `Test`, `TestApp` | none: they tested the generator. A project that rendered them keeps them as its own templates (below) |
| Python `package` | `Base` and `Attachments`; `Pool` if the model declares pools |
| Python `wheel/pyproject.toml.stg` | `Wheel` |
| TypeScript `typescript` | `Base` and `Attachments`; `Pool` if the model declares pools |
| TypeScript `typescript/project` | `Package` |

The 1.2 Python and TypeScript packages held the attachments and pools of every model; in
kibo 2 they are features, so a project that used them names them. The full list of features
and what each generates is in
[kibo-template-viper features](../kibo-template-viper/features.md).

## Templates of your own

A template the pack does not ship — a project's test programme, a report, a binding of its
own — is declared in a manifest of the project, in the pack's format. Its templates sit beside
it, in a directory per target:

```text
templates/
├── features.json
└── cpp/
    ├── test.hpp.stg
    ├── test.cpp.stg
    └── test_app.cpp.stg
```

```json
{
  "cpp": {
    "Test": {
      "doc": "What it takes to put a unit to the test.",
      "templates": ["test.cpp.stg", "test.hpp.stg"],
      "requires": ["Base", "Attachments"]
    },
    "TestApp": {
      "doc": "The programme that runs the test over the whole model.",
      "templates": ["test_app.cpp.stg"],
      "requires": ["Test", "Pool"]
    }
  }
}
```

`kibo.toml` names the manifest in `[generator] manifests`, and a target selects its features
as it selects the pack's. A feature name the pack already declares is refused. `requires` names
the features the template's output needs beside it, the pack's as well as the manifest's;
kibo-project renders them too.

A template of your own renders where the pack's do: for C++ into `output`, for Python into the
package, `<output>/<infrastructure>/`, for TypeScript into `<output>/src`. A module it adds to a
Python or TypeScript package takes a name a DSM namespace or pool could also take; reserve it,
so that such a namespace stops the generation instead of overwriting the module:

```json
{
  "python": {
    "Report": {
      "doc": "A report of the model's types, as a module of the package.",
      "templates": ["report.py.stg"],
      "requires": ["Base"]
    }
  },
  "reserved": {
    "python": {"namespace": ["report"], "pool": ["report"]}
  }
}
```

A template written for kibo 1.2 reads Template Model 1: it renders, under kibo 2, only once
migrated ([Migrating a template pack](template-pack.md)). kibo 2 also renders a template once
per scope it declares — `main(m)` keeps rendering it once for the whole model, as in 1.2.

A template that rendered to another directory than the rest (`TestApp` into `.`) is a target
of its own, with `with_requirements = false`: it renders only the features it names, and
another target of the same language and infrastructure renders what they require.

```toml
[target.app]
language = "cpp"
features = ["TestApp"]
with_requirements = false
output = "."
```

## A complete example

A kibo 1.2 `generate.py` (shortened):

```python
NAMESPACE = 'Features'
DSM_SOURCE = arguments.definitions        # all.dsm

# C++, into Features/
for template in ['Model', 'Data', 'Stream', 'Json', 'Database',
                 'Attachments', 'AttachmentFunctionPool_Attachments',
                 'ValueType', 'ValueCodec', 'ValueHasher', 'Test']:
    generate(namespace=NAMESPACE, template=template, output='Features')
generate_resource(definitions=DEFINITIONS, output='Features/Features_Resources.hpp')
generate(namespace=NAMESPACE, template='TestApp', output='.')

# Python, into python/features, then resources.py
generate_package(name='features', output='python/features')

# TypeScript: -t typescript into typescript/features/src, -t typescript/project into
# typescript/features, then resources.ts
generate_typescript(name='features', package_root='typescript/features')
```

The same project in kibo 2, with `Test` and `TestApp` moved to the project's
`templates/features.json` and migrated to Template Model 2:

```toml
[project]
definitions = "all.dsm"
infrastructure = "features"

[generator]
templates = "2"
manifests = ["templates/features.json"]

[target.cpp]
infrastructure = "Features"
features = ["Base", "Attachments", "Pool", "Test"]
output = "Features"

[target.app]
language = "cpp"
infrastructure = "Features"
features = ["TestApp"]
with_requirements = false
output = "."

[target.python]
features = ["Base", "Attachments", "Pool", "Wheel"]
output = "python"

[target.typescript]
features = ["Base", "Attachments", "Pool", "Package"]
output = "typescript/features"
```

`Stream`, `Json`, `Database`, `ValueCodec`, `ValueHasher` and
`AttachmentFunctionPool_Attachments` have no line: the runtime covers them. `[target.cpp]`
renders `Pool` and `Test`, which `TestApp` requires: a target with `with_requirements = false`
is refused unless another target of the same language and infrastructure renders them.

For `dsm_util.py create_python_package model.dsm --wheel`, run in a directory: the package was
`./model/`, `pyproject.toml` at `.`:

```toml
[project]
definitions = "model.dsm"
infrastructure = "model"

[generator]
templates = "2"

[target.python]
features = ["Base", "Attachments", "Wheel"]
output = "."
```

For `dsm_util.py create_node_package model.dsm`: the package root was `./model/`:

```toml
[target.typescript]
features = ["Base", "Attachments", "Package"]
output = "model"
```

## Check the result

1. `python3 kibo_project.py plan kibo.toml` — the jar and the pack it found, and per target
   its output directory, the features and every template, marked `sources` or `root`.
   Nothing is written. Check each output directory and feature list against what the
   project's build expects.
2. `python3 kibo_project.py generate kibo.toml` — generates every target, then validates the
   Python (imported, every structure built, `mypy --strict`) and the TypeScript (`tsc`).
3. Build the project. The C++ file names and namespaces changed, and so did the Python and
   TypeScript modules: the compiler and the type checkers list what the code still names the
   1.2 way, which [Migrating application code](application.md) moves.
4. `python3 kibo_project.py check kibo.toml` — once the project builds, exits 0 when the
   generated files in place are those `kibo.toml` generates. Run it in the project's checks.
