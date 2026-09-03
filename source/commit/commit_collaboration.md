# Supervised Reconciliation

When scope cannot be decomposed and a supervisor becomes necessary —
[Cooperative Discipline](commit_cooperation.md#when-a-supervisor-is-required)
sets out when — that supervisor is yours to build; the engine provides none.
This page documents one implementation: an API that **identifies, surfaces,
and reconciles a reconstructed conflict** over a merge the engine has already
performed.

It is **additive**: a set of free functions over `CommitDatabase`'s public
API, with no change to the engine, the storage format, or the runtime. It
ships inside Viper and reaches Python through `dsviper`.

## A conflict is reconstructed, not reported

The engine has no notion of conflict. Mechanical reduction linearises
streams and collapses overlapping intent by structural rule, signalling
nothing. A pairwise merge is target-wins and non-commutative, and
`CommitDatabaseHelper.reduce_heads()` folds several heads in an order the
authors do not control
([the mechanism](commit_database.md#how-reduction-picks-a-winner)).
The reduced state is therefore deterministic, but the determinant is
the opcode shape, which head is most recent, and the hash ordering of the rest,
not the authors' intent — so to an observer, *which* intent the merge keeps is
arbitrary. This is the index's own caveat: "which sequence is applied when
several heads meet is an application strategy, not an engine guarantee".

This layer does not change that. It **reconstructs** a notion of conflict as
an analysis overlay: after a merge, it recomputes each stream's typed delta
and reports the loci where one stream's intent did not survive. The conflict
is manufactured on replay; it is not something the engine stores or knows.

## The headless triad

No user interface is part of this layer. Both seams are plain data, so the
presentation tier is the consumer's choice — QML tooling, a CLI, a web review,
or an automated policy.

| Step          | API                                                      | Produces                                               |
|---------------|----------------------------------------------------------|--------------------------------------------------------|
| **Identify**  | `CommitMergeAnalyzer.analyze_merge(db, merge)`           | `CommitMergeAnalysis` with the reconstructed conflicts |
| **Surface**   | `CommitMergeConflict` (read-only, serialisable)          | `{attachment, key, path, base/ours/theirs/merged}`     |
| **Reconcile** | `CommitMergeAnalyzer.reconcile(db, merge, [...], label)` | a survival commit, child of the merge                  |

These name the post-merge functions; the same three steps also work before the
merge commit is written, shown below.

The supervisor reads the conflicts, decides per conflict, and expresses each
decision as a `CommitMergeResolution`. Accepting the merge requires no
resolution.

Conflicts arrive grouped per document — `CommitMergeAnalysis.documents()`
returns one `CommitMergeDocument` per `(attachment, key)`, the unit
`reconcile` operates on; `conflicts()` is the flattened view across all of
them.

## Why the anchor is the computed merge state

The choice cannot be made from the three-way values alone. The merge result depends on the
**opcode shape** — an absolute `set` re-baselines the document and is then
overwritten target-wins, while incremental path-based operations combine
without loss — and a value-level three-way comparison cannot predict which
case applies. The only authority is the **computed merge state**, the result
the engine's reduction actually produces.

So the layer anchors on that computed state — `merge_state = CommitStateBuilder.state(db, merge)` — and
defines lost intent against it: a stream's intent is lost at an opcode's locus
**iff that opcode's effect is not already present** in `merge_state`. The
check is per opcode type — a `Set_Union` survived iff its elements are present,
a `Document_Update(path, value)` iff `path` resolves to `value`, and so on. A
conflict is therefore anchored on a **path** (the opcode locus), not on a whole
document.

## Reconciliation is a survival commit

To make a chosen value survive, the layer authors a follow-up `Mutations`
commit, child of the merge: it copies `merge_state`, places each decree at its
path, and diffs the result against `merge_state`. "Accept the merge" yields an
empty diff, so the merge simply stands and no commit is created.

No patch algebra is invented: the layer builds the survival commit with the
engine's own `diff`, applied by the same deterministic evaluator. The
round-trip

```
apply(merge_state, diff(merge_state, chosen)) == chosen
```

is therefore the diff/apply law itself, not a property the layer proves. What
the layer *does* guarantee is that this holds for **every** value shape — and
that guarantee is the coarsening, not the equation: the decree stays
fine-grained where the container round-trips element by element, and falls
back to a whole-field `Document_Update` where it would not (see
[Granularity](#granularity-and-its-ceiling)).

## Granularity and its ceiling

The decree's reach mirrors the merge's own nature, container by container:

| Container       | Reconciliation                                          |
|-----------------|---------------------------------------------------------|
| Set / Map       | fine, per element / entry (union, subtract, update)     |
| Structure       | per field (`Document_Update`, sibling fields preserved) |
| XArray / Vector | field-scoped `Document_Update` (whole field)            |

A decree is anchored on the conflict's own `path` — the finest locus the merge
localised the lost intent to — and the supervisor dictates only the *value*
that should survive there (`CommitMergeResolution(conflict, chosen)`). `reconcile`
applies a recursive deep `Document_Update` at that path, so the merge's sibling
fields and leaves are preserved untouched; the blast radius is bounded to the
locus, not the whole document. Sequence reordering and element-level XArray
merge are out of scope.

## When there is no base

When the two streams share no unambiguous common ancestor — a criss-cross
history, or two independent roots — there is no base to anchor detection
against. The layer degrades to a 2-way scan (candidates are every key where
the streams differ) rather than failing; `CommitMergeAnalysis.two_way()`
reports this mode. Survival is base-free either way, so reconciliation is
identical.

## Reconciling before the merge exists

The triad above assumes the merge commit is already written. It need not be.
The anchor is the *computed* merge state, and that state follows from the two
heads alone — `CommitStateBuilder.merge_state(db, ours, theirs)` — with no
merge commit persisted. The reconciliation is then identical; only the moment
the merge commit is written moves. Two faces of one mechanism:

| Face           | Anchor              | Path                                                                                              |
|----------------|---------------------|---------------------------------------------------------------------------------------------------|
| **post-merge** | the persisted merge | `analyze_merge(db, merge)` → `reconcile(db, merge, [...], label)`                                  |
| **pre-merge**  | the two heads       | `analyze_virtual_merge(db, ours, theirs)` → `reconcile_state(merge_state, [...])` → `materialize_merge(db, ours, theirs, [...], merge_label, survival_label)` |

The pre-merge path writes nothing until the last step. `analyze_virtual_merge`
returns an analysis with no anchor — `CommitMergeAnalysis.merge_commit()` is
empty — and `reconcile_state` renders the arbitrated result in memory as a
`CommitMutableState`, so a supervisor can preview every decree and discard it
with the graph untouched. Only `materialize_merge` commits, writing the merge
and its survival child together. Detection stays advisory in both faces: it
directs attention, it does not gate the merge.

## Why the pre-merge face is load-bearing

The two faces are not conveniences of equal weight. On an append-only DAG
nothing is ever un-written: once the merge and its survival child are
materialised, a reconciliation you come to regret cannot be removed, only
**compensated** — a revert, a fresh survival that re-decrees, stacked on top.
The state you now call wrong stayed momentarily real and reachable; another
head may have diverged from it, and the history keeps the hesitation. There is
no `delete_commit` to reach for — it is a live-demo trick, not a feature (see
[Storage growth](commit_database.md#storage-growth)). Immutability splits
"undo" into two different acts, and only the pre-merge face reaches the cheap
one:

- **abort** (virtual) — the arbitrated result lives only in memory as a
  `CommitMutableState`; discarding it costs nothing and leaves no trace, the
  graph untouched.
- **compensate** (post-merge) — the merge is written, so the correction is
  another commit, and the wrong state stays forever visible and reachable in
  the DAG.

The virtual merge moves the decision point in front of the irreversible write.
That is what lets a supervisor *deliberate*: they may explore a whole
reconciliation and decide against it without engraving the attempt. Without
this face, every "let me see what this reconciliation would produce" becomes a
commit, and the DAG records the supervisor's drafts rather than their
decisions. `materialize_merge` is the line between the two — deliberation stays
in memory, only the decision is graved.

Two bounds keep the gate honest:

- **It is a session abort, before publication — not a distributed undo.** The
  window closes at `materialize_merge`, the publication frontier. Once the
  merge is materialised and shared, everyone who can already see it is back in
  the compensate-only regime.
- **It discards the resolution attempt, not the divergence.** The two heads
  still diverge; throwing the virtual merge away returns you to the unresolved
  conflict — which, being [reconstructed on
  demand](#a-conflict-is-reconstructed-not-reported), is still there, ready for
  another attempt.

## Honest bounds

- **It inherits the engine's reduction; it does not repair it.** The merge
  stays hash-ordered and target-wins — this layer only makes the lost intent
  observable and correctable.
- **It is *a* supervisor, not *the* supervisor.** Other supervised regimes
  (a semantic gate that refuses commits, a service mediating strong
  invariants) are not provided here — see
  [Cooperative Discipline](commit_cooperation.md#when-a-supervisor-is-required).
- **Intent beyond commit headers is not recoverable.** The layer surfaces
  *that* values collided and *what* each was, never *why* an author wanted it.

The full class surface — signatures, accessors, and a runnable example —
is the API reference: {doc}`Merge Reconciliation </dsviper-python/api/reconciliation>`.

## See Also

- {ref}`Three regimes of multi-author work <three-regimes>` — where this layer
  sits.
- [Modes of Use](commit_modes.md) — the diagnostic that determines whether the
  contract, and this layer, are load-bearing.
- [The Dual-Layer Contract](commit_contract.md) — what the engine guarantees
  structurally and what remains the application's semantic responsibility.
- [Cooperative Discipline](commit_cooperation.md) — the disjoint envelope, and
  when a supervisor is required instead.
