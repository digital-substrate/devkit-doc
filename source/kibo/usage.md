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
  -d [definitions.dsm.json] \
  -t [template] \
  -o [output]
```

## Options

| Option              | Description                        |
|---------------------|------------------------------------|
| `-c, --converter`   | Target language: `cpp` or `python` |
| `-n, --namespace`   | Namespace for generated files      |
| `-d, --definitions` | Path to definitions (`.dsm.json`)  |
| `-t, --template`    | Template directory or file         |
| `-o, --output`      | Output directory or file           |
| `-q, --quiet`       | Disable output messages            |
| `-h, --help`        | Show help                          |
| `-v, --version`     | Show version                       |

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
set you need;

## Usage Examples

### Generate All C++ Features

```python
# From generate.py
templates = [
    'Model',
    'Data',
    'Stream', 'Json',
    'Database',
    'Attachments', 'AttachmentFunctionPool_Attachments',
    'ValueType', 'ValueCodec', 'ValueHasher',
    'Fuzz',
    'Test',
]

for template in templates:
    subprocess.run([
        'java', '-jar', JAR,
        '-c', 'cpp',
        '-n', 'Features',
        '-d', 'Features.dsm.json',
        '-t', f'{TEMPLATES}/cpp/{template}',
        '-o', 'Features',
    ])
```

### Generate Python Package

```python
subprocess.run([
    'java', '-jar', JAR,
    '-c', 'python',
    '-n', 'features',
    '-d', 'Features.dsm.json',
    '-t', f'{TEMPLATES}/python/package',
    '-o', 'python/features',
])
```

### Mixing the viper template pack with custom templates

Real projects often combine the shared `kibo-template-viper` pack with
project-local templates that emit code for a custom framework or surface.
Two distinct `-t` paths follow this convention:

| Source             | `-t` argument                | Purpose                                    |
|--------------------|------------------------------|--------------------------------------------|
| Shared viper pack  | `{TEMPLATES}/cpp/{template}` | Standard viper code (`Model`, `Data`, …)   |
| Project-local pack | `templates/{template}`       | Bindings for a custom framework or surface |

```{tip}
Project-local templates live in the project repo (e.g. `templates/RaptorLogic/`)
and are versioned with the code they target. The viper pack lives in its own
repo so it can evolve independently of any consumer.
```

### Complete generate.py Example

A production-ready script combining the viper pack and a project-local
template pack. This mirrors the script used by the
[Raptor Editor](../dsm/samples/raptor_editor.rst), which generates
four artefacts from a single DSM:

- viper C++ code under `src/RE/` (shared pack),
- a custom `RaptorLogic` C++ binding under `src/RaptorLogic/` (project-local pack),
- viper Python embedded into the editor, and
- a Python package shipped to the editor's `Scripts/` directory and to a `demo/`.

```python
#!/usr/bin/env python3
import argparse
import base64
import glob
import os
import subprocess
import zlib

from dsviper import DSMBuilder, DSMDefinitions, DefinitionsConst

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--re", action="store_true",
                    help="Generate C++ for RE (viper pack)")
parser.add_argument("-l", "--logic", action="store_true",
                    help="Generate C++ for RaptorLogic (custom pack)")
parser.add_argument("-e", "--editor", action="store_true",
                    help="Generate C++ for RaptorEditor")
parser.add_argument("-p", "--python", action="store_true",
                    help="Generate Python for RaptorEditor")
arguments = parser.parse_args()

# Sibling-checkout convention: kibo and the viper template pack live in
# their own repos next to this one under a common parent. Project-local
# templates (templates/RaptorLogic/) stay in this repo.
SIBLING_KIBO = '../kibo'
SIBLING_TEMPLATES = '../kibo-template-viper'


def _resolve_jar():
    env = os.environ.get('KIBO_JAR')
    if env:
        return env
    matches = sorted(glob.glob(f'{SIBLING_KIBO}/target/kibo-*.jar'))
    if not matches:
        raise SystemExit(f"No kibo jar at {SIBLING_KIBO}/target/. "
                         f"Run `mvn package` in {SIBLING_KIBO} or set KIBO_JAR.")
    return matches[-1]


JAR = _resolve_jar()
TEMPLATES = os.environ.get('KIBO_TEMPLATES') or SIBLING_TEMPLATES
KIBO = ['java', '-jar', JAR]


def generate_viper(namespace, dsm_path, template, output, *args):
    """Render a template from the shared viper pack."""
    cmd = KIBO + [
        '-c', 'cpp', '-n', namespace,
        '-d', dsm_path, '-t', f'{TEMPLATES}/cpp/{template}',
        '-o', output,
    ] + list(args)
    subprocess.run(cmd)


def generate_raptor_logic(namespace, dsm_path, template, output, *args):
    """Render a project-local template (here: bindings for RaptorLogic)."""
    cmd = KIBO + [
        '-c', 'cpp', '-n', namespace,
        '-d', dsm_path, '-t', f'templates/{template}',
        '-o', output,
    ] + list(args)
    subprocess.run(cmd)


def render_viper_templates(namespace, dsm_path, output):
    templates = [
        'Model', 'Data',
        'Stream',
        'Database',
        'Attachments',
        'ValueType', 'ValueCodec',
        'FunctionPool', 'AttachmentFunctionPool',
        'AttachmentFunctionPool_Attachments',
    ]
    for template in templates:
        generate_viper(namespace, dsm_path, template, output)


def generate_resource(definitions: DefinitionsConst, output: str):
    blob = definitions.encode()
    with open(output, 'w') as file:
        file.write(blob.embed("definitions"))


def generate_package(name: str, dsm_path: str,
                     definitions: DefinitionsConst, output: str):
    cmd = KIBO + [
        '-c', 'python', '-n', name,
        '-d', dsm_path, '-t', f'{TEMPLATES}/python/package',
        '-o', output,
    ]
    subprocess.run(cmd)
    blob = definitions.encode()
    encoded = base64.b64encode(zlib.compress(blob))
    with open(f'{output}/resources.py', 'w') as file:
        file.write(f"B64_DEFINITIONS = {encoded}")


def check_report(report):
    if report.has_error():
        for err in report.errors():
            print(repr(err))
        exit(1)


def save_dsm_definitions(dsm_definitions: DSMDefinitions, dsm_path: str):
    with open(dsm_path, "w") as file:
        file.write(dsm_definitions.json_encode())


PROJECT = 'RE'
DSM_SOURCE = 'definitions/RE'
DSM_PATH = f'{PROJECT}.dsm.json'

if not os.path.exists(JAR):
    raise SystemExit(f'{JAR} not found. Read the documentation to build the jar.')

print(f'using kibo: {KIBO}')

builder = DSMBuilder.assemble(DSM_SOURCE)
report, dsm_definitions, definitions = builder.parse()
check_report(report)
save_dsm_definitions(dsm_definitions, DSM_PATH)

if not (arguments.re or arguments.logic or arguments.editor or arguments.python):
    parser.print_help()
    exit(0)

if arguments.re:
    print('** Render C++ viper templates')
    render_viper_templates('RE', DSM_PATH, 'src/RE')
    generate_resource(definitions, 'src/RE/RE_Resources.hpp')

if arguments.logic:
    print('** Render C++ for RaptorLogic (custom pack)')
    generate_raptor_logic('RaptorLogic', DSM_PATH, 'RaptorLogic', 'src/RaptorLogic')

if arguments.editor:
    print('** Render C++ Python bridge for RaptorEditor')
    generate_viper('RE', DSM_PATH, 'Python', 'RaptorEditor/RaptorEditor')

if arguments.python:
    print('** Render Python package for RaptorEditor')
    generate_package('red', DSM_PATH, definitions,
                     'RaptorEditor/RaptorEditor/Scripts/red')
    print('** Render Python package for demo')
    generate_package('red', DSM_PATH, definitions, 'demo/red')
```

## Workflow

### Step 1: Parse and Persist DSM

```python
from dsviper import DSMBuilder

# Parse DSM source
builder = DSMBuilder.assemble("model.dsm")
report, dsm_definitions, definitions = builder.parse()

# Check for errors
if report.has_error():
    for err in report.errors():
        print(repr(err))
    exit(1)

# Persist the JSON definitions Kibo will read
with open("model.dsm.json", "w") as f:
    f.write(dsm_definitions.json_encode())
```

### Step 2: Generate Embedded Definitions

```python
# Generate C++ resource header consumed by the runtime
blob = definitions.encode()
with open("Resources.hpp", "w") as f:
    f.write(blob.embed("definitions"))
```

### Step 3: Run Kibo

```bash
java -jar kibo-1.2.7.jar -c cpp -n MyApp -d model.dsm.json -t templates/cpp/Data -o src/
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
