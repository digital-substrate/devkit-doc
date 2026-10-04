# Python Wheels

Making the generated Python package installable — a wheel that `pip` installs, and that a
type checker reads.

## The `Wheel` feature

The Python `Base` feature renders a package: a directory of modules that an application can
place on its path. The `Wheel` feature adds the two files that make it a distribution:

- `pyproject.toml`, at the project root — the target's output, one level above the package;
- `py.typed`, inside the package — the marker without which a type checker treats the package
  as untyped (`Stub file not found`) and every annotation in it is invisible.

Both are rendered by [kibo-project](../kibo/kibo-project.md) from the project's `kibo.toml`:

```toml
[project]
definitions = "definitions"
infrastructure = "features"

[generator]
templates = "2"

[target.python]
features = ["Base", "Wheel"]
output = "python"
```

```bash
python3 kibo_project.py generate kibo.toml
```

`infrastructure` names the package (`features` here, in kibo's snake_case); add `"Pool"` to
the features when the model declares function pools.

## The generated `pyproject.toml`

```toml
# Generated from features.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.0 (MIT), Template Model 2.
# Runtime: this file declares a dependency on `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "features"
version = "1.0.0"
description = "Generated Python bindings for the features model"
requires-python = ">=3.10"
license = { text = "Proprietary" }
dependencies = ["dsviper >= 1.2.29, < 1.3"]

[tool.setuptools.packages.find]
include = ["features", "features.*"]

[tool.setuptools.package-data]
"features" = ["py.typed", "*.pyi"]
```

It keeps what a build needs — the name, the version, the packages (the units are subpackages,
hence `features.*`), `py.typed` as package data, and the `dsviper` range the pack declares.
Authors, maintainers, a readme, classifiers and keywords are the packager's to add.

## Build

From the target's output, the directory holding `pyproject.toml`:

```bash
pip wheel . --no-deps -w dist
```

or, with the [build](https://pypi.org/project/build/) front-end, which also makes an sdist:

```bash
python -m build
```

Either gives `features-1.0.0-py3-none-any.whl`: a pure-Python wheel, the same on every
platform. `--no-deps` keeps `pip wheel` from also downloading `dsviper` into `dist/`.

## Install

```bash
pip install features-1.0.0-py3-none-any.whl
```

`pip` resolves `dsviper` from the range the wheel declares. An environment that already holds
the runtime can install the wheel alone, with `--no-deps`.

## Use

A namespace is a module of the package, and a type is reached through it:

```python
import dsviper
import features
from features import demo, containers

s = demo.StructureS(f_float=1.5, f_string="hello")
v = containers.Vector_of_uint8([1, 2, 3])
key = demo.ConceptAKey.create()

db = dsviper.Database.create_in_memory()
db.extend_definitions(features.definitions())
db.begin_transaction()
demo.attachments.ConceptA.properties.set(db, key, demo.StructureV(f_string="stored"))
db.commit()
demo.attachments.ConceptA.properties.get(db, key).unwrap().f_string   # 'stored'
```

`features.definitions()` is the model, decoded once from the embedded definitions. A
generated object is a box around a Viper value: `s.unwrap_value()` gives it,
`demo.StructureS.wrap_value(value)` boxes one, without copying. The package's own docstring
(`help(features)`) says where to start; the
[Python page of the generated SDK](../using-generated-sdk/python.md) covers the API.

Because the wheel carries `py.typed`, a type checker sees the annotations from the installed
package:

```python
from features import demo

s = demo.StructureS(f_float=1.5, f_string="hello")
s.f_float = "not a float"
```

```
$ mypy use.py
use.py:4: error: Incompatible types in assignment (expression has type "str", variable has type "float")  [assignment]
```

## Package structure

A model named `features` with one namespace `Demo` and one function pool `Tools`, rendered
with `Base`, `Pool` and `Wheel`:

```
python/
├── pyproject.toml            # Wheel: at the project root
└── features/                 # the package, named by the project's infrastructure
    ├── __init__.py           # definitions(), AnyConceptKey, AnyValue, AttachmentProxy, Key, the units
    ├── containers.py         # one class per container shape the model uses: Vector_of_uint8, …
    ├── resources.py          # the embedded definitions (base64 of the zlib-compressed bytes)
    ├── py.typed              # Wheel: the package is typed
    ├── demo/                 # one subpackage per DSM namespace: Demo is demo
    │   ├── __init__.py       # re-exports data, imports attachments
    │   ├── data.py           # structures, enumerations, keys, and the runtime ids
    │   └── attachments.py    # one class per concept, one accessor per attachment
    ├── tools/                # Pool: one subpackage per function pool
    │   ├── __init__.py
    │   └── pool.py           # Pool (local) and Remote (through a service)
    └── _codegen/             # the runtime every generated package carries
        ├── __init__.py
        ├── proxy.py
        ├── container.py
        └── attachment.py
```

A pool is imported by its path, `import features.tools`: the entry module belongs to `Base` and
cannot import what only the `Pool` feature renders. `_codegen/` and `resources.py` are written
by kibo-project, as the pack's layout declares — the runtime copied from the pack, the
definitions encoded beside the modules.

## Distribution

A wheel goes wherever wheels go: a private package index, an artifact store, or a path in an
application's `requirements.txt`. It holds no binary, so one wheel serves every platform and
every Python from 3.10; the runtime it needs, `dsviper`, is a separate distribution that the
installer resolves from the declared range.

## Version management

Two numbers meet in `pyproject.toml`, and they are not the same thing:

- **The package's own version**, `version = "1.0.0"` as rendered. It is the version of your
  model's surface: bump it for each release, following semver against what the model
  declares. The file is regenerated with the project, so set the version where the release
  is made — after generation, or in the step that publishes the wheel.
- **The runtime range**, `dsviper >= 1.2.29, < 1.3`. It is the pack's, not yours: the floor is
  what the generated code uses, the ceiling the runtime's compatibility contract (the 1.2
  minor). A later pack may raise the floor; the header of every generated module names the
  same range.
