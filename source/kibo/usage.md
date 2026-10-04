# Command-line usage

Kibo renders one template against a DSM model per run. A project rarely calls it by hand:
[kibo-project](kibo-project.md) reads the project's `kibo.toml` and runs kibo once per
template the chosen features need. This page is for calling the jar directly, or for
understanding what kibo-project does on your behalf. See [Templates](templates.md) for
templates as an ecosystem and the [Template Model reference](template_model.md) for what a
template reads.

## Synopsis

```bash
java -jar kibo-2.0.0.jar \
  -c [cpp | python | typescript] \
  -n [namespace] \
  -d [definitions.dsm.json] \
  -t [template] \
  -o [output]
```

## Options

| Option | Description |
|---|---|
| `-c, --converter` | The target: `cpp`, `python` or `typescript`. It decides how a type is spelled for the binding (`int64` is `int` in Python, `bigint` in TypeScript) and how output files are named |
| `-n, --namespace` | The name of the generated infrastructure. In C++ it is the namespace every generated line lives under, taken as written; in Python and TypeScript, the package |
| `-d, --dsm` | The DSM definitions, `.dsm.json` |
| `-t, --template` | A template file, or a directory of them |
| `-o, --output` | The output directory |
| `--atom WORD` | A word the snake_case of a static name never splits (`IPv4`, `YCoCg`); repeatable |
| `--rename NAME=snake_name` | A DSM name and the snake_case it takes; repeatable |
| `-q, --quiet` | Disable output messages |
| `-l, --log` | Display internal process steps |
| `-h, --help` | Show help |
| `-v, --version` | Show the version |

## What a run renders

A template declares what it is rendered for by the entry it defines: `main` or `model` once
for the whole model, `unit` once per DSM namespace, `pool` and `attachment_pool` once per
function pool. Kibo renders every entry the template declares, and names each output after
the scope it covers and the target's layout. The [Template Model
reference](template_model.md) lists the entries, their arguments and the layout.

A template that reads an accessor the model does not carry renders the empty string. Kibo
reports every such miss on stderr, each once with its count; a clean render prints nothing.

## Names

Where a target projects a DSM name to snake_case — a Python field, method, parameter or
module, a package directory — one rule applies: `vec3Curves` is `vec3_curves`, `docUInt8` is
`doc_uint8`, `render2DAttributes` is `render_2d_attributes`. A module name Python reserves
takes a trailing underscore (`annotations_`), in both bindings. `--atom` and `--rename` carry
what only a project knows. Two names that land on one spelling in one scope stop the
generation, and so does a namespace or a pool spelled like the model-wide code or like
another one.

## Example

Render the Python package of a model, from the first-party pack:

```bash
java -jar kibo-2.0.0.jar -c python -n features \
  -d features.dsm.json -t kibo-template-viper/python -o python/generated
```

The same with kibo-project, which also assembles the definitions, resolves the features into
their templates, embeds the definitions and copies the pack's runtime:

```toml
# kibo.toml
[project]
definitions = "definitions"
infrastructure = "features"

[generator]
templates = "2"

[target.python]
features = ["Base", "Wheel"]
output = "python/generated"
```

```bash
python3 kibo_project.py generate kibo.toml
```

## Coming from kibo 1.2

A template pack written for kibo 1.2 reads Template Model 1; moving it is covered in
[Migrating a template pack](migrating.md). A project's `generate.py` gives way to a
`kibo.toml` and [kibo-project](kibo-project.md).
