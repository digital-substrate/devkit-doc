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
download the DevKit from the [Downloads](https://digitalsubstrate.io/downloads/) page, unzip, and run:

```bash
cd dsviper-*-devkit
pip install -r requirements.txt
```

The DevKit's `requirements.txt` pulls `dsviper` from PyPI alongside the
GUI/web dependencies needed by the bundled tools.

## Verifying Installation

Verify that dsviper is correctly installed:

```pycon
>>> import dsviper
>>> dsviper.version()
```

If the call returns the version tuple, dsviper is ready to use.

## Understanding dsviper

**dsviper** is the Python extension module that provides access to the Viper runtime. Key
points:

- **dsviper = Viper**: Learning dsviper means learning Viper. The Python API mirrors the
  C++ API.

- **Strong typing**: Unlike typical Python, dsviper raises exceptions immediately on type
  mismatches. This enforces data integrity.

- **Seamless bridge**: Python natives (lists, dicts, tuples) are accepted as input since
  Viper's metadata drives automatic conversion.

## Core Philosophy

Understanding these principles helps you work effectively with Viper:

> **Metadata Everywhere Principle**
>
> Viper's type system carries metadata at runtime. This means Type, Value,
> Function, Serialization, Database Persistence, and RPC all leverage the same
> type information. Define your types once, and Viper handles serialization,
> validation, and cross-language interoperability automatically.

> **Strong-Typed Layer Over Python**
>
> Unlike Python's permissive duck typing, dsviper enforces types immediately.
> When you create a `Vector<Int64>`, only integers can be added. Type mismatches
> raise `ViperError` exceptions at the point of error, not downstream when data
> is corrupted. See [Error Handling](errors.md) for details.

> **Reference Semantics + Immutable Commits**
>
> Primitive values are immutable. Containers (Vector, Map, Set) are mutable
> via `shared_ptr` (like Python references). Once committed to a database,
> state becomes immutable in the commit DAG. This enables safe concurrent
> access and version control.

## Quick Test

Test the type system:

```pycon
>>> from dsviper import *

# Create a vector of strings
>>> v = Value.create(TypeVector(Type.STRING))
>>> v.append("hello")
>>> v.append("world")
>>> v
['hello', 'world']

# Type checking in action
>>> v.append(42)
dsviper.ViperError: expected type 'str', got 'int'
```

## What's Next

- [Error Handling](errors.md) - Understanding ViperError exceptions
- [Types and Values](types_values.md) - Understanding the type system
- [DSM](dsm.md) - Define data models with DSM
- [Tutorial](tutorial.md) - Complete walkthrough with User/Login example
