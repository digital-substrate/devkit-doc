# dsm_util.py

`dsm_util.py` is the command-line tool for working with DSM definitions. It validates
models, creates databases, and generates Python packages.

## Commands

| Command                  | Description                  |
|--------------------------|------------------------------|
| `check`                  | Validate DSM syntax          |
| `create_commit_database` | Create a versioned database  |
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

Create an empty versioned database with embedded definitions:

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

Generate a complete Python package from DSM definitions:

```bash
python3 tools/dsm_util.py create_python_package model.dsm --repos /path/to/repos
```

### Generated Package Contents

| Module              | Description                             |
|---------------------|-----------------------------------------|
| `model.definitions` | Type definitions for Viper              |
| `model.data`        | Classes for concepts, structures, enums |
| `model.attachments` | Attachment accessors with type hints    |
| `model.database`    | Database API with type hints            |
| `model.value_types` | Type mappings                           |

### Usage

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

| Option       | Description                                |
|--------------|--------------------------------------------|
| `--repos`    | Path to Digital Substrate repositories     |
| `--wheel`    | Generate pyproject.toml for wheel building |
| `--kibo`     | Path to kibo JAR file                      |
| `--template` | Path to template folder                    |

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

# 4. Generate Python package
python3 tools/dsm_util.py create_python_package model.dsm

# 5. Use in Python
python3 -c "import model; print(model)"
```

