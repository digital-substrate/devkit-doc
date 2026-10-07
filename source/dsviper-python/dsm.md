# DSM Processing

This chapter covers loading and processing DSM (Digital Substrate Model) files in Python.

```{note}
This page is about *processing* a model from Python. The DSM language
itself — its syntax, its types, its doc comments — is
{doc}`its own chapter <../dsm/introduction>`, and two complete models are
published in full: the {doc}`Graph Editor <../dsm/samples/graph_editor>`
and the {doc}`Raptor Editor <../dsm/samples/raptor_editor>`. Neither page
assumes you have read this one.
```

## The DSM Workflow

Processing DSM files follows three steps:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  assemble   │ ──► │    parse    │ ──► │  introspect │
│  (.dsm)     │     │  (validate) │     │   (visit)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Step 1: Assemble

`DSMBuilder.assemble()` reads DSM files. The path can be a single `.dsm`
file or a directory containing `.dsm` files; in the directory case, every
file is concatenated and parsed as a single unit. The doctests below reuse
the bundled `Tuto` fixture builder pre-loaded by the test harness:

```{doctest}
>>> builder = _builder
>>> [p.source().split('/')[-1] for p in builder.parts()]
['model.dsm']
```

In production code you would assemble from your own paths:

```pycon
>>> builder = DSMBuilder.assemble("model.dsm")

>>> builder = DSMBuilder.assemble("models")

>>> for part in builder.parts():
...     print(part.source())
```

## Step 2: Parse

`parse()` validates syntax and semantics, returning three values:

```{doctest}
>>> report, dsm_defs, defs = builder.parse()
>>> report.has_error()
False
>>> type(dsm_defs).__name__
'DSMDefinitions'
>>> type(defs).__name__
'DefinitionsConst'
```

| Return Value | Type               | Description                             |
|--------------|--------------------|-----------------------------------------|
| `report`     | `DSMParseReport`   | Errors and warnings                     |
| `dsm_defs`   | `DSMDefinitions`   | Structured DSM data (or None if errors) |
| `defs`       | `DefinitionsConst` | Runtime definitions (or None if errors) |

### Handling Errors

```pycon
>>> report, dsm_defs, defs = builder.parse()
>>> if report.has_error():
...     for error in report.errors():
...         print(f"{error.source()}:{error.line()}: {error.message()}")
... else:
...     print("Parse successful!")
```

## Step 3: DSM Introspection

`DSMDefinitions` provides structured access to inspect the parsed model.

### DSMDefinitions

The root container for all DSM elements:

```{doctest}
>>> dsm_defs.concepts()
[Tuto::User]

>>> sorted(str(s) for s in dsm_defs.structures())
['Tuto::Account', 'Tuto::Identity', 'Tuto::Login', 'Tuto::Texture', 'Tuto::Thumbnail']

>>> dsm_defs.enumerations()
[Tuto::Status]

>>> sorted(str(a).split()[-1] for a in dsm_defs.attachments())
['Tuto::account', 'Tuto::avatar', 'Tuto::identity', 'Tuto::login', 'Tuto::portrait']
```

### DSMConcept

Inspect concept definitions:

```{doctest}
>>> concept = dsm_defs.concepts()[0]
>>> concept.type_name()
Tuto::User

>>> isinstance(concept.runtime_id(), ValueUUId)
True

>>> concept.documentation()
'A user.'

>>> concept.parent() is None
True
```

For a model with concept inheritance, `parent()` returns the parent concept,
e.g. `Tuto::Admin`.

### DSMStructure

Inspect structure definitions and their fields:

```{doctest}
>>> struct = [s for s in dsm_defs.structures() if str(s.type_name()) == 'Tuto::Login'][0]
>>> struct.type_name()
Tuto::Login

>>> [(f.name(), str(f.type())) for f in struct.fields()]
[('nickname', 'string'), ('password', 'string')]

>>> struct.fields()[0].documentation()
''
```

### DSMEnumeration

Inspect enumeration definitions and their cases:

```{doctest}
>>> enum = dsm_defs.enumerations()[0]
>>> enum.type_name()
Tuto::Status

>>> [case.name() for case in enum.members()]
['pending', 'active', 'completed']
```

The Tuto fixture ties `Status` into a struct used by the `account`
attachment, so the enum can be exercised end-to-end through the runtime:

```{doctest}
>>> account = Tuto.attachments.User.account.create_document()
>>> account
{state=.pending}

>>> account.state = ValueEnumeration(Tuto.Status, "active")
>>> account
{state=.active}
```

### DSMAttachment

Inspect attachment definitions. `identifier()` returns the attachment's
namespace, its key written relative to that namespace, and its name — unique
among the attachments. Here `Tuto::User.login`; an attachment `login` that
namespace `App` declares on `Tuto::User` is `App::Tuto::User.login`:

```{doctest}
>>> att = dsm_defs.attachments()[0]
>>> att.identifier()
'Tuto::User.login'

>>> att.key_type()
Tuto::User

>>> att.document_type()
Tuto::Login
```

### Generate DSM Text

Reconstruct DSM source from definitions. The output groups types by
attachment and adds explanatory comments:

```{doctest}
>>> source = dsm_defs.to_dsm()
>>> 'namespace Tuto' in source and 'concept User' in source
True
>>> 'attachment<User, Login> login' in source
True
```

Pass `show_runtime_id=True` to append runtime IDs.

## Using Runtime Definitions

The `DefinitionsConst` from parse enables runtime operations.

### Inject the Namespace

`defs.inject()` binds one object per namespace of the definitions, under the
namespace's own name: its types, and three views — `keys`, `attachments` by
key concept, `paths` by structure. `Tuto` is already in scope thanks to the
doctest fixture:

```{doctest}
>>> Tuto.Login
Tuto::Login

>>> Tuto.attachments.User.login
attachment<User, Login> Tuto::login
```

**Layout**: every name is the definitions' own, as they write it.

| Reached as                              | Example                       | What                         |
|-----------------------------------------|-------------------------------|------------------------------|
| `<Namespace>.<Type>`                    | `Tuto.User`, `Tuto.Login`     | a concept, club, structure or enumeration |
| `<Namespace>.keys.<Concept>`            | `Tuto.keys.User`              | the key type of a concept or club |
| `<Namespace>.attachments.<Key>.<name>`  | `Tuto.attachments.User.login` | an attachment, by key concept then name |
| `<Namespace>.paths.<Structure>.<field>` | `Tuto.paths.Login.nickname`   | the path to a field          |

A key concept of another namespace takes that namespace in front:
`App.attachments.Lib_User.profile`. A name the target already binds to
something else is refused, and nothing is bound; `discard()` removes what
`inject()` bound.

### Query Types

```{doctest}
>>> types = defs.query_types("Login")
>>> types
[Tuto::Login]
>>> Value.create(types[0])
{nickname='', password=''}
```

### Access Attachments

```pycon
>>> for att in defs.attachments():
...     print(att.description())
```

## Serialization

DSMDefinitions can be serialized for distribution.

### JSON (`.dsm.json`)

The canonical on-disk form consumed by Kibo and `dsm_util`:

```{doctest}
>>> json_str = dsm_defs.json_encode()
>>> 'concepts' in json_str and 'attachments' in json_str
True

>>> restored = DSMDefinitions.json_decode(json_str)
>>> type(restored).__name__
'DSMDefinitions'
```

### Binary blob

A compact in-memory representation, mainly used to embed definitions into a
C++ resource header (via `blob.embed("definitions")`):

```{doctest}
>>> blob = dsm_defs.encode()
>>> blob
blob(...)

>>> restored = DSMDefinitions.decode(blob)
>>> type(restored).__name__
'DSMDefinitions'
```

