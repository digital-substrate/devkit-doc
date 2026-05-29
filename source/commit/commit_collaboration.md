# Supervised Reconciliation

The {ref}`three regimes <three-regimes>` place *collaboration* — arbitrating
overlapping intentions, the manual-merge / review model — *above* the engine:
"Commit provides none". [Cooperative Discipline](commit_cooperation.md#when-a-supervisor-is-required)
says the same from the other side: when scope cannot be decomposed, "the
supervisor is yours to build". This page documents a reference implementation
of that supervisor: an API that **identifies, surfaces, and reconciles a
reconstructed conflict** over a merge the engine has already performed.

It is **additive**: a set of free functions over `CommitDatabase`'s public
API, with no change to the engine, the storage format, or the runtime. It
ships inside Viper and reaches Python through `dsviper`.

## A conflict is reconstructed, not reported

The engine has no notion of conflict. Mechanical convergence linearises
streams and collapses overlapping intent by structural rule, signalling
nothing. A pairwise merge is target-wins and non-commutative; when several
heads meet, `reduce_heads()` folds them in the lexicographic order of their
content hashes (the SHA-1 `CommitId`s). The resolved state is therefore
deterministic, but the determinant is the opcode shape and the hash ordering,
not the authors' intent — so to an observer, *which* intent the merge keeps is
arbitrary. This is the index's own caveat: "which sequence is applied when
several heads meet is an application strategy, not an engine guarantee".

This layer does not change that. It **reconstructs** a notion of conflict as
an analysis overlay: after a merge, it recomputes each branch's typed delta
and reports the loci where one branch's intent did not survive. The conflict
is manufactured on replay; it is not something the engine stores or knows.

## The headless triad

No user interface is part of this layer. Both seams are plain data, so the
presentation tier is the consumer's choice — QML tooling, a CLI, a web review,
or an automated arbiter.

| Step          | API                                                      | Produces                                               |
|---------------|----------------------------------------------------------|--------------------------------------------------------|
| **Identify**  | `CommitMergeAnalyzer.analyze_merge(db, merge)`           | `CommitMergeAnalysis` with the reconstructed conflicts |
| **Surface**   | `CommitMergeConflict` (read-only, serialisable)          | `{attachment, key, path, base/ours/theirs/merged}`     |
| **Reconcile** | `CommitMergeAnalyzer.reconcile(db, merge, [...], label)` | a survival commit, child of the merge                  |

The supervisor reads the conflicts, decides per conflict, and expresses each
decision as a `CommitMergeResolution`. Accepting the merge requires no
resolution.

## Why the anchor is post-merge

Arbitration cannot happen *before* the merge. The merge result depends on the
**opcode shape** — an absolute `set` re-baselines the document and is then
overwritten target-wins, while incremental path-based operations combine
without loss — and a value-level three-way comparison cannot predict which
case applies. The only authority is `state(merge)`, the result the engine
actually produced.

So the layer endures the merge, reads `merge_state = db.state(merge)`, and
defines lost intent against it: a branch's intent is lost at an opcode's locus
**iff that opcode's effect is not already present** in `merge_state`. The
check is per opcode type — a `Set_Union` survived iff its elements are present,
a `Document_Update(path, value)` iff `path` resolves to `value`, and so on. A
conflict is therefore anchored on a **path** (the opcode locus), not on a whole
document.

## Reconciliation is a survival patch

To make a chosen value survive, the layer authors a follow-up `Mutations`
commit, child of the merge: it copies `merge_state`, places each decree at its
path, and diffs the result against `merge_state`. "Accept the merge" yields an
empty diff, so the merge simply stands and no commit is created.

The construction satisfies a round-trip invariant for every value shape:

```
apply(merge_state, diff(merge_state, chosen)) == chosen
```

It holds by construction, because `diff` is the engine's own authoring
function replayed by the same evaluator. No patch algebra is invented; the
layer constructs a patch the deterministic evaluator applies exactly.

## Granularity and its ceiling

The decree's reach mirrors the merge's own nature, container by container:

| Container       | Reconciliation                                          |
|-----------------|---------------------------------------------------------|
| Set / Map       | fine, per element / entry (union, subtract, update)     |
| Structure       | per field (`Document_Update`, sibling fields preserved) |
| XArray / Vector | field-scoped `Document_Update` (decretal, whole field)  |

A conflict's `path` is the finest decree point; a supervisor may climb its
ancestors for a coarser, more dictatorial decree, up to a whole-document
`Document_Set`. Deeper paths bound the blast radius to a smaller locus. The
universal fallback — `Document_Update(path = field, value = chosen)` — is
always expressible and round-trips trivially. Sequence reordering and
element-level XArray merge are out of scope.

## When there is no base

When the two branches share no unambiguous common ancestor — a criss-cross
history, or two independent roots — there is no base to anchor detection
against. The layer degrades to a 2-way scan (candidates are every key where
the branches differ) rather than failing; `CommitMergeAnalysis.two_way()`
reports this mode. Survival is base-free either way, so reconciliation is
identical.

## Honest bounds

- **It inherits the engine's convergence; it does not repair it.** The merge
  it reconciles is still hash-ordered and target-wins. This layer makes the
  lost intent observable and correctable — nothing more.
- **It is *a* supervisor, not *the* supervisor.** Other supervised regimes —
  a semantic gate that refuses commits, a service that mediates allocation of
  strong invariants — occupy the same row and are not provided here. See
  [Cooperative Discipline](commit_cooperation.md#when-a-supervisor-is-required).
- **Intent beyond commit headers is not recoverable.** The layer surfaces
  *that* values collided and *what* each was, never *why* an author wanted it.

## API surface

| Type / function                     | Role                                                                                             |
|--------------------------------------|--------------------------------------------------------------------------------------------------|
| `CommitMergeAnalyzer.merge_base`     | Structural common ancestor (DAG only); `None` on criss-cross.                                    |
| `CommitMergeAnalyzer.analyze_merge`  | Post-merge analysis; returns a `CommitMergeAnalysis`.                                             |
| `CommitMergeAnalyzer.reconcile`      | Authors the survival commit from a list of resolutions.                                          |
| `CommitMergeAnalysis`                | `conflicts()`, `has_conflicts()`, `base()`, `two_way()`, `ours()`, `theirs()`, `merge_commit()`. |
| `CommitMergeConflict`                | `attachment()`, `key()`, `path()`, `base_value()`, `ours_value()`, `theirs_value()`, `merged_value()`. |
| `CommitMergeResolution`              | A decree `(attachment, key, path, chosen)` built by the supervisor.                              |

## Example

```pycon
>>> # Endure the merge the engine produces (Data).
>>> merge = db.merge_commit("merge ours into theirs", ours, theirs)

>>> # Identify the reconstructed conflicts (Logic).
>>> analysis = CommitMergeAnalyzer.analyze_merge(db, merge)
>>> analysis.has_conflicts()
True

>>> # Surface each conflict to the supervisor (Presentation, tier-agnostic).
>>> resolutions = []
>>> for conflict in analysis.conflicts():
...     # The supervisor decides; here, keep ours at the conflicting path.
...     resolutions.append(CommitMergeResolution(
...         conflict.attachment(), conflict.key(),
...         conflict.path(), conflict.ours_value().unwrap()))

>>> # Reconcile: a survival commit, child of the merge (Data).
>>> survivor = CommitMergeAnalyzer.reconcile(db, merge, resolutions, "reconcile")
```

When a supervisor accepts the merge for every conflict, `reconcile` returns
the merge commit unchanged.

## See Also

- {ref}`Three regimes of multi-author work <three-regimes>` — where this layer
  sits.
- [Modes of Use](commit_modes.md) — the diagnostic that determines whether the
  contract, and this layer, are load-bearing.
- [The Dual-Layer Contract](commit_contract.md) — what the engine guarantees
  structurally and what remains the application's semantic responsibility.
- [Cooperative Discipline](commit_cooperation.md) — the disjoint envelope, and
  when a supervisor is required instead.
