# Python Wheels

Creating distributable Python wheels from your DSM model.

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
requires-python = ">=3.14"
dependencies = ["dsviper>=1.2.0"]

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
├── __init__.py                          # Re-exports data
├── data.py                              # Concept, struct, enum, key classes
├── attachments.py                       # Attachment getters/setters (incl. collaborative variants)
├── database_attachments.py              # Database-side attachment getters/setters
├── function_pools.py                    # Function pool API
├── attachment_function_pools.py         # Function pools tied to attachments
├── function_pool_remotes.py             # Remote function pools
├── attachment_function_pool_remotes.py  # Remote function pools (attachment-bound)
├── definitions.py                       # DSM type definitions
├── value_type.py                        # Type bindings
├── path.py                              # Field paths
└── resources.py                         # Embedded definitions (base64 blob)
```

## Distribution

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

Bump the `version` field in `pyproject.toml` for each release; follow semver
against your DSM model surface.
