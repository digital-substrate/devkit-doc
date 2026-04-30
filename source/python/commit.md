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
but NOT **semantic integrity**. Best-effort merge means the state returned after convergence
is **structurally sound but semantically untrusted**: mutations may have been silently dropped,
and disjoint updates may have combined into a state that violates a cross-field invariant.

Treat post-merge state like deserialized external input: re-validate it at read time, before
acting on it. `dsviper.Error` covers only API misuse — it does not signal lost mutations or
business-rule violations.

See [The Dual-Layer Contract](commit_contract.md) for details.
```

---

## Opening a CommitDatabase

```pycon
>>> db = CommitDatabase.open("model.cdb")
```

To create a new database with embedded definitions, use:

```bash
python3 tools/dsm_util.py create_commit_database model.dsm model.cdb
```

---

## Reading State

A freshly created database has no commits — `first_commit_id()` and
`last_commit_id()` return `None`:

```{doctest}
>>> db.first_commit_id() is None
True
>>> db.last_commit_id() is None
True
>>> db.head_commit_ids()
set()
```

The `initial_state()` method always works and returns the empty state:

```{doctest}
>>> initial = db.initial_state()
>>> len(initial.attachment_getting().keys(TUTO_A_USER_LOGIN))
0
```

### AttachmentGetting Interface

Read attachments via `attachment_getting()`:

```pycon
>>> getting = state.attachment_getting()

>>> doc = getting.get(attachment, key)
>>> doc
Optional({...})

>>> keys = getting.keys(attachment)
```

---

## Mutations

Create a mutable state and apply changes:

```pycon
>>> mutable_state = CommitMutableState(db.state(db.last_commit_id()))
>>> mutating = mutable_state.attachment_mutating()

>>> mutating.set(attachment, key, document)

>>> mutating.update(attachment, key, path, new_value)
```

> **Note**: CommitDatabase tracks history via mutations from CommitMutableState.

### Committing

`commit_mutations()` returns the new commit id — capture it explicitly to
chain further mutations or read the resulting state:

```pycon
>>> commit_id = db.commit_mutations("Commit message", mutable_state)
```

---

## Complete Example

Add an Alice document and read it back:

```{doctest}
>>> key = TUTO_A_USER_LOGIN.create_key()
>>> login = TUTO_A_USER_LOGIN.create_document()
>>> login.nickname = "alice"
>>> login.password = "secret"

>>> mutable = CommitMutableState(db.initial_state())
>>> mutable.attachment_mutating().set(TUTO_A_USER_LOGIN, key, login)
>>> commit_id = db.commit_mutations("Add Alice", mutable)

>>> state = db.state(commit_id)
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
>>> mutating.update(TUTO_A_USER_LOGIN, key, TUTO_P_LOGIN_NICKNAME, "alice_updated")
```

### Set Operations

```pycon
>>> mutating.union_in_set(GRAPH_A_TOPOLOGY, graph_key, GRAPH_P_TOPOLOGY_VERTEX_KEYS, {new_vertex_key})

>>> mutating.subtract_in_set(GRAPH_A_TOPOLOGY, graph_key, GRAPH_P_TOPOLOGY_VERTEX_KEYS, {deleted_vertex_key})
```

### Map Operations

```pycon
>>> mutating.union_in_map(attachment, key, path_to_map, {"new_key": "new_value"})
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

```{doctest}
>>> header = db.commit_header(commit_id)
>>> header.label()
'Add Alice'
>>> header.parent_commit_id() == ValueCommitId()
True
```

The first commit's parent is the zero `ValueCommitId` (no ancestor).

Navigate history by passing the explicit ids you captured:

```pycon
>>> state1 = db.state(first_commit_id)
>>> state2 = db.state(latest_commit_id)
```

---

## Embedded Definitions

CommitDatabase stores its definitions:

```{doctest}
>>> defs = db.definitions()
>>> defs.types()
[Tuto::User, Tuto::Login, Tuto::Identity]
```

Calling `defs.inject()` makes `TUTO_A_USER_LOGIN`, `TUTO_S_LOGIN`, etc.
available as constants in the calling namespace.

---

## What's Next

- [Blobs](blobs.md) - Binary data storage
- [Serialization](serialization.md) - JSON and binary encoding
