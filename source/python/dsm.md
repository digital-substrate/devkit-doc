# DSM Processing

This chapter covers loading and processing DSM (Digital Substrate Model) files in Python.

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
['Tuto::Identity', 'Tuto::Login', 'Tuto::Texture', 'Tuto::Thumbnail']

>>> dsm_defs.enumerations()
[Tuto::Status]

>>> sorted(str(a).split()[-1] for a in dsm_defs.attachments())
['Tuto::avatar', 'Tuto::identity', 'Tuto::login', 'Tuto::portrait']
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

### DSMAttachment

Inspect attachment definitions. `identifier()` returns the fully qualified
name `<concept>.<attachment>`:

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

### Inject Constants

`defs.inject()` makes generated constants available in the namespace.
The `Tuto` constants are already in scope thanks to the doctest fixture:

```{doctest}
>>> TUTO_S_LOGIN
Tuto::Login

>>> TUTO_A_USER_LOGIN
attachment<User, Login> Tuto::login
```

**Naming convention**: Constants follow the pattern `{NAMESPACE}_{KIND}_{NAME}`:

| Kind        | Prefix | Example                 | Description      |
|-------------|--------|-------------------------|------------------|
| Attachment  | `_A_`  | `TUTO_A_USER_LOGIN`     | Attachment type  |
| Structure   | `_S_`  | `TUTO_S_LOGIN`          | Structure type   |
| Enumeration | `_E_`  | `TUTO_E_STATUS`         | Enumeration type |
| Concept     | `_C_`  | `TUTO_C_USER`           | Concept type     |
| Path        | `_P_`  | `TUTO_P_LOGIN_NICKNAME` | Path to field    |

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

### Binary (DSMB)

```{doctest}
>>> blob = dsm_defs.encode()
>>> blob
blob(...)

>>> restored = DSMDefinitions.decode(blob)
>>> type(restored).__name__
'DSMDefinitions'
```

### JSON

```{doctest}
>>> json_str = dsm_defs.json_encode()
>>> 'concepts' in json_str and 'attachments' in json_str
True

>>> restored = DSMDefinitions.json_decode(json_str)
>>> type(restored).__name__
'DSMDefinitions'
```

## What's Next

- [Tutorial](tutorial.md) - Complete workflow using DSM with CommitDatabase
- [Database](database.md) - Persistence with Database and CommitDatabase
- [Serialization](serialization.md) - Binary and JSON encoding
