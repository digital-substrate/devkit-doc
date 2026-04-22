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

`DSMBuilder.assemble()` reads DSM files:

```pycon
>>> from dsviper import *

# Assemble a single file
>>> builder = DSMBuilder.assemble("model.dsm")

# Assemble all .dsm files in a directory
>>> builder = DSMBuilder.assemble("models")

# View assembled parts
>>> for part in builder.parts():
...     print(part.source())
```

If the path is a directory, all `.dsm` files are assembled together and parsed as a single
unit.

## Step 2: Parse

`parse()` validates syntax and semantics, returning three values:

```pycon
>>> report, dsm_defs, defs = builder.parse()
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
    ...
for error in report.errors():
    ...
print(f"{error.source()}:{error.line()}: {error.message()}")
... else:
...
print("Parse successful!")
```

## Step 3: DSM Introspection

`DSMDefinitions` provides structured access to inspect the parsed model.

### DSMDefinitions

The root container for all DSM elements:

```pycon
>>> dsm_defs.concepts()
[Tuto::User]

>>> dsm_defs.structures()
[Tuto::Login, Tuto::Identity]

>>> dsm_defs.enumerations()
[Tuto::Status]

>>> dsm_defs.attachments()
[attachment<User, Login> Tuto::login, attachment<User, Identity> Tuto::identity]
```

### DSMConcept

Inspect concept definitions:

```pycon
>>> concept = dsm_defs.concepts()[0]
>>> concept.type_name()
Tuto::User

>>> concept.runtime_id()
'a1b2c3d4-...'

>>> concept.documentation()
'A user in the system.'

>>> concept.parent()  # None if no parent
Tuto::Admin
```

### DSMStructure

Inspect structure definitions and their fields:

```pycon
>>> struct = dsm_defs.structures()[0]
>>> struct.type_name()
Tuto::Login

>>> for field in struct.fields():
    ...
print(f"{field.name()}: {field.type()}")
nickname: string
password: string

>>> field = struct.fields()[0]
>>> field.documentation()
'The user display name.'
>>> field.default_value()
''
```

### DSMEnumeration

Inspect enumeration definitions:

```pycon
>>> enum = dsm_defs.enumerations()[0]
>>> enum.type_name()
Tuto::Status

>>> for case in enum.members():
    ...
print(case.name())
pending
active
completed
```

### DSMAttachment

Inspect attachment definitions:

```pycon
>>> att = dsm_defs.attachments()[0]
>>> att.identifier()
'login'

>>> att.key_type()
Tuto::User

>>> att.document_type()
Tuto::Login
```

### Generate DSM Text

Reconstruct DSM source from definitions:

```pycon
>>> print(dsm_defs.to_dsm())
namespace Tuto {f529bc42-a399-415c-baf0-db42949d2ba2} {
    concept User;
    struct Login {
        string nickname;
        string password;
    };
    attachment<User, Login> login;
};
```

Pass `show_runtime_id=True` to append runtime IDs.

## Using Runtime Definitions

The `DefinitionsConst` from parse enables runtime operations:

### Inject Constants

```pycon
>>> defs.inject()

# Constants are now available
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

```pycon
>>> types = defs.query_types("Login")
>>> t_login = types[0]
>>> Value.create(t_login)
{nickname = '', password = ''}
```

### Access Attachments

```pycon
>>> for att in defs.attachments():
    ...
print(att.description())
```

## Serialization

DSMDefinitions can be serialized for distribution:

### Binary (DSMB)

```pycon
# Encode
>>> blob = dsm_defs.encode()

# Decode
>>> dsm_defs = DSMDefinitions.decode(blob)
```

### JSON

```pycon
# Encode
>>> json_str = dsm_defs.json_encode()

# Decode
>>> dsm_defs = DSMDefinitions.json_decode(json_str)
```

## What's Next

- [Tutorial](tutorial.md) - Complete workflow using DSM with CommitDatabase
- [Database](database.md) - Persistence with Database and CommitDatabase
- [Serialization](serialization.md) - Binary and JSON encoding
