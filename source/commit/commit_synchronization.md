# Database synchronisation

`CommitSynchronizer` replicates a `CommitDatabase` between two
sites. A `CommitDatabase` is made of **two content-addressed
spaces**: the **DAG of commits**, and the **pool of blobs** —
immutable binary payloads identified by their hash and referenced
from inside commits (see
[Binary Data (Blobs)](../dsviper-python/blobs.md)). Both are append-only
and content-addressed
independently. Sync replicates both, by **two set differences**:
one on commit ids, one on blob hashes. Each side copies what the
other has and it lacks. The resulting DAG and blob pool on each
side are the union of both — divergent heads included, unchanged.

```{important}
That union is where the exposure begins. Sync loses nothing itself — it
is a verbatim, append-only copy — but a replicated topology is
**multi-head by construction**: each site holds its own write head, and
reducing those heads is where overlapping intent is silently collapsed,
with nothing signalled. Whether that puts you in multi-stream usage is a
modelling question, and it is effectively irreversible once the DSM model
is sealed. Run the [Modes of Use](commit_modes.md) diagnostic *before*
reaching for sync, not after.
```

---

## Two deployment patterns

### Transparent proxy

`CommitDatabase.connect()` and `CommitDatabase.connect_local()` open
a **remote proxy** over a `commit_database_server`. The application
holds no local copy; every read and write traverses the network.
This is direct remote access — not synchronisation. There is no
second base to keep in step.

See [`commit_database_server.py`](../dsviper-tools/server.md) for
the server side and `CommitDatabase.connect()` for the client side.

### Replicated

Each site holds its **own local `CommitDatabase`**, and a
`CommitSynchronizer` periodically (or on demand) exchanges commits
with another site — typically a central server, but the engine
makes no such assumption.

This pattern enables offline work, local-first reads, and bandwidth
amortisation. It also gives each site its **own write head**, which
can make the application a **multi-stream** consumer of the engine —
depending on how the diverging heads are reduced; see
[Implications](#implications).

---

## Mechanism

`CommitSynchronizer` operates on two `CommitDatabasing` instances
named **source** and **target** — they are roles, not a hierarchy.
The same machinery synchronises two local databases, two remote
ones, or any combination.

The operation in one pass:

1. **Detect change.** Read `dataVersion()` on both sides. If neither
   has changed since the last sync, return immediately.
2. **Extend definitions if needed.** Compare `definitionsHexDigest`
   on both sides — if they differ, `extendDefinitions` adds the
   sender's missing types to the receiver. `extendDefinitions` is
   strictly additive by construction (DSM types are sealed by
   definition), so independent schema evolution never blocks sync. Additive here means
   *new types*: `extendDefinitions` never rewrites data that already
   exists, which is also why it is not a migration path: reshaping data that
   already exists happens outside the runtime, with
   [`dsviper-database-tools`](https://github.com/digital-substrate/dsviper-database-tools)
   (beta) — see [Modes of Use](commit_modes.md).
3. **Copy missing commits and the blobs they reference.** Walk the
   missing commits — `source.commitIds() \ target.commitIds()` for
   Fetch, `target.commitIds() \ source.commitIds()` for Push — in
   topological order. For each Mutations commit, decode its opcodes
   (against the synced definitions) to collect any blob references they
   carry, copy those the target lacks (set difference on blob hashes),
   then create the commit itself. This guarantees the invariant that
   **a commit on the target never references a blob the target does
   not have** — the
   [`blob_id` constraint](../dsviper-python/blobs.md#blob_id-reference)
   stated in the blob API.

   Blobs are packed into batches of `size_of_packed_blobs` (default
   25 MB) to amortise network round-trips — without packing, a commit
   referencing many small blobs would cost one round-trip per blob.

Sync is a **verbatim, append-only copy**: each commit and its opcode
payload crosses the wire unchanged — it decodes a Mutations commit's opcodes
only to find the blob references it must copy first (step 3). Both sides end
with the **union of all commits, every divergent head preserved**.

---

## Three modes

The two roles are symmetric by construction; a **mode** picks one of
the two possible directions across that pair (or both, for `Sync`).

| Mode    | Direction              | Use case                                         |
|---------|------------------------|--------------------------------------------------|
| `Fetch` | source → target        | Pull updates from a server into a local replica. |
| `Push`  | target → source        | Send local commits up to a server.               |
| `Sync`  | both (Fetch then Push) | Bidirectional, the common case.                  |

Modes are passed as strings to the Python constructor and exposed
as the class constants `MODE_FETCH`, `MODE_PUSH`, `MODE_SYNC`.

---

## API

### Python (`dsviper.CommitSynchronizer`)

```python
from dsviper import CommitSynchronizer, CommitDatabase

local = CommitDatabase.open("local.cdb")
remote = CommitDatabase.connect("server.local", "54321")

synchronizer = CommitSynchronizer(local, remote, mode="Sync")
info = synchronizer.sync()
```

The returned `CommitSynchronizerInfo` reports how many commits and
blobs flowed in each direction and whether DSM definitions were
extended. See the
[CommitSynchronizer API reference](../dsviper-python/api/commit.rst) for
the full surface.

### Command line

```bash
python3 tools/commit_admin.py --host server.local sync local.cdb
python3 tools/commit_admin.py --host server.local sync local.cdb --loop --update-interval 2
```

See {ref}`commit_admin.py <commit-admin-py>` for all options,
including continuous mode.

---

## Implications

### On Modes of Use

A replicated topology is **multi-head by construction**: each site
has its own write head, and divergent heads meet at sync time, not at
write time. Whether that makes you *multi-stream* is a question of how
those heads are reduced, not of topology — the same line
[Modes of Use](commit_modes.md#multi-head-exploration) draws for
multi-head exploration. A single author who reviews each head
reduction stays single-stream; a **second author committing in
parallel**, or head reduction left unreviewed, does not.

Once you are past that line, a single-stream model — one that assumes
a single author with a linear history — has no safe path here. You are
then at least in
[Multi-stream with local invariants](commit_modes.md#multi-stream-with-local-invariants),
and possibly in
[Multi-stream with strong invariants](commit_modes.md#multi-stream-with-strong-invariants)
depending on what your invariants look like. The diagnostic of
[Modes of Use](commit_modes.md) applies *before* you reach for sync.

### Who reduces, and when

Sync never reduces. It copies commits; the heads it brings in stay divergent
until something folds them, and
[`commit_admin reduce_heads`](../dsviper-tools/server.md#reduce-heads) is a
separate operation on purpose. A replicated deployment therefore has to
answer three questions the engine does not: **which node reduces, on what
trigger, and from which anchor.**

Nothing enforces an answer. The exclusive transaction that
[`reduce_heads`](commit_database.md#how-reduction-picks-a-winner) takes stops
two nodes from folding at the same moment, not from folding differently —
and two policies produce different states on contested paths, both landing
in the history as competing merge commits.

The workable default is a **single designated reducer**: one node —
typically the site hosting the shared database, or one scheduled job — folds
after sync using the built-in `reduce_heads`, and every other site reads and
writes without folding. That is what makes the order the same for everyone,
since it is the only order anyone applies.

Treat that designation as a decision, not a detail. Launching a reduction is
an act of arbitration ([Import Outcomes](commit_contract.md#import-outcomes)):
the fold picks winners on every contested path, and whoever calls it chooses
them without being able to predict them. Decide who is allowed to perform
it, rather than leaving it to whoever happens to call first.

### On the Dual-Layer Contract

Every sync extends the local DAG with commits authored elsewhere.
Once the local state is reconstructed from a head that descends
from a `commitMerge`, **reading that state is an
[import](commit_contract.md#reading-the-state-is-an-import-not-a-load)**
— the same import boundary the contract describes for intra-base
mechanical reduction. Synchronisation does not weaken the
contract; it expands the surface where the contract applies.

### On Cooperative Discipline

[Cooperative Discipline](commit_cooperation.md) remains the
modelling exit. If the contributions of each site are routed
through structurally disjoint paths — by attachment partitioning,
accretive containers, or scope decomposition — the fold has nothing
meaningful to pick between, and reducing the heads costs you nothing
semantically. That is a property of the routing, which the
application maintains and nothing verifies, not of sync. The
discipline does not change across the sync boundary; the boundary is
just another place where it pays off — and another place where it can
quietly stop holding, since a second site is a second source of
writes on the same paths.

---

## Tools

| Tool                                                                     | Role                                                                                            |
|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| [`dsviper.CommitSynchronizer`](../dsviper-python/api/commit.rst)                | The runtime class. Python API.                                                                  |
| [`commit_admin sync`](../dsviper-tools/server.md#sync-local-with-remote) | CLI wrapper for one-shot or continuous sync against a remote server.                            |
| [`commit_admin reduce_heads`](../dsviper-tools/server.md#reduce-heads)   | Reduce multiple heads after sync. Separate operation.                                           |
| [`commit_database_server.py`](../dsviper-tools/server.md)                | Network-exposed CommitDatabase. The remote endpoint of replicated sync.                         |
| [`cdbe.py`](../commit-apps/cdbe.md)                                      | Example application wiring sync into a Qt UI (connect dialog, threaded synchroniser, live log). |

---

## See also

- [Modes of Use](commit_modes.md) — the diagnostic that determines
  whether sync is even an option for your application.
- [The Dual-Layer Contract](commit_contract.md) — what becomes
  load-bearing once sync is in play.
- [Cooperative Discipline](commit_cooperation.md) — routing each
  site's writes so the post-sync fold has nothing meaningful to pick
  between.
- [Database Server](../dsviper-tools/server.md) — the network
  surface and CLI tools.
- [cdbe.py](../commit-apps/cdbe.md) — a worked example wiring sync
  into a real application.
