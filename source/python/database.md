# Database

Viper provides two database types for persistence:

| Type             | Use Case                 | History   |
|------------------|--------------------------|-----------|
| `Database`       | Simple key-value storage | No        |
| `CommitDatabase` | Versioned data           | Yes (DAG) |

This page covers the simple `Database`. For versioned storage,
see [CommitDatabase](commit.md).

---

## Creating a Database

```pycon
>>> from dsviper import *

# Create in memory
>>> db = Database.create_in_memory()

# Create on disk
>>> db = Database.create("data.vdb")

# Create with documentation metadata
>>> db = Database.create("data.vdb", documentation="Cache for processed meshes")

# Open existing
>>> db = Database.open("data.vdb")

# Open in read-only mode
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
# List available databases on a server
>>> Database.databases("server.local")
['cache', 'index']

# Connect to a remote database
>>> db = Database.connect("cache", "server.local")

# Unix socket connection
>>> db = Database.connect_local("cache", "/tmp/project.sock")
```

See [Server](../tools/server.md) for deployment details.

---

## Setting Up Definitions

```pycon
# Load definitions from DSM
>>> builder = DSMBuilder.assemble("model.dsm")
>>> report, dsm_defs, defs = builder.parse()

# Extend database with definitions
>>> db.extend_definitions(defs)
>>> defs.inject()
```

---

## CRUD Operations

```pycon
# Create
>>> key = TUTO_A_USER_LOGIN.create_key()
>>> login = TUTO_A_USER_LOGIN.create_document()
>>> login.nickname = "alice"

# Write (requires transaction)
>>> db.begin_transaction()
>>> db.set(TUTO_A_USER_LOGIN, key, login)
>>> db.commit()

# Read
>>> result = db.get(TUTO_A_USER_LOGIN, key)
>>> result.unwrap()
{nickname='alice', password=''}

# Check existence
>>> db.has(TUTO_A_USER_LOGIN, key)
True

# Update
>>> db.begin_transaction()
>>> login.password = "secret"
>>> db.set(TUTO_A_USER_LOGIN, key, login)
>>> db.commit()

# Delete
>>> db.begin_transaction()
>>> db.delete(TUTO_A_USER_LOGIN, key)
>>> db.commit()

# List all keys
>>> db.keys(TUTO_A_USER_LOGIN)
[key1, key2, ...]
```

---

## Transactions

All write operations require a transaction:

```pycon
>>> db.begin_transaction()
>>> # ... mutations ...
>>> db.commit()      # Apply changes

# Or rollback
>>> db.begin_transaction()
>>> # ... mutations ...
>>> db.rollback()    # Discard changes
```

**Safe transaction pattern** - Always use try/finally to ensure cleanup:

```python
db.begin_transaction()
try:
    db.set(attachment, key, document)
    db.commit()
except ViperError:
    db.rollback()
    raise
```

You can check transaction state with `in_transaction()`:

```pycon
>>> db.in_transaction()
False
>>> db.begin_transaction()
>>> db.in_transaction()
True
```

---

## Lifecycle

Always close a database when done, especially for on-disk databases:

```pycon
>>> db.close()
>>> db.is_closed()
True
```

---

## Metadata

```pycon
>>> db.path()
'/path/to/data.vdb'

>>> db.in_memory()
False

>>> db.uuid()
{a1b2c3d4-...}

>>> db.documentation()
'Cache for processed meshes'

>>> db.codec_name()
'StreamBinary'
```

---

## Choosing Between Database and CommitDatabase

| Feature              | Database             | CommitDatabase   |
|----------------------|----------------------|------------------|
| Simple CRUD          | ✓                    | ✓                |
| History              | ✗                    | ✓                |
| Sync                 | ✗                    | ✓                |
| Embedded definitions | ✓                    | ✓                |
| Remote access        | ✓                    | ✓                |
| Blob storage         | ✓                    | ✓                |

---

## What's Next

- [CommitDatabase](commit.md) - Versioned database with history
- [Blobs](blobs.md) - Binary data storage
