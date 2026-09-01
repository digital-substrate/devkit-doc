# Database Transfer

Four converters move documents and blobs between `Database` and `CommitDatabase`
stores, in every combination of the two.

Each converter takes **pre-opened source and target handles** — never filesystem
paths — so a transfer works over both local and remote transports. Every direction
returns a {js:class}`DatabaseTransferInfo` reporting how many documents and blobs it
moved.

**When to use**: reach for these when data must change store kind or be replicated,
rather than be read or mutated in place.

```{seealso}
{doc}`/commit/commit_database` — the `CommitDatabase` model, including the
**Flatten** pattern that {js:class}`CommitDatabaseFlattener` automates.
```

## The four directions

| From | To | Class / method | Blobs kept |
|------|----|----------------|------------|
| `Database` | `Database` | {js:class}`DatabaseCopier` — `.copy(source, target)` | **All**, including orphans — a faithful replica |
| `Database` | `CommitDatabase` | {js:class}`DatabaseToCommitDatabaseConverter` — `.convert(source, target, label)` | Only those the documents reference |
| `CommitDatabase` | `Database` | {js:class}`CommitDatabaseToDatabaseConverter` — `.convert(source, commitId, target)` | Only those the chosen commit references |
| `CommitDatabase` | `CommitDatabase` | {js:class}`CommitDatabaseFlattener` — `.flatten(source, commitId, target, label)` | Only those the chosen commit references |

The two converters that target a `CommitDatabase` write the source state as a
**single commit** under an explicit `label`; the two that read from one take an
explicit `commitId` and reconstruct that commit's state. There is no implicit
current commit.

## Blob handling

Only {js:class}`DatabaseCopier` preserves orphan blobs, because it is the one
faithful 1:1 replica. The three converters that *narrow* — into a commit, into a
flat state, or into a single-commit history — first collect the blobs the resulting
state actually references and copy only those, dropping orphans on the `Database`
side and superseded history blobs on the `CommitDatabase` side.

Blobs are streamed in 64 MiB chunks, so payloads larger than 2 GB transfer without
failing.

## Quick Start

```js
const { CommitDatabaseFlattener, CommitDatabaseToDatabaseConverter } =
    require('@digitalsubstrate/dsviper');

// Collapse a chosen commit into a fresh single-commit CommitDatabase,
// discarding history and superseded blobs (the Flatten pattern).
const info = new CommitDatabaseFlattener().flatten(
    source, headCommitId, target, 'flattened baseline');
console.log(info.documents(), 'documents,', info.blobs(), 'blobs');

// Materialize one commit's state into a plain, history-free Database.
new CommitDatabaseToDatabaseConverter().convert(source, commitId, flatDb);
```

`source`, `target` and `flatDb` are already-open database handles; see
{doc}`database` and {doc}`commit` for opening and creating each kind.

```{note}
`documents()` and `blobs()` are methods here, where the Python binding exposes them
as attributes (`info.documents`). They are also missing from the binding's
TypeScript declarations, so they do not appear in the Reference section below.
```

## Progress reporting

Pass a callback as the last argument to observe a long-running transfer. It
receives the current action and a percentage:

```js
const { DatabaseCopier } = require('@digitalsubstrate/dsviper');

new DatabaseCopier().copy(source, target,
    (action, percent) => console.log(`${action}: ${percent.toFixed(0)}%`));
```

```{tip}
The Python binding takes a `StepperDelegate` subclass overriding `step()` where Node
takes a plain function. A first-class callback is the JS idiom, so the binding has
no `StepperDelegate` class to expose.
```

## Key classes

| Class | Purpose | Example |
|-------|---------|---------|
| {js:class}`DatabaseCopier` | Faithful `Database` → `Database` replica | `.copy(source, target)` |
| {js:class}`CommitDatabaseFlattener` | Collapse a commit into a fresh single-commit store | `.flatten(source, id, target, label)` |
| {js:class}`DatabaseToCommitDatabaseConverter` | Bring a flat store under version control | `.convert(source, target, label)` |
| {js:class}`CommitDatabaseToDatabaseConverter` | Materialize one commit as a flat store | `.convert(source, id, target)` |

The mirror of this page for the Python binding is {doc}`../../dsviper-python/api/transfer`.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`CommitDatabaseFlattener` | Flattens a CommitDatabase commit into a single-commit CommitDatabase |
| {js:class}`CommitDatabaseToDatabaseConverter` | Converts a CommitDatabase into a Database |
| {js:class}`DatabaseCopier` | Copies a Database into another Database |
| {js:class}`DatabaseToCommitDatabaseConverter` | Converts a Database into a CommitDatabase |
| {js:class}`DatabaseTransferInfo` | Result of a database conversion: counts of copied documents and blobs |

## Reference

```{js:autoclass} CommitDatabaseFlattener
:members:
```

```{js:autoclass} CommitDatabaseToDatabaseConverter
:members:
```

```{js:autoclass} DatabaseCopier
:members:
```

```{js:autoclass} DatabaseToCommitDatabaseConverter
:members:
```

```{js:autoclass} DatabaseTransferInfo
:members:
```
