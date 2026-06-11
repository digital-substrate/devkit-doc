# Commit Database

The Commit Database is the **persistence layer**: an immutable, append-only
mutation DAG, transactional, with history. It *stores* mutations; it does not,
by itself, reduce divergence or reconstruct state. Reconstruction
(`CommitStateBuilder`) and head reduction (`CommitDatabaseHelper`) are stateless
namespaces that operate over it — see the {doc}`Commit API <../dsviper/api/commit>`
for which class owns which call. (The `CommitStore` facade wraps all three for
interactive apps.)

## The reconstruction pipe

A state is never *stored*; it is **rebuilt on demand** from the trace of
mutations leading to a commit:

```text
CommitDatabase (the DAG)
   │   CommitStateBuilder — prune the DAG, then linearize it
   ▼
Linearization — an ordered trace of opcodes (a computation trace);
   │            Enable/Disable commits mask their targets, and on every
   │            overlapping path the merge order settles target-wins (LWW)
   ▼   CommitState — apply the trace opcode by opcode onto the 
   │                initial state S₀: no interpretation, no conflict
   ▼                check, no knowledge of the DAG it came from
CommitState (the reconstructed state at that commit)
```

This is why a read is a **reconstruction, not a retrieval**: `CommitState`
replays the linearized computation trace onto the initial state S₀ and
validates nothing — it applies each opcode without interpreting it. That replay
is not hidden: {py:class}`CommitStateTrace` exposes the exact trace per
document, opcode by opcode (each opcode's exception included). The DAG
topology and the merge order fix what that trace contains (see
[How Reduction Picks a Winner](#how-reduction-picks-a-winner)); nothing
downstream re-examines the result. The state you get back is therefore *input
to re-validate*, not a stored fact — a read is "an import, not a load", the
[Dual-Layer Contract](commit_contract.md#reading-the-state-is-an-import-not-a-load).

```{important}
Before reading the API, identify your **mode of use**. The
[Modes of Use](commit_modes.md) diagnostic decides whether the
sections below are reference material or load-bearing for you —
single-stream readers can ignore reduction-related sections
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

`CommitStateBuilder.initial_state(db)` always works and returns the empty
state. The example uses constants like `TUTO_A_USER_LOGIN` exposed
by the database's embedded definitions — see
[Embedded Definitions](#embedded-definitions) below; a one-line
`db.definitions().inject()` makes them available in the calling
namespace.

```{doctest}
>>> initial = CommitStateBuilder.initial_state(db)
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
>>> mutable_state = CommitMutableState(CommitStateBuilder.state(db, db.last_commit_id()))
>>> mutating = mutable_state.attachment_mutating()

>>> mutating.set(attachment, key, document)

>>> mutating.update(attachment, key, path, new_value)
```

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

>>> mutable = CommitMutableState(CommitStateBuilder.initial_state(db))
>>> mutable.attachment_mutating().set(TUTO_A_USER_LOGIN, key, login)
>>> commit_id = db.commit_mutations("Add Alice", mutable)

>>> state = CommitStateBuilder.state(db, commit_id)
>>> state.attachment_getting().get(TUTO_A_USER_LOGIN, key)
Optional({nickname='alice', password='secret'})
```

---

## Path-Based Mutators

Instead of replacing entire documents with `set()`, path-based mutators use
**Paths** to target specific locations. This lets edits to **disjoint** paths
compose when multiple users write concurrently.

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

After reduction: Both updates apply (disjoint paths)
```

With `set()`, one user's changes would overwrite the other's.

Paths matter here because *name* and *email* are **owned by distinct writers**:
each means exactly the field they touch, so the union — Alice's name beside
Bob's email — is the collective intent, owned end to end. The same verbs
*invent* instead when a path is a **fragment** of a whole-value intent that
`diff` happened to split — see
[Re-entering the graph](commit_contract.md#re-entering-the-graph).

See [Cooperative Discipline](commit_cooperation.md) for the principle (scope
ownership) and its limits.

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
>>> state1 = CommitStateBuilder.state(db, first_commit_id)
>>> state2 = CommitStateBuilder.state(db, latest_commit_id)
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

## How Reduction Picks a Winner

When concurrent streams are reduced, the engine has to choose a single
outcome for every overlapping path. The choice is deterministic given
a fixed merge sequence — same inputs, same merges, same result on
every client — but its mechanics are *structural*, not author- or
time-meaningful.

**The merge primitive.** `commitMerge(parent, target)` only *records* a
merge commit — the pair `(parent, target)`; it resolves nothing. The ordering
is realized later, at reconstruction: when `CommitStateBuilder` linearizes the
DAG, `target`'s mutations land *after* `parent`'s, so `CommitState` replays
them last and on every overlapping path `target`'s value survives. This is the
only such rule the engine itself fixes, and it makes the operation
non-commutative: `commitMerge(A, B) ≠ commitMerge(B, A)`.

**Reducing multiple heads is a strategy, not a guarantee.** The
built-in `CommitDatabaseHelper.reduceHeads` seeds the running result with the
most recent head (`lastCommitId()`, by authoring timestamp) and folds the remaining
heads into it in ascending `CommitId` order, calling `commitMerge` once
per head with the running result as parent and the head as target. Applications are free to use a
different order — or to skip `reduceHeads` entirely and issue their
own `commitMerge` sequence. The final state depends on *who calls
commitMerge in what order*, not on a property of the engine.

Within this default, the outcome on an overlapping path is still fully
determined — a function of the `CommitId` hashes, reproducible on every
client — but it is not predictable without computing them. One
consequence is easy to miss: because the seed is folded in first and
each later `commitMerge` lets `target` overwrite it, the *most recent*
head is not the one preserved on an overlapping path; the
highest-`CommitId` head, applied last, is.

Because the outcome is set by the merge sequence and not by the engine, **every
client that reduces heads on a shared database must use the same strategy.** Two
processes folding the same heads in different orders — one in ascending
`CommitId`, another in, say, hash-table iteration order — produce different
states on contested paths, and the shared history stops converging. Fix one
reduction order for all writers of a shared store; the built-in
`CommitDatabaseHelper.reduceHeads()` is the obvious choice, and it is
transactional, where a hand-rolled fold can
leave a half-merged DAG if it is interrupted mid-merge.

**On an overlapping path, the surviving value is structural, not
intentional.** Whichever strategy is used, the value that survives is
a function of how merges were sequenced — not of authorship, recency,
or semantic priority. Two authors editing the same field have no way
to predict which value will survive reduction, even within a fixed
strategy.

The implication for the application is treated in the
[Dual-Layer Contract](commit_contract.md#reading-the-state-is-an-import-not-a-load):
do not rely on a specific LWW outcome; re-validate at read time.

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

This is not the whole-document `set()` that [Why Paths
Matter](#why-paths-matter) warns against: here `set()` targets one
subtree node, so concurrent writers on different nodes stay on disjoint
paths. Splitting accumulation this way is
[scope decomposition](commit_cooperation.md) — bounded cost *and*
composable edits, not a trade between them.

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

The only sanctioned way to shrink a database is **Flatten** — a
user-space pattern, not a runtime operation: read the current head
state from the source database, write it as the initial commit of a
fresh target database, then switch readers and writers to the new
database. The source database is untouched; the target is a new
append-only history that happens to start where the old one ended.

The `dsviper` binding ships this pattern as a ready-made converter,
`CommitDatabaseFlattener`: it flattens a chosen commit into a fresh
single-commit target, keeping only the blobs that commit still references
and dropping superseded history blobs. The source is left untouched — the
converter automates the pattern, it does not trim history in place. See
{doc}`Database Transfer <../dsviper/api/transfer>` for the full transfer
toolkit.

```{warning}
`CommitDatabase.delete_commit()` and `CommitDatabase.reset_commits()`
(plus the CLI wrapper `commit_admin reset`) are **not features** —
they are tricks for live-demo scenarios.

- `delete_commit(commit_id)` only makes sense on a head — deleting
  any other commit would orphan its descendants. Live-demo use:
  rewinding the DAG by one step.
- `reset_commits()` / `commit_admin reset` removes every commit
  except the initial one. Live-demo use: replaying a scenario from
  a known baseline between runs.

Both operations break the append-only invariant that every other
reader relies on. Never use them as storage-management tools.
```

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
  mutations and reads from the captured value. **That id is itself state**: if
  you keep it outside the database — in a scene file, a config, any side-channel
  the store never sees — it can drift out of sync (one is copied, restored, or
  reopened without the other). A stale or absent baseline makes the next read
  either raise or, worse, diff against the wrong commit and emit authored
  mutations no one made. Store the cursor so it cannot outlive or desync from
  the database it points into.
- **Prefer path-based mutators over `set()`** for fields edited
  concurrently. `set()` replaces the whole document, so disjoint edits
  collide. `update`, `union_in_set`, `update_in_map`, etc. converge
  cleanly on disjoint paths — see [Why Paths Matter](#why-paths-matter).
  But match the path to the semantic unit: letting `diff` split a bound
  value into sub-paths is its own failure mode — see
  [Re-entering the graph](commit_contract.md#re-entering-the-graph).
- **Re-validate the state when you read it back, not when you build the
  mutations.** Under best-effort reduction, mutations may have been
  silently dropped and combined states may violate cross-field
  invariants. See
  [The Dual-Layer Contract](commit_contract.md#reading-the-state-is-an-import-not-a-load)
  for the discipline and where it becomes load-bearing.

