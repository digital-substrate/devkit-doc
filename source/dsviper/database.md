# Database

Viper C++ provides two database types for persistence:

| Type             | Use Case                 | History   |
|------------------|--------------------------|-----------|
| `Database`       | Simple key-value storage | No        |
| `CommitDatabase` | Versioned data           | Yes (DAG) |

This page covers the simple `Database`. For versioned storage,
see [CommitDatabase](../commit/commit.md).

---

## Creating a Database

In-memory and on-disk variants:

```{doctest}
>>> db = Database.create_in_memory()
>>> db.in_memory()
True
```

```pycon
>>> db = Database.create("data.vdb")

>>> db = Database.create("data.vdb", documentation="Cache for processed meshes")

>>> db = Database.open("data.vdb")

>>> db = Database.open("data.vdb", readonly=True)
```

Before opening, you can check if a file is a valid Database:

```pycon
>>> Database.is_compatible("data.vdb")
True
```

---

## Remote Access

Database supports network access through a server:

```pycon
>>> Database.databases("server.local")
['cache', 'index']

>>> db = Database.connect("cache", "server.local")

>>> db = Database.connect_local("cache", "/tmp/project.sock")
```

See [Server](../dsviper-tools/server.md) for deployment details.

---

## Setting Up Definitions

```{doctest}
>>> _ = db.extend_definitions(_tuto_defs)
>>> sorted(str(a).split()[-1] for a in db.definitions().attachments())
['Tuto::account', 'Tuto::avatar', 'Tuto::identity', 'Tuto::login', 'Tuto::portrait']
```

In your own code you would assemble definitions from your DSM model:

```pycon
>>> builder = DSMBuilder.assemble("model.dsm")
>>> report, dsm_defs, defs = builder.parse()
>>> db.extend_definitions(defs)
>>> defs.inject()
```

---

## CRUD Operations

Create a key and a document:

```{doctest}
>>> key = TUTO_A_USER_LOGIN.create_key()
>>> login = TUTO_A_USER_LOGIN.create_document()
>>> login.nickname = "alice"
```

Write — all mutations require a transaction:

```{doctest}
>>> db.begin_transaction()
>>> _ = db.set(TUTO_A_USER_LOGIN, key, login)
>>> db.commit()
```

Read:

```{doctest}
>>> result = db.get(TUTO_A_USER_LOGIN, key)
>>> result.unwrap()
{nickname='alice', password=''}
```

Check existence:

```{doctest}
>>> db.has(TUTO_A_USER_LOGIN, key)
True
```

Update:

```{doctest}
>>> db.begin_transaction()
>>> login.password = "secret"
>>> _ = db.set(TUTO_A_USER_LOGIN, key, login)
>>> db.commit()

>>> db.get(TUTO_A_USER_LOGIN, key).unwrap()
{nickname='alice', password='secret'}
```

List keys for an attachment — `keys()` returns a `ValueSet` of `ValueUUId`:

```{doctest}
>>> isinstance(db.keys(TUTO_A_USER_LOGIN), ValueSet)
True
>>> len(db.keys(TUTO_A_USER_LOGIN))
1
```

Delete:

```{doctest}
>>> db.begin_transaction()
>>> _ = db.delete(TUTO_A_USER_LOGIN, key)
>>> db.commit()

>>> db.has(TUTO_A_USER_LOGIN, key)
False
```

---

## Transactions

All write operations require a transaction:

```{doctest}
>>> db.begin_transaction()
>>> db.in_transaction()
True
>>> db.commit()
>>> db.in_transaction()
False
```

A transaction can also be rolled back:

```{doctest}
>>> db.begin_transaction()
>>> _ = db.set(TUTO_A_USER_LOGIN, key, login)
>>> db.rollback()
>>> db.has(TUTO_A_USER_LOGIN, key)
False
```

**Safe transaction pattern** — use try/finally to ensure cleanup:

```python
db.begin_transaction()
try:
    db.set(attachment, key, document)
    db.commit()
except ViperError:
    db.rollback()
    raise
```

---

## Lifecycle

Always close a database when done, especially for on-disk databases:

```{doctest}
>>> tmp_db = Database.create_in_memory()
>>> tmp_db.close()
>>> tmp_db.is_closed()
True
```

---

## Metadata

`Database` exposes a few metadata accessors:

```{doctest}
>>> db.in_memory()
True
>>> db.path()
'InMemory'
>>> isinstance(db.uuid(), ValueUUId)
True
>>> db.codec_name()
'StreamBinary'
```

For an on-disk database, `path()` returns the file path and `documentation()`
returns the string passed to `Database.create(..., documentation=...)`.

