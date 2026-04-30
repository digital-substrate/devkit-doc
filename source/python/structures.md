# Structures and Enumerations

Structures and enumerations are user-defined types that require registration
with `Definitions` before use. This chapter covers creating and working with both.

## Creating Structures with Definitions

Structures are defined within a `Definitions` context:

```{doctest}
>>> from dsviper import *

>>> defs = Definitions()
>>> ns = NameSpace(ValueUUId("f529bc42-0618-4f54-a3fb-d55f95c5ad03"), "Tuto")
```

Define a structure with a descriptor:

```{doctest}
>>> desc = TypeStructureDescriptor("Login")
>>> desc.add_field("nickname", Type.STRING)
>>> desc.add_field("password", Type.STRING)

>>> t_login = defs.create_structure(ns, desc)
>>> t_login
Tuto::Login
```

## Instantiating Structures

Create structure instances with `Value.create()`. Default values use the
type's "zero":

```{doctest}
>>> login = Value.create(t_login)
>>> login
{nickname='', password=''}
```

Initialize from a dict:

```{doctest}
>>> login = Value.create(t_login, {"nickname": "zoop"})
>>> login
{nickname='zoop', password=''}
```

## Field Access

Access fields by name:

```{doctest}
>>> login.nickname
'zoop'

>>> login.password = "secret"
>>> login
{nickname='zoop', password='secret'}
```

### Type Checking

Field assignments are type-checked:

```{doctest}
>>> login.nickname = 42
Traceback (most recent call last):
    ...
dsviper.ViperError: ...expected type 'str', got 'int'...
```

## Default Values

Specify default values when defining fields:

```{doctest}
>>> desc = TypeStructureDescriptor("Config")
>>> desc.add_field("scale", ValueFloat(1.0))
>>> desc.add_field("items", Value.create(TypeVector(Type.INT64), [1, 2, 3]))

>>> t_config = defs.create_structure(ns, desc)
>>> Value.create(t_config)
{scale=1.0, items=[1, 2, 3]}
```

## Nested Structures

Structures can contain other structures:

```{doctest}
>>> desc_pos = TypeStructureDescriptor("Position")
>>> desc_pos.add_field("x", Type.FLOAT)
>>> desc_pos.add_field("y", Type.FLOAT)
>>> t_position = defs.create_structure(ns, desc_pos)

>>> desc_vertex = TypeStructureDescriptor("Vertex")
>>> desc_vertex.add_field("position", t_position)
>>> desc_vertex.add_field("label", Type.STRING)
>>> t_vertex = defs.create_structure(ns, desc_vertex)

>>> vertex = Value.create(t_vertex)
>>> vertex
{position={x=0.0, y=0.0}, label=''}
```

Mutate a nested field:

```{doctest}
>>> vertex.position.x = 10.0
>>> vertex.position.y = 20.0
>>> vertex.label = "A"
>>> vertex
{position={x=10.0, y=20.0}, label='A'}
```

## Paths

A `Path` locates a piece of information within a value:

```{doctest}
>>> p = Path.from_field("nickname").const()
>>> p
.nickname
```

Apply a path to read or write the targeted field:

```{doctest}
>>> p.at(login)
'zoop'

>>> p.set(login, "new_nick")
>>> login.nickname
'new_nick'
```

### Complex Paths

Paths can traverse nested structures:

```{doctest}
>>> p = Path.from_field("position").field("x").const()
>>> p
.position.x

>>> p.at(vertex)
10.0
>>> p.set(vertex, 15.0)
```

### Path Components

Paths can include:

- Field access: `.field("name")`
- Index access: `.index(0)`
- Unwrap: `.unwrap()`
- Map key: `.key(key_value)`

```{doctest}
>>> p = Path.from_field("items").index(0).const()
>>> p
.items[0]

>>> p.components()
[{type: Field, value: 'items':string}, {type: Index, value: 0:uint64}]
```

## Enumerations

Enumerations are types with a fixed set of named cases.

### Defining an Enumeration

```{doctest}
>>> desc = TypeEnumerationDescriptor("Status", documentation="Task status")
>>> desc.add_case("pending", "Waiting to start")
>>> desc.add_case("active", "In progress")
>>> desc.add_case("completed", "Finished")

>>> t_status = defs.create_enumeration(ns, desc)
>>> t_status
Tuto::Status
```

### Creating Enumeration Values

By case name (most common):

```{doctest}
>>> status = ValueEnumeration(t_status, "active")
>>> status.name()
'active'
```

By index (0-based):

```{doctest}
>>> status = ValueEnumeration(t_status, 0)
>>> status.name()
'pending'
```

Default (first case):

```{doctest}
>>> Value.create(t_status)
.pending
```

Specify case with `Value.create()`:

```{doctest}
>>> Value.create(t_status, "completed")
.completed
```

### Properties

```{doctest}
>>> status = ValueEnumeration(t_status, "active")

>>> status.name()
'active'

>>> status.index()
1

>>> status.type_enumeration()
Tuto::Status
```

### Type Introspection

Query available cases from the type:

```{doctest}
>>> cases = t_status.cases()
>>> [c.name() for c in cases]
['pending', 'active', 'completed']
```

Query a case by name:

```{doctest}
>>> case = t_status.query("active")
>>> case.documentation()
'In progress'
```

Check existence (raises on invalid):

```{doctest}
>>> t_status.check("unknown")
Traceback (most recent call last):
    ...
dsviper.ViperError: ...the case unknown is not defined for enum Tuto::Status...
```

### Comparison

Enumerations compare lexicographically by name, not by index:

```{doctest}
>>> pending = ValueEnumeration(t_status, "pending")
>>> active = ValueEnumeration(t_status, "active")

>>> active < pending
True
```

### Constraints

- Maximum 256 cases per enumeration (uint8 index)
- Case names must be unique within an enumeration
- Empty enumerations are not allowed

## Type Information

Introspect structure types. Field reprs include the field type:

```{doctest}
>>> t_login.fields()
[nickname:string, password:string]

>>> field = t_login.fields()[0]
>>> field.name()
'nickname'
>>> field.type()
string
```

## Using Structures with Databases

Structures are typically stored via attachments. See [DSM](dsm.md)
for defining attachments and [Database](database.md) for persistence patterns.

```{note}
The "Quick preview" snippet below depends on a DSM model compiled by Kibo
(`TUTO_A_USER_LOGIN` is generated). It is illustrative — see the
[Tutorial](tutorial.md) for a self-contained working example.
```

```pycon
# With DSM definitions loaded
>>> key = TUTO_A_USER_LOGIN.create_key()
>>> login = TUTO_A_USER_LOGIN.create_document()
>>> login.nickname = "alice"

# Store in database
>>> db.set(TUTO_A_USER_LOGIN, key, login)
```

## What's Next

- [DSM](dsm.md) - Define data models with attachments
- [Database](database.md) - Persisting structures
- [Serialization](serialization.md) - JSON and binary encoding
