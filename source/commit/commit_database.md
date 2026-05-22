# Commit Database

The Commit Database is the persistence layer: an immutable mutation
DAG, transactional, with history and synchronisation across streams.

```{seealso}
For the runtime surface most applications actually use — current
state, dispatch, undo / redo, notifications — see
[CommitStore](commit_store.md).
```

---

## Two kinds of version DAG

Two distinct families of versioning systems share vocabulary
(commit, merge, head, branch, parent) and topology (a DAG of
nodes with one or more parents), but differ on **what a node
contains**.

Some systems (git, hg, fossil) are **snapshot DAGs**: each node
contains a full state of the tree. Their `merge` reconciles
states; when states disagree, the algorithm cannot pick and
surfaces a conflict for human arbitration.

The Commit Database is a **mutation DAG**: each node contains a
sequence of path-based mutations. Its `commitMerge` composes
mutation sequences; when mutations target the same path,
deterministic composition rules apply (last-writer-wins by
fusion order). No conflict is ever surfaced.
This is what makes mechanical convergence possible — and what makes the
[Dual-Layer Contract](commit_contract.md) necessary.

Habits built in snapshot DAGs do not transfer cleanly. Read
on with this distinction in mind.

---

## Modes of Use

How you exercise the mutation DAG determines whether the
[Dual-Layer Contract](commit_contract.md) applies to you at all.
Read this section as a diagnostic, not a catalogue.

Five user-facing modes. The first three are **single-stream** — no
`commitMerge` is reconstructed at read time, so the contract is not
load-bearing. The last two are **multi-stream** under mechanical
convergence, split by **what your invariants look like**.

```{note}
**Three regimes of multi-author work** — only one is what the Commit
Database provides:

- **Collaboration** — humans arbitrate overlapping intentions
  *before* convergence (manual-merge / review).
- **Cooperation** — disjoint contributions assemble without conflict
  by construction.
- **Mechanical convergence** — the Commit Database linearises streams
  deterministically with no notion of "conflict": clashing intentions
  are silently reconciled by structural rules. Structurally sound,
  semantically untrusted.

dsviper offers mechanical convergence. The two multi-stream modes
below are flavours of it.
```

### Time travel (read-only)

Reconstruct any past state from a `commitId`. No writes, so only the
read-side structural guarantees apply: determinism, immutability,
content-addressing.

### Single-user undo / redo

Step back along the chain, diverge, redo. *Intent: revise history*
on a single author's line. All structural guarantees apply, plus
tombstone semantics.

### Single-user exploration

Diverge the DAG and keep parallel heads alive, merging them on your
own schedule. Same machinery as undo/redo with multiple heads. Merges
happen, but a single author reviews the resulting state — still
single-stream.

### Multi-stream with local invariants

Multiple authors converge automatically, but the structural drops
cost the application nothing in practice. Two routes lead here:

- **Naturally local invariants** — the entire mutable state lives
  in containers whose convergence is commutative by construction
  (`set`, `map`, `xarray` with union / subtract / UUID positions).
  There is nothing for the engine to silently break.
- **Defensive-by-design** — cross-attachment references exist and
  may break under convergence, but the application is built from
  day one to tolerate the break: load robustly, surface the
  integrity issue, expose corrective actions to the user. This is
  an uncommon architectural choice — most applications are not
  built this way.

The Graph Editor sample exemplifies the second route: `EdgeTopology`
references vertices, and the model ships `ModelIntegrity` as a
user-facing repair pool (recreate, delete, or respawn missing
elements), on top of an application that loads graphs with broken
integrity without crashing.

For this mode the [Dual-Layer Contract](commit_contract.md) is
reference material, not load-bearing.

### Multi-stream with strong invariants

Multiple authors converge automatically; your invariants are global
(uniqueness, referential integrity the engine must uphold), or your
domain does not tolerate silent loss (financial, safety, regulatory).
This is where the [Dual-Layer Contract](commit_contract.md) becomes
load-bearing — and where reading it is a diagnostic, not a cookbook:
the four post-convergence outcomes collapse to *refuse the state*,
which is equivalent to saying mechanical convergence was the wrong
primitive.

The exit is not better post-convergence handling. It is
re-architecting toward **multi-stream with local invariants** via
scope decomposition (see
[Cooperative Discipline](commit_cooperation.md)), or building an
application-level supervisor on top of Commit.

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

- **Identify your mode first.** The [Modes of Use](#modes-of-use) carry
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
- **Do not assume a mutation landed.** After convergence, mutations
  targeting non-existent documents or unresolved paths are silently
  dropped. If the outcome matters, read the state back and check.
- **Validate on read, not on write,** when the contract applies. Engine
  output is structurally sound but semantically untrusted
  ([why](commit_contract.md#reading-the-state-is-an-import-not-a-load)) —
  enforce uniqueness, referential integrity, and cross-field invariants
  when you consume the state, not when you build the mutations.

