# Installation

This chapter covers installing and verifying the dsviper Python module.

## Prerequisites

- Python 3.14+
- pip package manager

## Installing from PyPI

The simplest install is directly from PyPI:

```bash
# Create a virtual environment (required since PEP 668)
python3 -m venv ~/venv
source ~/venv/bin/activate  # macOS/Linux
# or
~/venv/Scripts/activate     # Windows

# Install dsviper
pip install dsviper
```

## Installing from the DevKit

If you also want the CLI tools, templates, and offline documentation,
download the DevKit from the [Downloads](https://devkit.digitalsubstrate.io/downloads/) page, unzip, and run:

```bash
cd dsviper-*-devkit
pip install -r requirements.txt
```

The DevKit's `requirements.txt` pulls `dsviper` from PyPI alongside the
GUI/web dependencies needed by the bundled tools.

## Verifying Installation

Verify that dsviper is correctly installed. `version()` returns a
`(major, minor, patch)` tuple:

```{doctest}
>>> import dsviper
>>> v = dsviper.version()
>>> isinstance(v, tuple) and len(v) == 3
True
```

## Understanding dsviper

**dsviper** is the Python extension module that provides access to the Viper runtime. Key
points:

- **dsviper = Viper**: Learning dsviper means learning Viper. The Python API mirrors the
  C++ API.

- **Strong typing**: Unlike typical Python, dsviper raises exceptions immediately on type
  mismatches. This enforces data integrity.

- **Seamless bridge**: Python natives (lists, dicts, tuples) are accepted as input since
  Viper's metadata drives automatic conversion.

## Strong-Typed Layer Over Python

> Unlike Python's permissive duck typing, dsviper enforces types immediately.
> When you create a `Vector<Int64>`, only integers can be added. Type mismatches
> raise `ViperError` exceptions at the point of error, not downstream when data
> is corrupted. See [Error Handling](errors.md) for details.

## Quick Test

Test the type system. Create a vector of strings:

```{doctest}
>>> from dsviper import *

>>> v = Value.create(TypeVector(Type.STRING))
>>> v.append("hello")
>>> v.append("world")
>>> v
['hello', 'world']
```

Type checking in action — adding the wrong type raises immediately:

```{doctest}
>>> v.append(42)
Traceback (most recent call last):
    ...
dsviper.ViperError: ...expected type 'str', got 'int'...
```

## What's Next

- [Error Handling](errors.md) - Understanding ViperError exceptions
- [Types and Values](types_values.md) - Understanding the type system
- [DSM](dsm.md) - Define data models with DSM
- [Tutorial](tutorial.md) - Complete walkthrough with User/Login example
