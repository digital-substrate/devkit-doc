# Python Wheels

This chapter covers creating distributable Python wheels from your DSM model.

## What is a Wheel?

A wheel is Python's standard distribution format. It packages your generated
code for easy installation via pip.

## Quick Start

### Step 1: Generate with Wheel Option

```bash
python3 tools/dsm_util.py create_python_package --wheel model.dsm
```

This creates:
- Generated Python package in `model/`
- Template `pyproject.toml`

### Step 2: Edit pyproject.toml

Customize the generated `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "model"
version = "1.0.0"
description = "Python wrapper for model"
authors = [
    {name = "Your Name", email = "you@example.com"}
]
maintainers = [
    {name = "Your Name", email = "you@example.com"}
]
readme = "README.rst"
requires-python = ">=3.14"
license = {text = "Proprietary"}
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "Topic :: Software Development",
]
keywords = ["model"]

[tool.setuptools.packages.find]
include = ["model"]

[tool.setuptools.package-data]
model = ["*.py", "resources/*.bin"]
```

### Step 3: Build the Wheel

```bash
pip3 wheel .
```

This creates: `model-1.0.0-py3-none-any.whl`

### Step 4: Install

```bash
pip3 install --force-reinstall model-1.0.0-py3-none-any.whl
```

### Step 5: Use

```python
>>> import model
>>> from model.data import Tuto_UserKey, Tuto_Login
>>> key = Tuto_UserKey.create()
```

## Package Structure

After generation, your package looks like:

```
model/
├── __init__.py
├── data.py              # Concept, struct, enum classes
├── commit.py            # Commit API
├── database.py          # Database API
├── definitions.py       # Type definitions
├── value_types.py       # Type mappings
├── path.py              # Field paths
└── resources/
    └── definitions.bin  # Embedded definitions
```

## Dependencies

Your wheel depends on `dsviper`. Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "dsviper>=1.2.0"
]
```

## Distribution

### Local Installation

```bash
pip3 install model-1.0.0-py3-none-any.whl
```

### Private PyPI

Upload to a private PyPI server:

```bash
pip3 install twine
twine upload --repository-url https://your-pypi.example.com model-1.0.0-py3-none-any.whl
```

### Requirements File

Add to `requirements.txt`:

```
dsviper>=1.2.0
./wheels/model-1.0.0-py3-none-any.whl
```

## Version Management

Update version in `pyproject.toml` for each release:

```toml
[project]
version = "1.1.0"  # Bump for new releases
```

Follow semantic versioning:
- **Major** (2.0.0): Breaking changes to DSM model
- **Minor** (1.1.0): New concepts, structures, or attachments
- **Patch** (1.0.1): Bug fixes, documentation

## What's Next

- [Templates](templates.md) - Understanding templated features
