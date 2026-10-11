# Migrating a template pack

A template pack written for kibo 1.2 reads **Template Model 1**; kibo 2 exposes **Template
Model 2**. Model 2 renames the accessors that describe a type **as the binding sees it**, and
changes some of the **values** the model carries — how a C++ type names its namespace, how a
container class is named, what a binding type answers for a concept or for `any`. There are no
compatibility aliases: a pack written against Model 1 does not render against kibo 2 until it
is migrated.

This page is the complete list of both: what was renamed, and what now reads differently. The
list is measured, not remembered: a probe template printing every scalar accessor of Template
Model 1 is rendered by both kibo lines on several models, and every value that differs must be
listed here ([devkit-codegen-test](https://github.com/digital-substrate/devkit-codegen-test),
`tools/template_model.py`). The renames below were also run on the whole kibo-template-viper
1.2 pack, which then renders under kibo 2 with nothing on stderr.

A project that renders the pack is moved as [Migrating a project](project.md) says.

## The method: a diff you can account for

A migration changes the names your templates read, and the values below change what some of
them return. So the test is a diff in which **every difference has a reason on this page**:

```sh
# before, with your current kibo
java -jar kibo-1.2.x.jar -c <target> -n <ns> -d model.dsm.json -t templates/ -o before/

# after, with kibo 2 and your migrated templates
java -jar kibo-2.0.0.jar -c <target> -n <ns> -d model.dsm.json -t templates/ -o after/

# every generated file names the jar that produced it, so that one line differs
diff -r -I 'by kibo-[0-9.]*\.jar' before/ after/
```

Render, in both, every template directory the project renders, with the same `-n` and the same
model: `-t` takes a directory or a single `.stg` file. The `.dsm.json` is the same for both:
the one the kibo 1.2 script wrote, or the one kibo-project writes beside `kibo.toml`. A TypeScript pack was rendered by kibo 1.2 with `-c python`: render it with `-c python`
under kibo 2 too, so that the diff shows the migration alone, then move it to `-c typescript` as
a change of its own (row 9 below).

Read the diff hunk by hunk. A difference that one of the [value changes](#what-reads-differently)
explains is expected; adapt your templates to it, or accept it in what you generate. **A
difference that none of them explains means a step of the migration is wrong.** Run it on the
largest model you have, and on one with several namespaces: a small model does not reach every
accessor, and several of the changes appear only across namespaces.

If your pack stamps its own version into what it generates, hold that stamp fixed for the
comparison, or ignore its line the same way. Take up what Model 2 makes possible — `dsmType` in
messages, dropping a leaf table — as a second change, once the first diff is accounted for;
otherwise a diff tells you two things at once.

## Names you build yourself

The diff shows what kibo 2 renders differently. It cannot show a name your templates build
by concatenation when that name reads the same in both renders but no longer designates
anything: `Set_<proxy>` renders `Set_Demo_ConceptAKey` before and after, while kibo 2's
packs generate `Set_of_Demo_ConceptAKey`. The rows of the next section say which names
moved; then check the generated code itself for a name it uses and does not define — a
compiler for C++, `tsc --noEmit` for TypeScript, a linter such as `pyflakes` for Python, or
simply importing and exercising the package. Search your templates for the places that
concatenate a class name (`Set_`, `Optional_`, `Vector<`, `…Suffix>`); each is a place to
check.

## Read the diagnostics, but do not stop there

A template that reads an accessor the model does not carry renders the **empty string**, and
kibo 2 reports it on stderr ([Render diagnostics](../kibo/template_model.md#render-diagnostics)). During
the migration, a line on stderr is a rename not yet done. **An empty stderr is not the end**: it
says every accessor resolves, not that every value is the one your templates expect — the diff
says that — nor that every name your templates build still designates a generated class.

## The renames

One to one, on the same objects:

| Model 1 | Model 2 | On |
|---|---|---|
| `pythonType` | `bindingType` | the classes that describe a type: concepts, clubs, enumerations, structures, structure fields, function parameters, attached key and document types, and the nine container functions |
| `pythonElementType` | `bindingElementType` | `vec`, `mat`, `optional`, `vector`, `set`, `map`, `xarray` functions, and `TemplateField` |
| `pythonKeyType` | `bindingKeyType` | `map` functions and `TemplateField` |
| `returnPythonType` | `returnBindingType` | functions and attachment functions |
| `pythonTupleType` | `bindingSequenceType` | `vec` and `mat` functions |
| `pythonColumnType` | `bindingColumnType` | `mat` functions |
| `pythonMembers` | `members` — see below | `tuple` and `variant` functions |

The members of a binding type are unchanged: `proxy`, `useProxy`, `typeSuffix`, `type`. No other
accessor of Model 1 was removed or renamed.

The first six rows are a word-for-word replacement. Run it on every `.stg` file of the pack; the
word boundaries matter, since `pythonType` is a prefix of `pythonTupleType`:

```sh
find templates -name '*.stg' -exec perl -pi -e '
  s/\bpythonElementType\b/bindingElementType/g;
  s/\bpythonKeyType\b/bindingKeyType/g;
  s/\breturnPythonType\b/returnBindingType/g;
  s/\bpythonTupleType\b/bindingSequenceType/g;
  s/\bpythonColumnType\b/bindingColumnType/g;
  s/\bpythonType\b/bindingType/g;
' {} +
```

**`pythonMembers` is not a word-for-word rename.** A tuple or a variant already had `members` in
Model 1: one entry per member, with its native `type` and its `typeSuffix`. Model 2 keeps that
list and adds to each member what `pythonMembers` held, under `bindingType`:

| Read on a member | For |
|---|---|
| `.dsmType` | what the model calls the member — `uint8`, `Test::StructureS` (new) |
| `.type` | the native spelling, as in Model 1 |
| `.typeSuffix` | the neutral key naming the generated symbol, as in Model 1 |
| `.bindingType` | what an entry of `pythonMembers` was: `.proxy`, `.useProxy`, `.type`, `.typeSuffix` |

So an expression over `pythonMembers` iterates `members` and hands each member's `bindingType`
to what it did before. Leave the expressions that already read `members` as they are.

| Model 1 | Model 2 |
|---|---|
| `<v.pythonMembers:{m\|<m.type>}>` | `<v.members:{m\|<m.bindingType.type>}>` |
| `<v.pythonMembers:{m\|<m:tuple_getter(i0)>}>` | `<v.members:{m\|<tuple_getter(m.bindingType, i0)>}>` |
| `<v.pythonMembers:python_type();separator=" \| ">` | `<v.members:{m\|<python_type(m.bindingType)>};separator=" \| ">` |
| `<v.pythonMembers:variant_constructor(v)>` | `<v.members:{m\|<variant_constructor(m.bindingType, v)>}>` |

The rule of the last two rows: `<x.pythonMembers:t(args)>`, which calls `t` with each entry
first, becomes a call of `t` in a lambda, with the member's `bindingType` first. Its index, `i`
or `i0`, stays the lambda's. The two forms are mechanical too:

```sh
find templates -name '*.stg' -exec perl -pi -e '
  s/(\w+)\.pythonMembers:\{(\w+)\|<\2:(\w+)\(([^()]*)\)>\}/"$1.members:{$2|<$3($2.bindingType".($4 ne ""?", $4":"").")>}"/ge;
  s/(\w+)\.pythonMembers:(\w+)\(([^()]*)\)/"$1.members:{m|<$2(m.bindingType".($3 ne ""?", $3":"").")>}"/ge;
' {} +
grep -rn pythonMembers templates    # what remains is a lambda reading m.<x>: make it m.bindingType.<x>
```

## What reads differently

Each row is a change of value under the same accessor, after the renames. They are what the
diff shows; the last column says what a template does about it.

| # | Change | Example, Model 1 → Model 2 | In your templates |
|---|---|---|---|
| 1 | **A C++ type names its namespace in lower snake case**: `type`, `typeInNamespace`, `elementType`, `keyType`, a member's `type`, and the names in `membersInNamespace` and `strictDescendantsInNamespace` | `Demo::StructureS` → `demo::StructureS`; `ModelA::Material` → `model_a::Material` | A pack that declares the namespaces itself declares them in the same spelling: `namespace <u.name;format="lsc">`. The DSM spelling stays in `dsmType` and `namespace`. |
| 2 | **`AnyConceptKey`, the key of `any_concept`, lives in the infrastructure namespace**, the one `-n` names | `AnyConceptKey` → `::features::AnyConceptKey` | Declare `AnyConceptKey` in the namespace `-n` names, or read the name from the model rather than writing it. |
| 3 | **A parent from another namespace is named with its namespace** in `parentNameInNamespace` | `Thing` → `core::Thing` | Nothing, if you used it as a C++ name: Model 1 named a parent from another namespace as if it were local. |
| 4 | **An attachment's `representation` names a type of another namespace with its namespace** | `attachment<Material, string> Annotations::note` → `attachment<ModelA::Material, string> Annotations::note` | Nothing, unless you parse it. A type of the attachment's own namespace stays unqualified. |
| 5 | **A container class of a binding is named after what it holds**: `bindingType.proxy` and `bindingType.type` of a container | `Map_int8_to_string` → `Map_of_int8_to_string`; `Vec_uint8_2` → `Vec2_of_uint8`; `Mat_uint8_2_3` → `Mat2x3_of_uint8`; `Tuple_uint8_string` → `Tuple2_of_uint8_and_string`; `Variant_A_B` → `Variant2_of_A_or_B` (a tuple and a variant say how many members follow, so a nested one reads one way) | Name a container class from its `proxy`. A map's set of keys and an attachment's set of keys have their own binding type, `bindingKeySetType`. Where no accessor carries the class you need — the optional an attachment's `get` returns, the vector an xarray converts to — build it by the same rule: `Optional_of_<proxy>`, `Vector_of_<proxy>`. A name built by the 1.2 rule (`Set_<proxy>`, `Vector<elementTypeSuffix>`) points at a class that is no longer generated, and reads the same in both renders, so the diff does not show it: see [Names you build yourself](#names-you-build-yourself). |
| 6 | **A concept's or a club's `bindingType.type` is its key class** | `Demo_ConceptA` → `Demo_ConceptAKey` | Every name you built from a concept's or a club's `bindingType.type` moves: where you appended `Key`, read `bindingType.type` alone; where you meant the entity's own name (a runtime id constant, say), read `bindingType.proxy`, which is unchanged. |
| 7 | **`any` is a proxy** | `bindingType.type` `dsviper.ValueAny` → `Any`; `useProxy` `false` → `true` | A pack that generates no `Any` class keeps a leaf table for it: test the type suffix `_Any` (row 12), and write `dsviper.ValueAny` yourself. |
| 8 | **A set of keys is spelled as the DSM spells it** in `dsmType` | `set<Demo::ConceptA>` → `set<key<Demo::ConceptA>>` | Nothing, unless you parsed the old form. |
| 9 | **A binding accessor answers for the target being generated**, and a native target has no binding | under `-c cpp`, the `type` of `bindingType`, `bindingElementType` and `bindingKeyType`, and a member's `bindingType.type`, are empty where `useProxy` is false — a primitive, for instance — and give the proxy where it is true (`proxy` is never empty); `bindingSequenceType` and `bindingColumnType` are always empty; Model 1 returned Python spellings there | Generate binding code with the binding's own target: `-c python` gives exactly what Model 1 gave under any target, apart from rows 5 to 7; `-c typescript` gives the TypeScript spellings (`bigint` for a 64-bit integer). |
| 10 | **Three lists changed order** | a namespace's `concepts` list a parent before its children (Model 1: by name); the container function lists (`optionalFunctions`, …) are sorted by their C++ type, so row 1 moves them; `attachedDocumentTypes` is sorted by its type suffix, so row 12 moves it | Nothing, unless the order of what you generate matters to you; then sort it yourself. |
| 11 | **A C++ set or map whose element or key holds a floating-point value outside any structure takes `Viper::StaticLess`**, in `type`, `typeInNamespace`, `elementType` and the container function lists | `std::set<double>` → `std::set<double, Viper::StaticLess>`; `std::map<std::array<float, 3>, std::int32_t>` → `std::map<std::array<float, 3>, std::int32_t, Viper::StaticLess>` | Nothing, if you write the type the model gives. `std::less` orders such a value as IEEE 754 does, which is no order once a NaN is present: the tree is undefined. Where you built a set of a map's keys yourself (`std::set<<keyType>>`), read `keySetType`, which carries the same comparator. |
| 12 | **A type suffix is `_` and the type's name** (`bindingType.proxy`), in every target, so that two types never share one: a nested tuple or variant made two types alike in Model 1 | `_vector_float` → `_Vector_of_float`; `_map_int64_to_vector_string` → `_Map_of_int64_to_Vector_of_string`; `_tuple_int64_float` → `_Tuple2_of_int64_and_float`; `_any` → `_Any`; a named type and a primitive are unchanged (`_Demo_StructureS`, `_Demo_ConceptAKey`, `_int64`) | Nothing, where the suffix is a key you concatenate inside the generated code (`write<v.typeSuffix>`). A public name built from it — a function the application calls — is renamed with it: its callers move too. A suffix your templates write literally (`_type_any`) is written the new way. |

Two additions are not changes: **structures and enumerations now carry `dsmType`**, as concepts
and clubs already did, and a member of a tuple or a variant carries it too.

## Does this affect your pack?

**A native target — C++ — is affected by rows 1 to 4, 8, 10, 11 and 12**, wherever it reads a type, a
parent name or a representation. Rows 1 and 2 are the ones a C++ pack meets first: the generated
namespaces are spelled in lower snake case, as the modules of the other bindings are.

**A delegating target — one that reaches the runtime through a binding and generates proxies —
is affected by every row.** Rows 5 to 7 change the names of the classes it generates and
refers to; row 12 the names of the helpers keyed on a type suffix.

## Templates that emit code calling the generated package

A template of your own may emit code that calls the package the pack generates: helpers beside
it, conversions, a report that imports its classes. The renames make it render, stderr is
empty, the diff is accounted for — and the module it writes still calls the 1.2 package
(`from .data import *`, `definitions.RuntimeIds.X`, `value_type.attachment_X()`, `vpr_value`),
which no longer exists. The diff cannot show this: the template wrote those names itself, in
both renders. Running the code does: kibo-project's validation imports the package, builds every
structure and runs `mypy --strict` on every module of it, yours included.

The code the template emits then moves as hand-written code does
([Migrating application code](application.md)), except that the template builds each name
from the model. In the Python package kibo-template-viper 2 generates:

| The code names | 1.2 | A template writes, in 2.0 |
|---|---|---|
| a unit's types, from a module at the package root | `from .data import *` | `from . import <u.name;format="snake">`, one import per namespace (`<m.nameSpaces:{u\|…}>`). A relative import does not depend on the package's name. |
| a type, in a type position | `<s.pythonType.type>` (`Test_StructureS`) | `<s.bindingType.qualified>` (`test.StructureS`) from outside a unit's module, `.annotation` inside it. `bindingType.type` of an entity is a flat name that designates no class. |
| a container class | `Set_X` | its `bindingType.qualified` (`containers.Set_of_X`): `proxy` is the class name alone, without its module |
| `any` | `dsviper.ValueAny` | `AnyValue`, as `.annotation` writes it |
| `AnyConceptKey`, `Key` | from `.data` | `from ._codegen import AnyConceptKey, Key` |
| an entity's runtime id | `definitions.RuntimeIds.<pythonType.type>` | the constant of its unit: `<c.namespace;format="snake">.<c.name;format="usnake"><if(c.nameIsUpperSnake)>_ID<endif>` |
| an attachment | `value_type.attachment_<ns>_<id>()`, `<ns>_<concept>_<att>_get(…)` | `<a.namespace;format="snake">.attachments.<a.conceptScope>.<a.name;format="snake">`, with `get`, `set`, `keys`, `diff_keys`, `runtime_id`, `descriptor`; import the unit's attachments module by its path (`from .<unit> import attachments`) |
| the runtime value of a proxy | `p.vpr_value` | `p.unwrap_value()` |

Two consequences of the validation:

- The emitted code must type-check strictly, which 1.2 output was never asked to: every
  function annotated, no untyped empty `set()` or `dict()`. Read a document through the
  generated attachment rather than the raw `dsviper` call: `diff_keys` on the attachment
  returns typed keys, where the runtime's returns a `ValueSet` of every value type.
- `m.setFunctions` lists every set of the model, a set of keys beside a set of structures or of
  strings, and the Template Model does not tell them apart. A helper meant for keys iterates
  the concepts and clubs instead (`<[m.concepts, m.clubs]:helper()>`), and names each key class
  by its `bindingType.qualified` (`test.ConceptAKey`).

## Naming a type in a message

Model 2 lets a message name a type as the model does: `dsmType` in a comment, a docstring, a
`repr` or an exception message, the target's spelling in a type position ([Which space to use
where](../kibo/template_model.md#which-space-to-use-where)). Adopting it moves your generated output, so
do it after the migration's diff is accounted for, as its own change.

## Dropping your leaf table

If your pack carries a dictionary mapping DSM primitive names to your binding's spellings —
`int64` to `bigint`, `blob` to a runtime value class — Model 2 lets you delete it and read
`bindingType.type` instead, provided kibo knows your binding. Kibo 2 ships vocabularies for
`python` and `typescript`. If yours is neither, keep your table: `proxy` and `useProxy` still let
you resolve a leaf yourself. Either way, verify by the same diff.

## What Model 2 adds, without breaking anything

A Model 1 pack renders its whole model from `main(m)`, as before. What a pack can take up when
it wants to, each described in the [Template Model reference](../kibo/template_model.md):

- entries per scope — `model(m)`, `unit(u)`, `pool(p)`, `attachment_pool(p)` — so that a
  namespace becomes a unit of generated code, with its `include`, `guard` and `dependencies`;
- dependencies by what an artefact emits: `u.dependencies.types`, `u.dependencies.attachments`,
  and `u.dependencies.attachmentFields` for an attachments artefact that addresses a document
  field by field;
- `keySetType` on a map field, and `strictAncestorsInNamespace` on a concept;
- the formats `string`, `docstring`, `comment`, `snake` and `usnake`.

## Checklist

1. Regenerate with your current kibo into `before/`.
2. Apply [the renames](#the-renames): the word-for-word script, then the `pythonMembers` one,
   then by hand what `grep pythonMembers` still finds.
3. Regenerate with kibo 2 into `after/`; read stderr until it is empty.
4. `diff -r -I 'by kibo-[0-9.]*\.jar' before/ after/`, and give each difference its row in
   [What reads differently](#what-reads-differently). Adapt your templates where the row says
   so; a difference with no row is a step done wrong.
5. Check the generated code for names it uses and does not define: the
   [names you build yourself](#names-you-build-yourself) do not show in the diff.
6. Generate with kibo-project, validation on, with your features in the target. For a template
   that [emits code calling the generated package](#templates-that-emit-code-calling-the-generated-package),
   this is the proof the diff cannot give.
7. Only then take up `dsmType` in messages and comments, or drop your leaf table, each as its
   own change with its own diff.
