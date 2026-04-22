# Templated Features

Templated features are code templates that Kibo uses to generate infrastructure code from
DSM definitions.

## Understanding Templates

A templated feature is like a giant code snippet where the DSM definitions are injected
and recursively consumed to generate repetitive code that implements a feature for a data
model. Kibo knows how to map DSM primitives (bool, int8, float...) and generic collections
(vector\<T>, map\<K, V>) to standard C++ types and to the Viper type and value system.

```text
DSM Model + Template → Generated Code
```

Templated features may depend on other templated features and form an **ecosystem**. For
example, the `Database` feature depends on `Attachments` and `Model`.

## C++ Template Categories

Templates in `templates/cpp/` are organized by feature:

### Core Types

| Template | Purpose                                              |
|----------|------------------------------------------------------|
| `Data`   | Type implementations for enum, struct, concept, club |
| `Model`  | DSM definitions, paths, fields                       |

### Persistence

| Template      | Purpose                  |
|---------------|--------------------------|
| `Attachments` | Attachment accessors     |
| `Database`    | SQLite persistence layer |

### Serialization

| Template      | Purpose                                            |
|---------------|----------------------------------------------------|
| `Stream`      | Binary encoder/decoder                             |
| `Json`        | JSON encoder/decoder                               |
| `ValueCodec`  | Bridge between static C++ and dynamic Viper values |
| `ValueHasher` | Content hashing for values                         |
| `ValueType`   | Viper type mappings                                |

### Function Pools

| Template                             | Purpose                      |
|--------------------------------------|------------------------------|
| `FunctionPool`                       | Pure function bindings       |
| `FunctionPoolRemote`                 | Remote function call API     |
| `AttachmentFunctionPool`             | Stateful function bindings   |
| `AttachmentFunctionPoolRemote`       | Remote stateful calls        |
| `AttachmentFunctionPool_Attachments` | Pool exposing attachment API |

### Python Integration

| Template | Purpose                                     |
|----------|---------------------------------------------|
| `Python` | Python module constants for types and paths |

### Testing

| Template  | Purpose                                          |
|-----------|--------------------------------------------------|
| `Fuzz`    | Random value generation                          |
| `Test`    | Unit tests for fuzzing, JSON, streaming, storing |
| `TestApp` | Test application entry points                    |

## Python Template Categories

Templates in `templates/python/package/`:

| Template                           | Generated File                        | Purpose                                        |
|------------------------------------|---------------------------------------|------------------------------------------------|
| `__init__.py`                      | `__init__.py`                         | Package initialization                         |
| `definitions`                      | `definitions.py`                      | Type definitions for Viper                     |
| `data`                             | `data.py`                             | Classes for concepts, clubs, enums, structures |
| `attachments`                      | `attachments.py`                      | Attachment API wrappers                        |
| `database_attachments`             | `database_attachments.py`             | Database attachment API wrappers               |
| `path`                             | `path.py`                             | Field path constants                           |
| `value_type`                       | `value_type.py`                       | Dynamic type definitions                       |
| `function_pools`                   | `function_pools.py`                   | Function pool wrappers                         |
| `attachment_function_pools`        | `attachment_function_pools.py`        | Stateful pool wrappers                         |
| `function_pool_remotes`            | `function_pool_remotes.py`            | Remote function call wrappers                  |
| `attachment_function_pool_remotes` | `attachment_function_pool_remotes.py` | Remote stateful call wrappers                  |
| `wheel/pyproject.toml`            | `pyproject.toml`                      | Minimal pyproject.toml to build a wheel        |

All Python features are grouped into a single Python package.

## Generation Strategy

When using templated features, you must decide **what to generate** and **where to put**
the generated code. Each project uses generated code for different needs:

- Low-level serialization to insert in a framework.
- Unit tests to insert in the test infrastructure.
- A part of a feature to insert in a framework.
- A part of a feature to insert in an application.
- A Python module embedded in a C++ application.
- A Python package embedded in a C++ application.
- A Python wheel to distribute.

Each project has a `generate.py` script that describes these choices.

```{note}
You can also create your own generation tool using the C++ Viper API, or use custom
rules in your build system (CMake, etc.).
```

### Example: exp project

The exp project generates a framework and a Python package:

```python
# Extracted from exp/generate.py
if arguments.cpp:
    # Generate a framework
    render_templates(namespace=NAMESPACE, dsmb_path=DSMB_PATH, output=PROJECT)
    generate_resource(definitions=DEFINITIONS,
                      output=f'{NAMESPACE}/{NAMESPACE}_Resources.hpp')

    # Generate application for testing the generated code.
    generate(namespace=NAMESPACE, dsmb_path=DSMB_PATH, template='TestApp', output=".")

if arguments.package:
    # Generate the Python package
    generate_package(name='exp', dsmb_path=DSMB_PATH, definitions=DEFINITIONS,
                     output=f'python/exp')
```

### Example: Raptor Editor project

A larger project distributes generated code across multiple targets:

```python
# Extracted from com.digitalsubstrate.red/generate.py
if arguments.red:
    # Generate the framework Raptor
    render_templates(namespace=NAMESPACE, dsmb_path=DSMB_PATH, output=f'src/{NAMESPACE}')
    generate_resource(definitions=DEFINITIONS,
                      output=f'src/{NAMESPACE}/{NAMESPACE}_Resources.hpp')

if arguments.logic:
    # Generate a part of the RaptorLogic framework
    generate_logic(namespace='RaptorLogic', dsmb_path=DSMB_PATH, template='RaptorLogic',
                   output=f'src/RaptorLogic')

if arguments.editor:
    # Generate a part of the application
    generate(namespace='RE', dsmb_path=DSMB_PATH, template='Python',
             output=f'RaptorEditor/RaptorEditor')

if arguments.python:
    # Generate the Python package embedded in the application
    generate_package(name='red', dsmb_path=DSMB_PATH, definitions=DEFINITIONS,
                     output=f'RaptorEditor/RaptorEditor/Scripts/red')
```

## Generation Workflow

### 1. Prepare Binary Definitions

```python
from dsviper import DSMBuilder

builder = DSMBuilder.assemble("model.dsm")
report, dsm_defs, definitions = builder.parse()

# Save binary format for Kibo
with open("model.dsmb", "wb") as f:
    f.write(dsm_defs.encode().encoded())
```

### 2. Generate Embedded Resource

```python
# For C++ Model/Definitions.cpp
blob = definitions.encode()
with open("Resources.hpp", "w") as f:
    f.write(blob.embed("definitions"))
```

### 3. Call Kibo

```python
import subprocess


def generate(namespace, dsmb_path, template, output):
    subprocess.run([
        'java', '-jar', 'tools/kibo-1.2.7.jar',
        '-c', 'cpp',
        '-n', namespace,
        '-d', dsmb_path,
        '-t', f'templates/cpp/{template}',
        '-o', output
    ])


# Generate all features
templates = ['Model', 'Data', 'Attachments', 'Stream', 'Json', 'Database']
for t in templates:
    generate('MyApp', 'model.dsmb', t, 'src/MyApp')
```

### 4. Generate Python Package

```python
import subprocess
import base64
import zlib


def generate_package(name, dsmb_path, definitions, output):
    # Generate Python files
    subprocess.run([
        'java', '-jar', 'tools/kibo-1.2.7.jar',
        '-c', 'python',
        '-n', name,
        '-d', dsmb_path,
        '-t', 'templates/python/package',
        '-o', output
    ])

    # Generate embedded definitions
    blob = definitions.encode()
    encoded = base64.b64encode(zlib.compress(blob.encoded()))
    with open(f'{output}/resources.py', 'w') as f:
        f.write(f"B64_DEFINITIONS = {encoded}")
```

## Selecting Features

You don't need all templates. Select based on your needs:

### Minimal (Data Only)

```python
templates = ['Data']  # Just type classes
```

### Persistence

```python
templates = ['Model', 'Data', 'Attachments', 'Database']
```

### Full Stack

```python
templates = [
    'Model', 'Data',
    'Stream', 'Json',
    'Attachments', 'Database',
    'ValueType', 'ValueCodec', 'ValueHasher',
    'FunctionPool', 'AttachmentFunctionPool'
]
```

### With Testing

```python
templates = [..., 'Fuzz', 'Test', 'TestApp']
```

## Example: generate.py

A typical project has a `generate.py` script:

```python
#!/usr/bin/env python3
import subprocess
from dsviper import DSMBuilder

NAMESPACE = "MyApp"
DSM_PATH = "definitions/model.dsm"
DSMB_PATH = "build/model.dsmb"
OUTPUT = "src/generated"

# Parse and encode
builder = DSMBuilder.assemble(DSM_PATH)
report, dsm_defs, defs = builder.parse()
with open(DSMB_PATH, "wb") as f:
    f.write(dsm_defs.encode().encoded())

# Generate C++
for template in ['Model', 'Data', 'Attachments', 'Database']:
    subprocess.run([
        'java', '-jar', 'tools/kibo-1.2.7.jar',
        '-c', 'cpp', '-n', NAMESPACE,
        '-d', DSMB_PATH,
        '-t', f'templates/cpp/{template}',
        '-o', OUTPUT
    ])

# Generate Python package
subprocess.run([
    'java', '-jar', 'tools/kibo-1.2.7.jar',
    '-c', 'python', '-n', 'myapp',
    '-d', DSMB_PATH,
    '-t', 'templates/python/package',
    '-o', 'python/myapp'
])

print("Generation complete!")
```

## Summary

| Step     | Tool      | Input               | Output          |
|----------|-----------|---------------------|-----------------|
| Parse    | dsviper   | `.dsm`              | DSMDefinitions  |
| Encode   | dsviper   | DSMDefinitions      | `.dsmb`         |
| Generate | Kibo      | `.dsmb` + templates | C++/Python code |
| Compile  | CMake/pip | Generated code      | Binary/wheel    |

Templates let you generate exactly the infrastructure you need, from minimal type
definitions to full-stack persistence with RPC.

## Getting Started

For your project, copy `exp/generate.py` and keep only the features you need. Or adapt
the steps for your build system.

The steps for C++:

1. Save the DSM definitions to a binary representation (`.dsmb`).
2. Generate the resource for the Definitions included by the generated
   `Model/Definitions.cpp`.
3. Call `kibo-1.2.7.jar` for each feature.

For Python, you can use `dsm_util.py create_python_package` as a shortcut
(see [dsm_util](dsm_util.md)).

```{tip}
Read the [Template Model Reference](template_model.md) to write your own templates.
Study the source code of the provided templates in `templates/cpp/` to learn how to
decompose the implementation of a feature.
```

## What's Next

- [Template Model Reference](template_model.md) - Type suffix mechanism, naming
  conventions, and complete class reference for writing `.stg` templates
