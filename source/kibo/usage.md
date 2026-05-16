# Command-line usage

Kibo is the code generator that transforms DSM definitions into C++ and Python
infrastructure code. See [Templates](templates.md) for the template model.

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
first-party template pack for the Viper ecosystem is
[`kibo-template-viper`](../kibo-template-viper/index.rst), which ships
both C++ and Python templates. The full catalogue (which template
generates which files, and for which purpose) is in
[Templated Features](../kibo-template-viper/features.md).

## Generation strategy

Generation strategy is project-specific. Teams typically encode their
choices (which features, where to put generated code, which template paths)
in a `generate.py` script that invokes Kibo. See
[Templated Features](../kibo-template-viper/features.md) for the available
features in the viper template pack.

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

### Skeleton generate.py

A minimal script combining the viper pack with a project-local pack:

```python
import os, subprocess
from dsviper import DSMBuilder

JAR       = os.environ.get('KIBO_JAR')         # path to kibo-X.Y.Z.jar
TEMPLATES = os.environ.get('KIBO_TEMPLATES')   # path to kibo-template-viper
KIBO      = ['java', '-jar', JAR]


def generate_viper(namespace, dsm_path, template, output):
    """Render a template from the shared viper pack."""
    subprocess.run(KIBO + [
        '-c', 'cpp', '-n', namespace,
        '-d', dsm_path, '-t', f'{TEMPLATES}/cpp/{template}',
        '-o', output,
    ])


def generate_project_local(namespace, dsm_path, template, output):
    """Render a project-local template (e.g. custom framework bindings)."""
    subprocess.run(KIBO + [
        '-c', 'cpp', '-n', namespace,
        '-d', dsm_path, '-t', f'templates/{template}',
        '-o', output,
    ])


def generate_package(name, dsm_path, output):
    """Render a Python package from the viper pack."""
    subprocess.run(KIBO + [
        '-c', 'python', '-n', name,
        '-d', dsm_path, '-t', f'{TEMPLATES}/python/package',
        '-o', output,
    ])


# Parse DSM, persist the .dsm.json, then run as many generations as needed.
builder = DSMBuilder.assemble('definitions/MyApp')
report, dsm_definitions, definitions = builder.parse()
with open('MyApp.dsm.json', 'w') as f:
    f.write(dsm_definitions.json_encode())

generate_viper('MyApp', 'MyApp.dsm.json', 'Model', 'src/MyApp')
generate_project_local('MyAppLogic', 'MyApp.dsm.json', 'MyAppLogic', 'src/MyAppLogic')
generate_package('myapp', 'MyApp.dsm.json', 'python/myapp')
```

