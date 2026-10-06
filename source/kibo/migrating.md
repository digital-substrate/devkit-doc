# Migrating a template pack from Template Model 1 to Template Model 2

Template Model 2 ships with kibo 2. It renames the accessors that describe a type **as the
binding sees it**, and it changes some of the **values** the model carries — how a C++ type
names its namespace, how a container class is named, what a binding type answers for a
concept or for `any`. There are no compatibility aliases: a pack written against Model 1 does
not render against kibo 2 until it is migrated.

This page is the complete list of both: what was renamed, and what now reads differently. A
project's own generation — a `generate.py` driving kibo 1.2 — moves to a `kibo.toml`, covered in
[kibo-project](kibo-project.md).

The list is measured, not remembered. A probe template that prints every scalar accessor of
every class of Template Model 1 is rendered by kibo 1.2, then migrated by the renames below and
rendered by kibo 2, on several models and for the `python` and `cpp` targets; every value that
differs must be one this page lists, or the check fails. It runs in the
[devkit-codegen-test](https://github.com/digital-substrate/devkit-codegen-test) laboratory as
`tools/template_model.py`.

## The method: a diff you can account for

A migration changes the names your templates read, and the values below change what some of
them return. So the test is a diff in which **every difference has a reason on this page**:

```sh
# before, with your current kibo
java -jar kibo-1.2.x.jar -c <target> -n <ns> -d model.dsm.json -t templates/ -o before/

# after, with kibo 2 and your migrated templates
java -jar kibo-2.0.2.jar -c <target> -n <ns> -d model.dsm.json -t templates/ -o after/

# every generated file names the jar that produced it, so that one line differs
diff -r -I 'by kibo-[0-9.]*\.jar' before/ after/
```

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

A template that reads an accessor the model does not carry renders the **empty string**. The
render succeeds, the file is written, and the missing part is simply absent. Kibo 2 reports
every such miss on stderr, each distinct one once with the number of times it fired:

```
kibo: templates/data.py.stg: context [/main /structure] 12:8 no such property or can't access: …
```

They are warnings: the file is still written and kibo still exits zero. During the migration a
line on stderr is a rename not yet done. **An empty stderr is not the end**: it says every
accessor resolves, not that every value is the one your templates expect — the diff says that —
nor that every name your templates build still designates a generated class.

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
accessor of Model 1 was removed or renamed. A mechanical rewrite covers all but the last row
(mind word boundaries: `pythonType` is a prefix of `pythonTupleType`).

**`members` replaces `pythonMembers`, and carries more.** A tuple or variant member is one
object describing all three spaces:

| Read | For |
|---|---|
| `.dsmType` | what the model calls the member — `uint8`, `Test::StructureS` |
| `.type` | the native spelling |
| `.bindingType` | the binding view: `.proxy`, `.useProxy`, `.type` |
| `.typeSuffix` | the neutral key naming the generated symbol |

So `<v.pythonMembers:{m|<m.type>}>` becomes `<v.members:{m|<m.bindingType.type>}>`.

## What reads differently

Each row is a change of value under the same accessor, after the renames. They are what the
diff shows; the last column says what a template does about it.

| # | Change | Example, Model 1 → Model 2 | In your templates |
|---|---|---|---|
| 1 | **A C++ type names its namespace in lower snake case**: `type`, `typeInNamespace`, `elementType`, `keyType`, a member's `type`, and the names in `membersInNamespace` and `strictDescendantsInNamespace` | `Demo::StructureS` → `demo::StructureS`; `ModelA::Material` → `model_a::Material` | A pack that declares the namespaces itself declares them in the same spelling: `namespace <u.name;format="lsc">`. The DSM spelling stays in `dsmType` and `namespace`. |
| 2 | **The untyped key lives in the infrastructure namespace**, the one `-n` names | `AnyConceptKey` → `::features::AnyConceptKey` | Declare `AnyConceptKey` in the namespace `-n` names, or read the name from the model rather than writing it. |
| 3 | **A parent from another namespace is named with its namespace** in `parentNameInNamespace` | `Thing` → `core::Thing` | Nothing, if you used it as a C++ name: Model 1 named a parent from another namespace as if it were local. |
| 4 | **An attachment's `representation` names a type of another namespace with its namespace** | `attachment<Material, string> Annotations::note` → `attachment<ModelA::Material, string> Annotations::note` | Nothing, unless you parse it. A type of the attachment's own namespace stays unqualified. |
| 5 | **A container class of a binding is named after what it holds**: `bindingType.proxy` and `bindingType.type` of a container | `Map_int8_to_string` → `Map_of_int8_to_string`; `Vec_uint8_2` → `Vec2_of_uint8`; `Mat_uint8_2_3` → `Mat2x3_of_uint8`; `Tuple_uint8_string` → `Tuple_of_uint8_and_string`; `Variant_A_B` → `Variant_of_A_or_B` | Name a container class from its `proxy`. A map's set of keys and an attachment's set of keys have their own binding type, `bindingKeySetType`. Where no accessor carries the class you need — the optional an attachment's `get` returns, the vector an xarray converts to — build it by the same rule: `Optional_of_<proxy>`, `Vector_of_<proxy>`. A name built by the 1.2 rule (`Set_<proxy>`, `Vector<elementTypeSuffix>`) points at a class that is no longer generated, and reads the same in both renders: see [Names you build yourself](#names-you-build-yourself). |
| 6 | **A concept's or a club's `bindingType.type` is its key class** | `Demo_ConceptA` → `Demo_ConceptAKey` | Every name you built from a concept's or a club's `bindingType.type` moves: where you appended `Key`, read `bindingType.type` alone; where you meant the entity's own name (a runtime id constant, say), read `bindingType.proxy`, which is unchanged. |
| 7 | **`any` is a proxy** | `bindingType.type` `dsviper.ValueAny` → `Any`; `useProxy` `false` → `true` | A pack that generates no `Any` class keeps a leaf table for it: test the type suffix `_any`, and write `dsviper.ValueAny` yourself. |
| 8 | **A set of keys is spelled as the DSM spells it** in `dsmType` | `set<Demo::ConceptA>` → `set<key<Demo::ConceptA>>` | Nothing, unless you parsed the old form. |
| 9 | **A binding accessor answers for the target being generated**, and a native target has no binding | under `-c cpp`, the `type` of `bindingType`, `bindingElementType` and `bindingKeyType`, `bindingSequenceType`, `bindingColumnType` and a member's `bindingType.type` are empty (`proxy` is not); Model 1 returned Python spellings there | Generate binding code with the binding's own target: `-c python` gives exactly what Model 1 gave under any target, apart from rows 5 to 7; `-c typescript` gives the TypeScript spellings (`bigint` for a 64-bit integer). |
| 10 | **Two lists changed order** | a namespace's `concepts` list a parent before its children (Model 1: by name); the container function lists (`optionalFunctions`, …) are sorted by their C++ type, so row 1 moves them | Nothing, unless the order of what you generate matters to you; then sort it yourself. |

Two additions are not changes: **structures and enumerations now carry `dsmType`**, as concepts
and clubs already did, and a member of a tuple or a variant carries it too.

## Does this affect your pack?

**A native target — C++ — is affected by rows 1 to 4, 8 and 10**, wherever it reads a type, a
parent name or a representation. Rows 1 and 2 are the ones a C++ pack meets first: the generated
namespaces are spelled in lower snake case, as the modules of the other bindings are.

**A delegating target — one that reaches the runtime through a binding and generates proxies —
is affected by every row.** Rows 5 to 7 change the names of the classes it generates and
refers to.

## Which space to name where

**In a type position** — a signature, an annotation, a declaration — use the target's spelling:
`bindingType.type`, or `bindingType.proxy` where you build a *name* rather than write a type.

**In a comment, a docstring, a `repr` or an exception message** — use `dsmType`. Every such
message in a generated file guards a runtime type comparison, and a runtime type is a DSM type;
the DSM name is what whoever wrote the model recognises, and it reads the same whatever the
target. Adopting it moves your generated output, so do it after the migration's diff is
accounted for, as its own change.

## Dropping your leaf table

If your pack carries a dictionary mapping DSM primitive names to your binding's spellings —
`int64` to `bigint`, `blob` to a runtime value class — Model 2 lets you delete it and read
`bindingType.type` instead, provided kibo knows your binding. Kibo 2 ships vocabularies for
`python` and `typescript`. If yours is neither, keep your table: `proxy` and `useProxy` still let
you resolve a leaf yourself. Either way, verify by the same diff.

## What Model 2 adds, without breaking anything

A Model 1 pack renders its whole model from `main(m)`, as before. Model 2 adds what a pack can
take up when it wants to:

- **Entries per scope**: `model(m)` once for the model, `unit(u)` once per DSM namespace,
  `pool(p)` and `attachment_pool(p)` once per pool. A namespace becomes a unit of generated
  code — a module, a header — with its dependencies, its include guard and its attachments
  grouped by the concept they are keyed on.
- **Formats** that carry a model's documentation into generated code (`string`, `docstring`,
  `comment`) and one snake_case rule for static names (`snake`, `usnake`).

The [Template Model reference](template_model.md) describes each.

## Checklist

1. Regenerate with your current kibo into `before/`.
2. Apply the renames, and rewrite `pythonMembers` to `members`.
3. Regenerate with kibo 2 into `after/`; read stderr until it is empty.
4. `diff -r -I 'by kibo-[0-9.]*\.jar' before/ after/`, and give each difference its row in
   [What reads differently](#what-reads-differently). Adapt your templates where the row says
   so; a difference with no row is a step done wrong.
5. Check the generated code for names it uses and does not define: the
   [names you build yourself](#names-you-build-yourself) do not show in the diff.
6. Only then take up `dsmType` in messages and comments, or drop your leaf table, each as its
   own change with its own diff.
