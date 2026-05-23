# Commit Database

The Commit Database is the persistence layer: an immutable mutation
DAG, transactional, with history and deterministic convergence across
concurrent streams.

```{important}
Before reading the API, identify your **mode of use**. The
[Modes of Use](commit_modes.md) diagnostic decides whether the
sections below are reference material or load-bearing for you —
single-stream readers can ignore convergence-related sections
entirely.
```

## Structure

A `CommitDatabase` holds **two content-addressed spaces**:

- The **DAG of commits** — the versioned history of mutations. Each
  commit is identified by its content hash (`CommitId`). This is
  what the rest of this page documents.
- The **pool of blobs** — immutable binary payloads (textures,
  meshes, raw buffers, …) identified by their hash and referenced
  from inside commits. See
  [Binary Data (Blobs)](../dsviper/blobs.md) for the blob API.

Both spaces are append-only and content-addressed independently.
They are replicated together by
[Database synchronisation](commit_synchronization.md).

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

The `initial_state()` method always works and returns the empty
state. The example uses constants like `TUTO_A_USER_LOGIN` exposed
by the database's embedded definitions — see
[Embedded Definitions](#embedded-definitions) below; a one-line
`db.definitions().inject()` makes them available in the calling
namespace.

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

See [Cooperative Discipline](commit_cooperation.md) for the
principle and its limits.

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

## How Convergence Picks a Winner

When concurrent streams converge, the engine has to choose a single
outcome for every overlapping path. The choice is deterministic given
a fixed merge sequence — same inputs, same merges, same result on
every client — but its mechanics are *structural*, not author- or
time-meaningful.

**The merge primitive.** `commitMerge(parent, target)` creates a
merge commit. When the resulting state is reconstructed, `target`'s
mutations are applied *after* `parent`'s — so on every overlapping
path, the value from `target` survives. This is the only such rule
the engine itself fixes, and it makes the operation non-commutative:
`commitMerge(A, B) ≠ commitMerge(B, A)`.

**Reducing multiple heads is a strategy, not a guarantee.** The
built-in `reduceHeads` iterates heads in lexicographic `CommitId`
order and calls `commitMerge` once per pair, with the running result
as parent and the next head as target. Applications are free to use a
different order — or to skip `reduceHeads` entirely and issue their
own `commitMerge` sequence. The final state depends on *who calls
commitMerge in what order*, not on a property of the engine.

**None of this preserves intent.** Whichever strategy is used, the
value that survives on an overlapping path is a function of how
merges were sequenced — not of authorship, recency, or semantic
priority. Two authors editing the same field have no way to predict
which value will survive convergence, even within a fixed strategy.

The implication for the application is treated in the
[Dual-Layer Contract](commit_contract.md#reading-the-state-is-an-import-not-a-load):
do not rely on a specific arbitration outcome; re-validate at read time.

---

## Performance characteristics

Reconstructing a document's state from its commit history is
**per-document**, not per-database. Cost depends on the opcodes that
touched it and on **Ops** — the number of path-targeted operations
on this document since its last `set`.

| Opcode             | Reconstruction | Notes                             |
|--------------------|----------------|-----------------------------------|
| `set`              | O(1)           | replaces the whole document       |
| `update`           | O(Ops)         | replays field-level updates       |
| `update_in_map`    | O(Ops)         |                                   |
| `update_in_xarray` | O(Ops)         |                                   |
| `remove_in_xarray` | O(Ops)         |                                   |
| `union_in_map`     | O(Ops · log M) | M = map size                      |
| `subtract_in_map`  | O(Ops · log M) |                                   |
| `union_in_set`     | O(Ops · S)     | S = set size                      |
| `subtract_in_set`  | O(Ops · S)     |                                   |
| `insert_in_xarray` | O(Ops²)        | UUID positioning, quadratic worst |

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

The mutation DAG is **append-only** — once written, every commit is
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

- **Identify your mode first.** The [Modes of Use](commit_modes.md) carry
  different burdens. Only *multi-stream with strong invariants* makes
  the [Dual-Layer Contract](commit_contract.md) load-bearing; the
  other modes are safe to use without it.
- **Capture `commit_id` explicitly.** `commit_mutations()` returns the new
  id; there is no implicit current commit to auto-advance. Chain further
  mutations and reads from the captured value.
- **Prefer path-based mutators over `set()`** for fields edited
  concurrently. `set()` replaces the whole document, so disjoint edits
  collide. `update`, `union_in_set`, `update_in_map`, etc. converge
  cleanly on disjoint paths — see [Why Paths Matter](#why-paths-matter).
- **Re-validate the state when you read it back, not when you build the
  mutations.** Under best-effort convergence, mutations may have been
  silently dropped and combined states may violate cross-field
  invariants. See
  [The Dual-Layer Contract](commit_contract.md#reading-the-state-is-an-import-not-a-load)
  for the discipline and where it becomes load-bearing.

