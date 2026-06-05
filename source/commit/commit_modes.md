# Modes of Use

This page is the **diagnostic** that decides what the rest of the
chapter means for you — whether you are building a Commit Application,
a service over the Commit Database, a CLI tool, or a batch script.
The architectural choice between single-stream and multi-stream usage
— and within multi-stream, between local and strong invariants — is
effectively irreversible once a DSM model is sealed: Commit carries
no migration tooling, so switching regimes after the fact is a schema
rewrite that invalidates existing data.

The asymmetry runs one way: a multi-stream-friendly model is harmless
in single-stream usage; a single-stream model has no safe path to
multi-stream. **In doubt, model for multi-stream.**

---

## Two kinds of version DAG

Two distinct families of versioning systems share vocabulary
(commit, merge, head, parent) and topology (a DAG of nodes with
one or more parents), but differ on **what a node contains**.

Some systems (git, hg, fossil) are **snapshot DAGs**: each node
contains a full state of the tree. Their `merge` reconciles
states; when states disagree, the algorithm cannot pick and
surfaces a conflict for human arbitration.

The Commit Database is a **mutation DAG**: each node contains a
sequence of path-based mutations. Its `commitMerge` composes
mutation sequences; when mutations target the same path,
deterministic composition rules apply (last-writer-wins by
fusion order). No conflict is ever surfaced.
This is what makes mechanical reduction possible — and what makes the
[Dual-Layer Contract](commit_contract.md) necessary.

Habits built in snapshot DAGs do not transfer cleanly. Read
on with this distinction in mind.

---

## Two orthogonal axes

How you exercise the mutation DAG splits along **two independent
axes**, and conflating them is the most common source of confusion.

- **What you can do** — the *operation* axis. Time travel, undo / redo
  and multi-head exploration are **always available**, in every
  context.
- **Where you do it** — the *context* axis. Single-stream, multi-stream
  with local invariants, or multi-stream with strong invariants. The
  context alone decides whether the engine ever has to pick a winner, and
  therefore whether the [Dual-Layer Contract](commit_contract.md)
  applies to you.

**The Dual-Layer Contract applies along the context axis, not the
operation axis.** An undo is trivial in single-stream; the *same* undo
in multi-stream reads through a state an earlier `commitMerge`
produced. The operation did not change — the context did.

Read both sections as a diagnostic, not a catalogue.

---

## What you can do — the operation axis

These three operations are available regardless of context. What
changes with context is not whether you can perform them, but whether
the state they read has already passed through `commitMerge`.

### Time travel

*Read-only.* Reconstruct any past state from a `commitId`. No writes,
so only the read-side structural guarantees apply: determinism,
immutability, content-addressing.

### Undo / redo

*Append-only.* Step back along the chain, diverge, redo. Undo never
rewrites history — it masks its target with an Enable/Disable commit.
All structural guarantees apply.

### Multi-head exploration

*Parallel heads.* Diverge the DAG and keep parallel heads alive,
merging them back on your own schedule. Multi-head exploration where a
single author reviews each merged result stays **single-stream** — the
merge happens, but one person owns the resulting state.

```{important}
In single-stream every read returns exactly what you wrote. In
multi-stream every read is an
[import](commit_contract.md#reading-the-state-is-an-import-not-a-load)
— a state structurally sound but semantically untrusted, to be
re-validated at read time. This includes reads of *past* states,
because that state was itself produced by `commitMerge`. The three
operations above do not change between the two contexts; what changes
is the contract around the state they read.
```

---

## Where you do it — the context axis

### Single-stream

One author writing at a time. No `commitMerge` is reconstructed at
read time, so the [Dual-Layer Contract](commit_contract.md) is
reference material, not load-bearing. Time travel, undo / redo and
multi-head exploration all apply with only the read-side structural
guarantees — there is nothing for the engine to pick between.

### Multi-stream

Multiple authors' writes are reduced automatically by mechanical reduction.
Two flavours, split by what your invariants look like.

(local-vs-strong-invariants)=

- **Local invariant** — its truth depends only on a structurally
  disjoint subset of the data (one attachment, one path, one
  document, or a container used only where it is commutative — a
  `set` / `map`, or an `xarray` read as a *set* of elements). Two
  authors writing on disjoint paths cannot break it: the disjointness
  shields the invariant from reduction.
- **Strong invariant** (also called *global*) — its truth couples
  data that multiple authors can write in parallel: uniqueness
  across the whole model (no two assets share an SKU), referential
  integrity between attachments (an edge must point to an existing
  vertex), cross-document consistency, or any domain that does not
  tolerate silent loss (financial, safety, regulatory).

Re-validating at read time closes the gap for local invariants —
there was nothing for reduction to break. It does **not** close
the gap for strong invariants: read-side validation can *detect* a
violation, but cannot *reconstruct* the intent that reduction
dropped. The lost information is not recoverable downstream.

### Multi-stream with local invariants

Multiple authors' writes are reduced automatically, but the structural drops
cost you nothing in practice. Two routes lead here:

- **Naturally local invariants** — the entire mutable state lives
  in containers whose convergence is commutative by construction
  (`set` / `map` union / subtract), or in an `xarray` read only as a
  *set* of elements. An `xarray` converges on membership — no insert
  is lost — but the relative order of concurrently-inserted elements
  is not commutative, so an order-dependent invariant is *not*
  naturally local. Where the invariant is membership-only, there is
  nothing for the engine to silently break.
- **Defensive-by-design** — cross-attachment references exist and
  may break under reduction, but the application is built from
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

Multiple authors' writes are reduced automatically; your invariants are global
(uniqueness, referential integrity the engine must uphold), or your
domain does not tolerate silent loss (financial, safety, regulatory).
This is where the [Dual-Layer Contract](commit_contract.md) becomes
load-bearing — and where reading it is a diagnostic, not a cookbook:
the four post-reduction outcomes (*Ignore / Extract a subset /
Correct / Reject*) collapse to *Reject*, which is equivalent to
saying mechanical reduction was the wrong primitive.

The exit is not better post-reduction handling. It is
re-architecting toward **multi-stream with local invariants** via
scope decomposition (see
[Cooperative Discipline](commit_cooperation.md)), or building an
**application-level supervisor** on top of Commit — a review UI, a
semantic gate, or a coordination protocol that arbitrates *before*
the engine reduces.
