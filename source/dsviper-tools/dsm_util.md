# dsm_util.py

`dsm_util.py` is the command-line tool for working with DSM definitions. It validates
models, creates databases, and generates Python packages.

```{note}
`dsm_util.py`'s package generation is kibo 1's: it renders the kibo-template-viper **1.2**
pack with kibo 1.2 — in the DevKit, from its `kibo-1/` folder — so the package it produces
has the **kibo 1 surface** (`model.data`, `model.attachments`, names prefixed by their
namespace such as `Tuto_Login`), described in the {doc}`Kibo 1 section <../kibo-1/index>`.
To generate with kibo 2, write a `kibo.toml` and run
{doc}`kibo-project <../kibo/kibo-project>` (`tools/kibo_project.py` in the DevKit); the
result is described in {doc}`../using-generated-sdk/index`. The other commands — `check`, `encode`, `decode`,
`create_database`, `create_commit_database` — work on DSM definitions and databases only,
and do not depend on a generated package.
```

## Commands

| Command                  | Description                  |
|--------------------------|------------------------------|
| `check`                  | Validate DSM syntax          |
| `create_commit_database` | Create a commit database     |
| `create_database`        | Create a simple database     |
| `create_python_package`  | Generate Python package      |
| `encode`                 | Convert DSM to binary format |
| `decode`                 | Convert binary to DSM format |

## Check Syntax

Validate DSM definitions and report errors:

```bash
# Check a single file
python3 tools/dsm_util.py check model.dsm

# Check a folder of DSM files
python3 tools/dsm_util.py check definitions/
```

### Error Format

Errors are reported in the standard format `<file>:<line>:<column>:<message>`:

```
model.dsm:10:5: The type 'strin' is unknown.
model.dsm:14:12: The type K='user' in attachment<K, D> 'identity' must be a concept.
```

This format integrates with most IDEs for click-to-navigate.

## Create Commit Database

Create an empty commit database with embedded definitions:

```bash
python3 tools/dsm_util.py create_commit_database model.dsm model.cdb
```

A CommitDatabase:

- Stores all mutations as commits
- Maintains full history (DAG)
- Embeds definitions for self-contained distribution

## Create Database

Create a simple (non-versioned) database:

```bash
python3 tools/dsm_util.py create_database model.dsm model.db
```

Use this for simpler applications that don't need history.

## Create Python Package

Generate a complete Python package from DSM definitions, with the 1.2 pack:

```bash
python3 tools/dsm_util.py create_python_package model.dsm
```

It runs kibo with the 1.2 pack's `python/package` templates (and, with `--wheel`, its
`python/wheel/pyproject.toml.stg`). The 2.0 pack has no such layout: for the 2.0 surface,
use {doc}`kibo-project <../kibo/kibo-project>`.

### Generated Package Contents (1.2 surface)

| Module              | Description                                                    |
|---------------------|---------------------------------------------------------------|
| `model.data`        | Proxy classes for concepts, clubs, enums, structs, containers |
| `model.attachments` | Attachment accessors (get / set / enumerate), type-hinted     |
| `model.definitions` | Runtime type catalog (`definitions()`) and `RuntimeIds`       |
| `model.value_type`  | Viper `Type` handles used by `data` / `attachments`           |
| `model.path`        | Field-path constants for fine-grained attachment setters      |
| `model.resources`   | Packed definitions blob decoded by `model.definitions`        |

A model that declares function pools also emits `model.function_pools`
(and the RPC / attachment-pool variants).

### Usage (1.2 surface)

```pycon
>>> import model.attachments as ma
>>> import model.data as md

# Use generated classes
>>> key = md.Tuto_UserKey.create()
>>> login = md.Tuto_Login()
>>> login.nickname = "alice"

# Use generated accessors
>>> ma.tuto_user_login_set(attachment_mutating, key, login)
```

### Options

| Option        | Description                                |
|---------------|--------------------------------------------|
| `--wheel`     | Generate pyproject.toml for wheel building |
| `--kibo`      | Path to kibo JAR file                      |
| `--templates` | Path to the folder of Python templates     |

## Encode to JSON

Convert DSM definitions to JSON (`.dsm.json`):

```bash
python3 tools/dsm_util.py encode model.dsm model.dsm.json
```

The JSON format is the canonical input consumed by the Kibo code generator
(`-d <file>.dsm.json`). It is human-inspectable, diff-friendly, and
platform-independent.

## Decode from JSON

Rewrite JSON definitions back to the DSM language:

```bash
python3 tools/dsm_util.py decode model.dsm.json decoded_model.dsm
```

## Workflow Example

```bash
# 1. Write your DSM model
vim model.dsm

# 2. Check syntax
python3 tools/dsm_util.py check model.dsm

# 3. Create database
python3 tools/dsm_util.py create_commit_database model.dsm model.cdb

# 4. Generate a Python package (the 1.2 surface; for 2.0, use kibo-project)
python3 tools/dsm_util.py create_python_package model.dsm

# 5. Use in Python
python3 -c "import model; print(model)"
```

