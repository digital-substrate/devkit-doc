# Kibo

Kibo is the code generator that transforms DSM definitions into C++ and Python
infrastructure code.

## Overview

```text
DSM Definitions  →  Kibo  →  Generated Code
   (273 lines)      ↓       (15,592 lines)
                Templates
```

Kibo uses StringTemplate files (`.stg`) to generate code from DSM models.

## Synopsis

```bash
java -jar kibo-1.2.7.jar \
  -c [converter] \
  -n [namespace] \
  -d [definitions.dsmb] \
  -t [template] \
  -o [output]
```

## Options

| Option              | Description                          |
|---------------------|--------------------------------------|
| `-c, --converter`   | Target language: `cpp` or `python`   |
| `-n, --namespace`   | Namespace for generated files        |
| `-d, --definitions` | Path to binary definitions (`.dsmb`) |
| `-t, --template`    | Template directory or file           |
| `-o, --output`      | Output directory or file             |
| `-q, --quiet`       | Disable output messages              |
| `-h, --help`        | Show help                            |
| `-v, --version`     | Show version                         |

## Available templates

Kibo itself is template-agnostic — it does not bundle templates. The
first-party template pack for the dsviper / Viper ecosystem is
[`kibo-template-viper`](../kibo-template-viper/index.rst), which ships
both C++ and Python templates. The full catalogue (which template
generates which files, and for which purpose) is in
[Templated Features](../kibo-template-viper/features.md).

## Generation strategy

Before invoking Kibo, decide **what to generate** and **where to put it**.
Each project tends to use generated code differently:

- low-level serialization to insert into a framework,
- unit tests to insert into a test infrastructure,
- a part of a feature to insert into a framework,
- a part of a feature to insert into an application,
- a Python module embedded in a C++ application,
- a Python package embedded in a C++ application,
- a Python wheel to distribute.

Each project usually has a `generate.py` script that encodes these
choices and runs Kibo accordingly.

```{note}
You can also build your own generation tool using the C++ Viper API, or
drive Kibo from custom rules in your build system (CMake, etc.).
```

For the catalogue of features available in the viper template pack, see
[Templated Features](../kibo-template-viper/features.md). Pick the minimal
set you need; Kibo will resolve dependencies between features for you.

## Usage Examples

### Generate All C++ Features

```python
# From generate.py
templates = [
    'Model', 'Data',
    'Attachments', 'Stream', 'Json',
    'Database',
    'ValueType', 'ValueCodec', 'ValueHasher',
    'Fuzz', 'Test'
]

for template in templates:
    subprocess.run([
        'java', '-jar', 'kibo-1.2.7.jar',
        '-c', 'cpp',
        '-n', 'MyApp',
        '-d', 'model.dsmb',
        '-t', f'templates/cpp/{template}',
        '-o', 'src/MyApp'
    ])
```

### Generate Python Package

```python
subprocess.run([
    'java', '-jar', 'kibo-1.2.7.jar',
    '-c', 'python',
    '-n', 'mymodel',
    '-d', 'model.dsmb',
    '-t', 'templates/python/package',
    '-o', 'python/mymodel'
])
```

### Complete generate.py Example

A production-ready script combining all generation steps:

```python
#!/usr/bin/env python3
"""Complete code generation script for a Viper project."""
import subprocess
import argparse
import base64
import zlib
from dsviper import DSMBuilder

# Configuration
JAR = 'tools/kibo-1.2.7.jar'
KIBO = ['java', '-jar', JAR]
TEMPLATES_CPP = 'templates/cpp'
TEMPLATES_PY = 'templates/python/package'

def check_report(report):
    """Exit on parse errors."""
    if report.has_error():
        for err in report.errors():
            print(repr(err))
        exit(1)

def generate_cpp(namespace, dsmb, template, output):
    """Generate C++ code from a template."""
    subprocess.run(KIBO + [
        '-c', 'cpp', '-n', namespace,
        '-d', dsmb, '-t', f'{TEMPLATES_CPP}/{template}',
        '-o', output
    ])

def generate_resource(definitions, output):
    """Generate embedded C++ resource."""
    blob = definitions.encode()
    with open(output, 'w') as f:
        f.write(blob.embed("definitions"))

def generate_python(name, dsmb, definitions, output):
    """Generate Python package with embedded definitions."""
    subprocess.run(KIBO + [
        '-c', 'python', '-n', name,
        '-d', dsmb, '-t', TEMPLATES_PY,
        '-o', output
    ])
    # Embed definitions as base64
    blob = definitions.encode()
    encoded = base64.b64encode(zlib.compress(blob))
    with open(f'{output}/resources.py', 'w') as f:
        f.write(f"B64_DEFINITIONS = {encoded}")

# Parse DSM
builder = DSMBuilder.assemble("definitions/MyApp")
report, dsm_defs, definitions = builder.parse()
check_report(report)

# Save binary definitions
with open("MyApp.dsmb", "wb") as f:
    f.write(dsm_defs.encode())

# Generate C++ (standard templates)
for template in ['Model', 'Data', 'Attachments', 'Stream', 'Database',
                 'ValueType', 'ValueCodec', 'ValueHasher', 'FunctionPool']:
    generate_cpp('MyApp', 'MyApp.dsmb', template, 'src/MyApp')

# Generate embedded resource
generate_resource(definitions, 'src/MyApp/MyApp_Resources.hpp')

# Generate Python package
generate_python('myapp', 'MyApp.dsmb', definitions, 'python/myapp')

print("Generation complete!")
```

## Workflow

### Step 1: Parse and Encode DSM

```python
from dsviper import DSMBuilder

# Parse DSM file
builder = DSMBuilder.assemble("model.dsm")
report, dsm_defs, definitions = builder.parse()

# Check for errors
if report.has_errors():
    print(report.errors())
    exit(1)

# Save binary format
with open("model.dsmb", "wb") as f:
    f.write(dsm_defs.encode().encoded())
```

### Step 2: Generate Embedded Definitions

```python
# Generate C++ resource for Definitions.cpp
blob = definitions.encode()
with open("Resources.hpp", "w") as f:
    f.write(blob.embed("definitions"))
```

### Step 3: Run Kibo

```bash
java -jar kibo-1.2.7.jar -c cpp -n MyApp -d model.dsmb -t templates/cpp/Data -o src/
```

### Step 4: Compile and Link

The generated code requires linking against the Viper runtime.

## Amplification Metrics

| Project       | DSM Lines | Generated Lines | Ratio |
|---------------|-----------|-----------------|-------|
| Graph Editor  | 273       | 15,592          | 57x   |
| Raptor Editor | 2,003     | 126,182         | 63x   |

Kibo typically generates 57-63x more code than the input DSM.

## What's Next

- [Templates](templates.md) - What templates are and how they fit together
- [Template Model Reference](template_model.md) - Write your own templates
- [Templated Features](../kibo-template-viper/features.md) - Catalogue of the viper template pack
- [IDE Integration](../dsm/ide.md) - VS Code and JetBrains
