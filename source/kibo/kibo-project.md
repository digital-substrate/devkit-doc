# kibo-project

A project states its code generation once, in a project file, `kibo.toml`. `kibo-project`
reads it and drives the two components it does not replace: `dsviper`, which assembles the DSM
into definitions, and the kibo jar, which renders a template pack. A project no longer carries
a generation script.

For each target of the project file, `kibo_project.py`:

1. assembles the definitions with `dsviper`, into `<infrastructure>.dsm.json` beside the
   project file — an intermediate, to ignore in version control;
2. finds the template pack, and the newest kibo jar the pack accepts;
3. resolves the features into the templates they need, dependencies included;
4. runs kibo once per template, into the directories the pack declares;
5. writes the embedded definitions in the encoding the pack declares, and copies the pack's
   runtime beside the generated sources.

The tool knows nothing of a particular pack: what a feature renders, where it lands and how
the definitions are embedded are read from the pack's `features.json`. Every file it writes
says where it comes from.

Source: [digital-substrate/kibo-project](https://github.com/digital-substrate/kibo-project).
It needs Python 3.11 or later with `dsviper`, and Java 17 for kibo.

## Usage

```bash
python3 kibo_project.py generate [kibo.toml] [--target NAME ...] [--definitions PATH] [--into DIR]
python3 kibo_project.py plan     [kibo.toml] [--definitions PATH]
```

`plan` shows the jar and the pack it found and, per target, the features it renders and every
template with where it lands, without writing anything. `--definitions` renders another model
than the project's, for one run. `--into` renders into another directory, each output keeping
its place relative to the project, and leaves the project untouched: two renderings, before
and after a change, can then be compared.

## The project file

```toml
[project]
definitions = "definitions"          # a .dsm file or a directory of them
infrastructure = "crossing"          # the name passed to kibo as -n

[generator]
templates = "2"                      # the template pack's line
manifests = ["../templates/features.json"]   # optional: the project's own features

[target.cpp]
features = ["TestApp"]
output = "cpp/generated"

[target.python]
features = ["Base", "Pool", "Wheel"]
output = "python/generated"
clean = true                         # optional: empty the sources directory first
```

Paths are relative to the project file. A target may set its own `infrastructure`.

A target named after a language needs nothing more. A project that renders one language to
several places names each target for what it produces, and states its language:

```toml
[target.infrastructure]
language = "cpp"
features = ["Base", "Attachments", "Pool"]
output = "src/rei"

[target.client]                      # the pool's client side, for another binary
language = "cpp"
features = ["PoolRemote"]
with_requirements = false            # Base is the infrastructure's
output = "client/generated"
```

- `[generator] kibo = "2"` optionally pins the kibo line; by default the pack's floor decides.
- `with_requirements = false` renders only the templates of the features named, not those they
  require. It is refused unless another target of the same language and infrastructure renders
  the rest.
- `clean` removes the files of a type the definitions no longer declare. It is refused when the
  sources directory holds the project itself.
- A project's own manifest follows the pack's format; its templates sit beside it, in
  `<manifest dir>/<target>/`. A feature name the pack already declares is refused.

A project spells a static name its own way where the snake_case rule cannot know better:

```toml
[names]
atoms = ["IPv4", "YCoCg"]            # never split: IPv4Address -> ipv4_address

[names.rename]
"f_E" = "f_enum"                     # a whole name, spelled as written here
```

## Where the generator comes from

| | |
|---|---|
| kibo jar | `KIBO_JAR`; else `kibo-*.jar` beside the script; else `../kibo/target/kibo-*.jar` |
| template pack | `KIBO_TEMPLATES`; else `../templates`; else `../kibo-template-viper` |

The pack is checked against the project's declared line through the version stamped in its
templates. The jar is the newest at or above the floor the pack declares; an explicit
`KIBO_JAR` below that floor is refused.

## Coming from a generate.py

A kibo 1.2 project drove kibo from a `generate.py`, one subprocess per template. Its
features become a target's `features`, its output paths the target's `output`, its namespace
the project's `infrastructure`; the templates each feature needs, their order and the
embedded definitions are the pack's business.
