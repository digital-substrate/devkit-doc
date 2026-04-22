# Commit System

The commit system provides transactional persistence with history tracking.

**When to use**: Use `CommitDatabase` for versioned persistence with history, concurrent
streams, and sync. Every change creates a commit, enabling undo/redo and concurrent editing.

---

## CommitDatabase

`CommitDatabase` provides versioned data storage:

- History is preserved as a DAG of commits
- You can read from any point in history

```{important}
**The Dual-Layer Contract**

CommitDatabase guarantees **structural integrity** (deterministic merge, DAG consistency)
but NOT **semantic integrity**. When concurrent streams converge, mutations are applied automatically
without checking business rules—mutations on non-existent documents or unresolved paths are silently ignored.

Your application must validate data when consuming state. The validation cost scales
with your data model complexity and business rules, not with Viper.

See [The Dual-Layer Contract](../concepts/commit_contract.md) for details.
```

---

## Opening a CommitDatabase

```pycon
# Open existing database
>>> db = CommitDatabase.open("model.cdb")

# Create new database (with embedded definitions)
# Use: python3 tools/dsm_util.py create_commit_database model.dsm model.cdb
```

---

## Reading State

Get a read-only state from any commit:

```pycon
# State at last commit
>>> state = db.state(db.last_commit_id())

# State at first commit
>>> state = db.state(db.first_commit_id())

# Initial state (before any commits)
>>> state = db.initial_state()
```

### AttachmentGetting Interface

Read attachments via `attachment_getting()`:

```pycon
>>> getting = state.attachment_getting()

# Get a document
>>> doc = getting.get(attachment, key)
>>> doc
Optional({...})

# Get all keys
>>> keys = getting.keys(attachment)
```

---

## Mutations

Create a mutable state and apply changes:

```pycon
>>> mutable_state = CommitMutableState(db.state(db.last_commit_id()))
>>> mutating = mutable_state.attachment_mutating()

# Set a document
>>> mutating.set(attachment, key, document)

# Update a field (path-based)
>>> mutating.update(attachment, key, path, new_value)
```

> **Note**: CommitDatabase tracks history via mutations from CommitMutableState.

### Committing

Commit mutations to the database:

```pycon
>>> commit_id = db.commit_mutations("Commit message", mutable_state)
>>> commit_id
'87b2b1d275f0ac3b2389b18f58d7abe0214c2493'
```

---

## Complete Example

```pycon
>>> from dsviper import *

# Open database and inject definitions
>>> db = CommitDatabase.open("model.cdb")
>>> db.definitions().inject()

# Create a new key and document
>>> key = TUTO_A_USER_LOGIN.create_key()
>>> login = TUTO_A_USER_LOGIN.create_document()
>>> login.nickname = "alice"
>>> login.password = "secret"

# Commit the document
>>> mutable = CommitMutableState(db.state(db.last_commit_id()))
>>> mutable.attachment_mutating().set(TUTO_A_USER_LOGIN, key, login)
>>> db.commit_mutations("Add Alice", mutable)

# Read it back
>>> state = db.state(db.last_commit_id())
>>> state.attachment_getting().get(TUTO_A_USER_LOGIN, key)
Optional({nickname='alice', password='secret'})
```

---

## Path-Based Mutators

Instead of replacing entire documents with `set()`, path-based mutators use
**Paths** to target specific locations. This enables path-based merging when multiple
users edit concurrently.

| Mutator            | Target | Operation             |
|--------------------|--------|-----------------------|
| `update`           | Field  | Replace value at path |
| `union_in_set`     | Set    | Add elements          |
| `subtract_in_set`  | Set    | Remove elements       |
| `union_in_map`     | Map    | Add key-value pairs   |
| `subtract_in_map`  | Map    | Remove keys           |
| `update_in_map`    | Map    | Update existing key   |
| `insert_in_xarray` | XArray | Insert at position    |
| `update_in_xarray` | XArray | Update at position    |
| `remove_in_xarray` | XArray | Remove at position    |

### Field Update

```pycon
>>> mutating.update(
    ...
TUTO_A_USER_LOGIN, key,
...
TUTO_P_LOGIN_NICKNAME, "alice_updated"
... )
```

### Set Operations

```pycon
# Add elements to a set field
>>> mutating.union_in_set(
    ...
GRAPH_A_TOPOLOGY, graph_key,
...
GRAPH_P_TOPOLOGY_VERTEX_KEYS, {new_vertex_key}
... )

# Remove elements from a set field
>>> mutating.subtract_in_set(
    ...
GRAPH_A_TOPOLOGY, graph_key,
...
GRAPH_P_TOPOLOGY_VERTEX_KEYS, {deleted_vertex_key}
... )
```

### Map Operations

```pycon
# Add entries to a map field
>>> mutating.union_in_map(
    ...
attachment, key, path_to_map,
...
{"new_key": "new_value"}
... )
```

### Why Paths Matter

When two users edit different fields simultaneously:

```
User A: update(attachment, key, path_to_name, "Alice")
User B: update(attachment, key, path_to_email, "bob@example.com")

After merge: Both updates apply (disjoint paths)
```

With `set()`, one user's changes would overwrite the other's.

---

## Commit History

Inspect commit metadata:

```pycon
>>> header = db.commit_header(db.last_commit_id())
>>> header.label()
'Update nickname'
>>> header.parent_commit_id()
'87b2b1d275f0ac3b2389b18f58d7abe0214c2493'
```

Navigate history:

```pycon
# Compare states at different commits
>>> state1 = db.state(db.first_commit_id())
>>> state2 = db.state(db.last_commit_id())
```

---

## Embedded Definitions

CommitDatabase stores its definitions:

```pycon
>>> defs = db.definitions()
>>> defs.types()
[Tuto::User, Tuto::Login, Tuto::Identity]

>>> defs.inject()
# Now TUTO_A_USER_LOGIN etc. are available
```

---

## What's Next

- [Blobs](blobs.md) - Binary data storage
- [Serialization](serialization.md) - JSON and binary encoding
