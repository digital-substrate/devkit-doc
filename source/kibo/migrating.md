# Migrating a template pack from Template Model 1 to Template Model 2

Template Model 2 ships with kibo 2. It renames the accessors that describe a type **as the
binding sees it**, and removes the ones that spelled a type for one particular language inside
the generator. There are no compatibility aliases: a pack written against Model 1 does not
render against kibo 2 until it is migrated.

This page is the complete list of what moved, and the rule that tells you when you are done. A
project's own generation — a `generate.py` driving kibo 1.2 — moves to a `kibo.toml`, covered
in [kibo-project](kibo-project.md).

## The rule that makes this safe

**A Template Model migration does not change what your templates emit.** It changes the names
they read. So the test is a fixed point:

```sh
# before, with your current kibo
java -jar kibo-1.2.x.jar -c <target> -n <ns> -d model.dsm.json -t templates/ -o before/

# after, with kibo 2 and your migrated templates
java -jar kibo-2.0.0.jar -c <target> -n <ns> -d model.dsm.json -t templates/ -o after/

# every generated file names the jar that produced it, so that one line differs
diff -r -I 'by kibo-[0-9.]*\.jar' before/ after/     # must be empty
```

An empty diff means the migration is complete and correct. **A non-empty diff means the
migration is wrong**, not that the generator changed its mind: every rename below maps one to
one onto a name that returns the same string for the same target. Run it on the largest model
you have; a small model does not reach every accessor.

If your pack stamps its own version into what it generates, hold that stamp fixed for the
comparison, or ignore its line the same way. If you also want to take up something Model 2
makes possible — dropping a leaf table, say — do it as a second change, after the fixed point
holds; otherwise a diff tells you two things at once.

## First: read the diagnostics

A template that reads an accessor the model does not carry renders the **empty string**. The
render succeeds, the file is written, and the missing part is simply absent. Kibo 2 reports
every such miss on stderr, each distinct one once with the number of times it fired:

```
kibo: templates/data.py.stg: context [/main /structure] 12:8 no such property or can't access: …
```

They are warnings: the file is still written and kibo still exits zero. **A clean render
prints nothing.** During the migration, treat any line on stderr as a step not yet done.

## Does this affect your pack?

**A native target — C++ — is not affected.** Nothing it reads changed: `type`,
`typeInNamespace`, `elementType`, `keyType`, `passBy`, `isMovable`, `valueRef`,
`defaultValue`, the `*InNamespace` family, `viperValue`, `viperType`, `dsmType`, `typeSuffix`,
names, runtime ids, documentation. A C++ pack migrates with zero edits and an empty diff,
which was checked on a third-party C++ pack rendered against a large model by kibo 1.2.11 and
by kibo 2.0.0: the two outputs differ only in the generator banner.

**A delegating target — one that reaches the runtime through a binding and generates
proxies — is affected.** Everything below applies to it.

## The renames

One to one. Each returns the same string as before, for the same target.

| Model 1 | Model 2 | On |
|---|---|---|
| `pythonType` | `bindingType` | the classes that describe a type: concepts, clubs, enumerations, structures, structure fields, function parameters, attached key and document types, and the nine container functions |
| `pythonElementType` | `bindingElementType` | `vec`, `mat`, `optional`, `vector`, `set`, `map`, `xarray` functions, and `TemplateField` |
| `pythonKeyType` | `bindingKeyType` | `map` functions and `TemplateField` |
| `returnPythonType` | `returnBindingType` | functions and attachment functions |
| `pythonTupleType` | `bindingSequenceType` | `vec` and `mat` functions |
| `pythonColumnType` | `bindingColumnType` | `mat` functions |
| `pythonMembers` | `members` — see below | `tuple` and `variant` functions |

The members of the object itself are unchanged: `proxy`, `useProxy`, `typeSuffix`, `type`. A
mechanical rewrite covers all but the last row. Do it, run the fixed point, and read stderr.

## Three changes that are not renames

**`bindingType.type` answers for the target you are generating.** In Model 1 the scalar
`type` returned a Python spelling whatever the target: `int`, `str`, `None`,
`dsviper.ValueBlob`. In Model 2 it returns the spelling of the binding `--converter` names —
`int` under `python`, `bigint` under `typescript` for the same 64-bit integer. If you generate
with `-c python`, you get exactly what you got before and the fixed point holds.

**`members` replaces `pythonMembers`, and carries more.** A tuple or variant member is now one
object describing all three spaces:

| Read | For |
|---|---|
| `.dsmType` | what the model calls the member — `uint8`, `Test::StructureS` |
| `.type` | the native spelling |
| `.bindingType` | the binding view: `.proxy`, `.useProxy`, `.type` |
| `.typeSuffix` | the neutral key naming the generated symbol |

So `<v.pythonMembers:{m|<m.type>}>` becomes `<v.members:{m|<m.bindingType.type>}>`, and a
member's own name for a message or a comment is `<m.dsmType>`.

**Entities carry `dsmType`.** A concept, a club, an enumeration and a structure answer
`dsmType` with the name the model gives them — `Test::ConceptA`, not the target's spelling of
it. This is additive: nothing requires you to use it.

## Which space to name where

**In a type position** — a signature, an annotation, a declaration — use the target's
spelling: `bindingType.type`, or `bindingType.proxy` where you build a *name* rather than
write a type.

**In a comment, a docstring, a `repr` or an exception message** — use `dsmType`. Every such
message in a generated file guards a runtime type comparison, and a runtime type is a DSM
type; the DSM name is what whoever wrote the model recognises, and it reads the same whatever
the target. Adopting this moves your generated output, so do it after the fixed point holds,
as its own change.

## Dropping your leaf table

If your pack carries a dictionary mapping DSM primitive names to your binding's spellings —
`int64` to `bigint`, `blob` to a runtime value class — Model 2 lets you delete it and read
`bindingType.type` instead, provided kibo knows your binding. Kibo 2 ships vocabularies for
`python` and `typescript`. If yours is neither, keep your table: `proxy` and `useProxy` still
let you resolve a leaf yourself. Either way, verify by the same fixed point.

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
2. Apply the renames in the table.
3. Rewrite `pythonMembers` to `members`, reading `.bindingType.type` where you read `.type`.
4. Regenerate with kibo 2 into `after/`.
5. `diff -r before/ after/` — empty.
6. stderr — empty.
7. Only then take up `dsmType` in messages and comments, or drop your leaf table, each as its
   own change with its own diff.
