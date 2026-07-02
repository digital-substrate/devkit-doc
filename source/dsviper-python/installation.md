# Installation

This chapter covers installing and verifying the dsviper Python module.

## Prerequisites

- Python 3.10+ (cp310 / cp311 / cp312 / cp313 / cp314 wheels published)
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

```{note}
`dsviper` is distributed under the Digital Substrate Commercial License 1.2,
which grants a free **Evaluation License** for assessment and training, and a
paid **Commercial License** by written agreement. See [License](../legal/license.md)
before any commercial use.
```

## Installing from the DevKit

If you also want Kibo, kibo-template-viper, dsviper-tools
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

