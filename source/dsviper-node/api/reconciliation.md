# Merge Reconciliation

`CommitMergeAnalyzer` is an additive, application-level supervisor over the public
`CommitDatabase` API. The engine reduces concurrent streams
mechanically and signals no conflict; this layer **reconstructs** a notion of
conflict over a merge — already persisted, or computed from the two heads before it
is written — and lets a caller make a chosen value survive. It adds no engine,
storage-format, or runtime change.

**When to use**: reach for this family when the application, not the engine, must
decide which value survives where two streams touched the same locus. If mechanical
reduction is acceptable, none of this is needed.

```{seealso}
{doc}`/commit/commit_collaboration` — the model, the headless
identify / surface / reconcile triad, and its bounds.
```

## Quick Start

```js
const { CommitMergeAnalyzer, CommitMergeResolution } =
    require('@digitalsubstrate/dsviper');

const merge = db.mergeCommit('merge', ours, theirs);
const analysis = CommitMergeAnalyzer.analyzeMerge(db, merge);

// The supervisor decides per conflict; here, keep ours at every locus.
// A resolution pairs the conflict with the value to make survive at its path —
// oursValue() already reads that value at the conflict's locus.
const resolutions = analysis.conflicts().map(
    (c) => new CommitMergeResolution(c, c.oursValue().unwrap()));

const survivor = CommitMergeAnalyzer.reconcile(db, merge, resolutions, 'reconcile');
```

Accepting the merge for every conflict makes `reconcile` return the merge commit
unchanged.

The same three steps run before the merge commit exists:
`analyzeVirtualMerge(db, ours, theirs)` — whose analysis carries no anchor, so
`CommitMergeAnalysis.mergeCommit()` is `undefined` — then
`reconcileState(mergeState, resolutions)` to render the arbitrated state in memory
(writing nothing), and `materializeMerge(db, ours, theirs, resolutions, mergeLabel,
survivalLabel)` to write the merge and its survival child together. The merge state
comes from `CommitStateBuilder.mergeState(db, ours, theirs)`.

## Key classes

| Class | Purpose | Example |
|-------|---------|---------|
| {js:class}`CommitMergeAnalyzer` | The entry point: analyze, reconcile, materialize | `CommitMergeAnalyzer.analyzeMerge(db, merge)` |
| {js:class}`CommitMergeAnalysis` | What the analysis found: documents, conflicts, base | `analysis.conflicts()` |
| {js:class}`CommitMergeConflict` | One locus, with its base / ours / theirs / merged values | `c.oursValue()` |
| {js:class}`CommitMergeResolution` | A conflict paired with the value to make survive | `new CommitMergeResolution(c, chosen)` |

The mirror of this page for the Python binding is {doc}`../../dsviper-python/api/reconciliation`.

## Classes

| Class | Description |
|-------|-------------|
| {js:class}`CommitMergeAnalysis` | The result of a 3-way merge analysis: the merge base and the list of reconstructed conflicts between the two branches |
| {js:class}`CommitMergeAnalyzer` | Additive, post-merge 3-way reconciliation over a CommitDatabase |
| {js:class}`CommitMergeConflict` | A single locus, anchored on a path, where one branch's intent did not survive the merge, reconstructed as base/ours/theirs/merged values |
| {js:class}`CommitMergeDocument` | All conflicts of one document (attachment, key) — the unit reconcile operates on |
| {js:class}`CommitMergeResolution` | A supervisor's decree for one conflict: the chosen value should survive at the conflict's locus |

## Reference

```{js:autoclass} CommitMergeAnalysis
:members:
```

```{js:autoclass} CommitMergeAnalyzer
:members:
```

```{js:autoclass} CommitMergeConflict
:members:
```

```{js:autoclass} CommitMergeDocument
:members:
```

```{js:autoclass} CommitMergeResolution
:members:
```

