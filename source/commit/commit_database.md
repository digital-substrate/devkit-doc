# Commit Database

The Commit Database provides transactional persistence with history tracking.

**When to use**: Use `CommitDatabase` for versioned persistence with history, concurrent
streams, and sync. A `CommitStore` wraps an open database to expose undo/redo and
the dispatch surface for concurrent editing.

```{seealso}
This page documents the persistence layer in isolation — opening a
database, capturing commit ids, walking history by id. For the
runtime surface most applications actually use — current state,
dispatch, undo / redo, notifications — see
[CommitStore](commit_store.md).
```

---

## Modes of Use

How you exercise the commit DAG determines which guarantees you can rely on
and where validation belongs. Four user-facing modes — the first three
either never invoke `commitMerge` or invoke it under direct human review of
the resulting state, so the dual-layer contract is not load-bearing. The
fourth automates merges away from any supervisor, and is where the contract
on the next page becomes the centre of gravity.

### Time travel (read-only)

Reconstruct any past state from a `commitId`. No writes, so only the
read-side structural guarantees apply: determinism, immutability,
content-addressing.

### Single-user undo / redo

Step back along the chain, diverge, redo. *Intent: revise history* —
correct or replay past decisions on a single author's line. All structural
guarantees apply, plus tombstone semantics.

### Single-user exploration

Diverge the DAG and keep parallel heads alive, merging heads on your own
schedule. *Intent: explore alternatives in parallel* — same machinery as
undo/redo, but you maintain multiple heads concurrently instead of
replaying one. All structural guarantees apply, plus multi-head machinery.

### Automated multi-user

Concurrent commits from multiple authors converge without human review.
The engine guarantees structural soundness only; semantic integrity
(uniqueness, referential integrity, cross-field invariants) is your
problem. This is where the
[Dual-Layer Contract](commit_contract.md) becomes load-bearing.

```{note}
**Three regimes of multi-author work** — only one is what the Commit
Database provides:

- **Collaboration** — humans reconcile intentions: conflicts are
  identified, surfaced, resolved (the manual-merge / review model).
- **Cooperation** — disjoint contributions assemble without conflict
  by construction.
- **Mechanical convergence** — the Commit Database linearises streams
  deterministically with no notion of "conflict": clashing intentions
  are silently reconciled by structural rules. Structurally sound,
  semantically untrusted.

dsviper offers mechanical convergence. Cooperation is achievable by
structuring work along disjoint paths — see
[Cooperative Editing Patterns](commit_cooperation.md) for the full
methodology, or [Why Paths Matter](#why-paths-matter) below for a
minimal concrete example. Collaboration requires an explicit
application layer on top — that is what the
[Dual-Layer Contract](commit_contract.md) formalises.
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

### Why Paths Matter

When two users edit different fields simultaneously:

```
User A: update(attachment, key, path_to_name, "Alice")
User B: update(attachment, key, path_to_email, "bob@example.com")

After convergence: Both updates apply (disjoint paths)
```

With `set()`, one user's changes would overwrite the other's.

See [Cooperative Editing Patterns](commit_cooperation.md) for the full
methodology this example illustrates.

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

## Performance characteristics

Reconstructing a document's state from its commit history is
**per-document**, not per-database. Cost depends on the opcodes that
touched it and on **Ops** — the number of path-targeted operations
on this document since its last `set`.

| Opcode             | Reconstruction  | Notes                              |
|--------------------|-----------------|------------------------------------|
| `set`              | O(1)            | replaces the whole document        |
| `update`           | O(Ops)          | replays field-level updates        |
| `update_in_map`    | O(Ops)          |                                    |
| `update_in_xarray` | O(Ops)          |                                    |
| `remove_in_xarray` | O(Ops)          |                                    |
| `union_in_map`     | O(Ops · log M)  | M = map size                       |
| `subtract_in_map`  | O(Ops · log M)  |                                    |
| `union_in_set`     | O(Ops · S)      | S = set size                       |
| `subtract_in_set`  | O(Ops · S)      |                                    |
| `insert_in_xarray` | O(Ops²)         | UUID positioning, quadratic worst  |

### Design pitfall: O(N²) on accumulated Sets

A document whose state grows by repeated `union_in_set` across many
commits incurs O(Ops²) reconstruction — every read replays every
prior union. For long-running topologies that grow by accumulation,
prefer either a tree structure with `set()` replacing the children
list each commit, or a periodic flatten (see
[Storage growth](#storage-growth)).

### Validated scale

Commit has been benchmarked at:

- ~6 600 documents per database — about 3 MB of structural data,
  alongside ~3 GB of associated blobs on CAD workloads (structure is
  typically < 0.15 % of total disk footprint);
- up to 8 concurrent processes sharing a single SQLite database with
  applicative jitter between commits.

State reconstruction is linear in document count: a full warm-up via
`CommitState.cache_preload()` runs at ~1.5–2 µs per document across
this range — 0.4 ms at 230 documents, 14 ms at 6 600.

Behaviour beyond those envelopes is not characterised.

---

## Storage growth

The commit DAG is **append-only** — once written, every commit is
immutable. The database grows monotonically; the runtime carries no
incremental garbage collection, no partial purge that trims old
commits while keeping recent history, and no archival mechanism.

Two reductions are possible, both all-or-nothing on history:

- **Reset** (built-in) — `commit_admin reset` deletes every commit
  except the initial one (see
  {doc}`commit_admin <../dsviper-tools/server>`). The database
  returns to its initial commit — whatever state was set up at
  creation (embedded definitions, seed data, etc.). Useful to replay
  a scenario from a known-good baseline; not a substitute for
  garbage collection.
- **Flatten** (user-space pattern) — read the current head state from
  the source database, write it as the initial commit of a fresh
  target database, then switch readers and writers to the new
  database. Current state is preserved; all history is dropped.

Sustained-growth scenarios that need to keep recent history while
trimming older commits are not addressed by the current runtime.

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
  collide. `update`, `union_in_set`, `update_in_map`, etc. converge
  cleanly on disjoint paths — see [Why Paths Matter](#why-paths-matter).
- **Do not assume a mutation landed.** After convergence, mutations
  targeting non-existent documents or unresolved paths are silently
  dropped. If the outcome matters, read the state back and check.
- **Validate on read, not on write,** when the contract applies. Engine
  output is structurally sound but semantically untrusted
  ([why](commit_contract.md#reading-the-state-is-an-import-not-a-load)) —
  enforce uniqueness, referential integrity, and cross-field invariants
  when you consume the state, not when you build the mutations.

