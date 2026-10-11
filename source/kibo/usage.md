# Command-line usage

Kibo renders templates against a DSM model, every template given with `-t` in the same run.
A project rarely calls it by hand: [kibo-project](kibo-project.md) runs it once per output
directory, with every template the chosen features need there. This page is for calling the
jar directly, or for understanding what kibo-project does on your behalf.

## Synopsis

```bash
java -jar kibo-2.0.0.jar \
  -c [cpp | python | typescript] \
  -n [namespace] \
  -d [definitions.dsm.json] \
  -t [template] [-t ...] \
  -o [output]
```

## Options

| Option | Description |
|---|---|
| `-c, --converter` | The target: `cpp`, `python` or `typescript`. It decides how a type is spelled for the binding (`int64` is `int` in Python, `bigint` in TypeScript) and how output files are named |
| `-n, --namespace` | The name of the generated infrastructure. In C++ it is the namespace every generated line lives under, taken as written; in Python and TypeScript, the package |
| `-d, --dsm` | The DSM definitions, `.dsm.json` |
| `-t, --template` | A template file, or a directory of them; repeatable — every template given renders in the same run, one JVM for all |
| `-o, --output` | The output directory |
| `--atom WORD` | A word the snake_case of a static name never splits (`IPv4`, `YCoCg`); repeatable |
| `--rename NAME=snake_name` | A DSM name and the snake_case it takes; repeatable |
| `--spell NAME=identifier` | How this target spells a DSM name it cannot take; the DSM name stays the one sent to the runtime; repeatable |
| `--type-name "type=Name"` | The name of a type, written as the DSM writes it (`tuple<App::A, float>`): its class and its type suffix, in every target. Kibo asks for it when two types would be written alike; repeatable |
| `--reserve KIND:name` | A name the template pack's own code takes in this target, for one family of names (`namespace`, `pool`, `type`, `field`, `case`, `attachment`, `function`, `parameter`); repeatable |
| `-q, --quiet` | Disable output messages |
| `-l, --log` | Display internal process steps |
| `-h, --help` | Show help |
| `-v, --version` | Show the version |

## What a run renders

Each template renders once per scope its entries declare — the whole model, each DSM
namespace, each pool — and each output is named by the target's layout. A template reading an
accessor the model does not carry is reported on stderr. The [Template Model
reference](template_model.md#what-a-template-is-rendered-for) lists the entries, the layout and
the diagnostics.

## Names

Kibo renames nothing on its own. Two names that land on one spelling, or a DSM name meeting a
name the pack's own code takes (`--reserve`), stop the generation; the message names the
directive to write. `--spell` is that directive for a name, `--type-name` for a type, and the
DSM name stays the one sent to the runtime. `--atom` and `--rename` adjust the snake_case rule
([`snake`](template_model.md#string-formats)). kibo-project passes `--reserve` from the pack and the
others from the project file: see [Names](kibo-project.md#names).

## Example

Render the Python package of a model, from the first-party pack:

```bash
java -jar kibo-2.0.0.jar -c python -n features \
  -d features.dsm.json -t kibo-template-viper/python -o python/generated
```

kibo-project does the same from a `kibo.toml`, and also assembles the definitions, resolves the
features into their templates, embeds the definitions and copies the pack's runtime: see the
[Kibo](index.rst) quickstart.
