# Commit System

The commit system provides transactional persistence with history tracking.

**When to use**: Use `CommitDatabase` for versioned persistence with history, concurrent
streams, and sync. Every change creates a commit, enabling undo/redo and concurrent editing.

---

## Modes of Use

How you exercise the commit DAG determines which guarantees you can rely on
and where validation belongs. Four user-facing modes:

| Mode                        | What you do                                                                | Engine guarantees that bite                          | Dual-layer contract                                              |
|-----------------------------|----------------------------------------------------------------------------|------------------------------------------------------|------------------------------------------------------------------|
| **Time travel** (read-only) | Reconstruct any past state from a `commitId`                               | Determinism, immutability, content-addressing        | Not applicable — no writes                                       |
| **Single-user undo / redo** | Step back, branch, redo on a single author's chain                         | All structural guarantees + tombstone semantics      | Not load-bearing — you arbitrate every change                    |
| **Single-user exploration** | Bifurcate the DAG, keep parallel sibling lines, merge on your own schedule | All structural guarantees + multi-head machinery     | Not load-bearing — you arbitrate merges                          |
| **Automated multi-user**    | Concurrent commits from multiple authors converge without human review     | Structural only — semantic integrity is your problem | **Load-bearing** → see [Dual-Layer Contract](commit_contract.md) |

The first three modes are what most desktop applications need. The fourth is
where the contract on the next page becomes the centre of gravity.

---

## CommitDatabase

`CommitDatabase` provides versioned data storage:

- History is preserved as a DAG of commits
- You can read from any point in history

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
>>> sorted(str(t) for t in defs.types())
['Tuto::Account', 'Tuto::Identity', 'Tuto::Login', 'Tuto::Status', 'Tuto::Texture', 'Tuto::Thumbnail', 'Tuto::User']
```

Calling `defs.inject()` makes `TUTO_A_USER_LOGIN`, `TUTO_S_LOGIN`, etc.
available as constants in the calling namespace.

---

## Safe Usage

A checklist for the operational gotchas. None of this is enforced by the
engine — it's on the application.

- **Identify your mode first.** The four [Modes of Use](#modes-of-use) carry
  different burdens. Only automated multi-user makes the
  [Dual-Layer Contract](commit_contract.md) load-bearing; the other three
  are safe to use without it.
- **Capture `commit_id` explicitly.** `commit_mutations()` returns the new
  id; there is no implicit current commit to auto-advance. Chain further
  mutations and reads from the captured value.
- **Prefer path-based mutators over `set()`** for fields edited
  concurrently. `set()` replaces the whole document, so disjoint edits
  collide. `update`, `union_in_set`, `update_in_map`, etc. merge cleanly on
  disjoint paths — see [Why Paths Matter](#why-paths-matter).
- **Do not assume a mutation landed.** After convergence, mutations
  targeting non-existent documents or unresolved paths are silently
  dropped. If the outcome matters, read the state back and check.
- **Validate on read, not on write,** when the contract applies. Engine
  output is structurally sound but semantically untrusted — enforce
  uniqueness, referential integrity, and cross-field invariants when you
  consume the state, not when you build the mutations.

---

## What's Next

- [Blobs](blobs.md) - Binary data storage
- [Serialization](serialization.md) - JSON and binary encoding
