# Commit & versioning

The versioned persistence tier. `CommitDatabase` keeps the history of mutations
in a DAG of commits; two stateless namespaces operate over it, each taking a
`CommitDatabase` as their first argument:

- `CommitStateBuilder` — **reconstruct** a `CommitState` from a chosen commit:
  `CommitStateBuilder.state(db, id)`, `CommitStateBuilder.initialState(db)`.
- `CommitDatabaseHelper` — **reduce heads** and navigate (`reduceHeads`,
  `forward` / `fastForward`).

`CommitDatabase` itself answers topology queries (`headCommitIds()`,
`lastCommitId()`, `isAncestor`) and holds no "current" state. A `CommitStore`
wraps the persistence layer and both namespaces behind a stateful facade
(undo/redo, the dispatch surface) for interactive apps. A reconstructed state is
a blind replay of the linearized trace — see the peer Python narrative,
{doc}`../../commit/index`.

This bucket also holds the additive merge machinery (`CommitMergeAnalyzer` and
friends): see [Merge reconciliation](#merge-reconciliation) below.

## When to use

Reach for this page's classes when you persist DSM documents **with history** —
every write is a commit, and earlier states stay reconstructible. If you only
need flat CRUD without versioning, use {doc}`database` instead. The Python
counterpart is {doc}`../../dsviper-python/api/commit`.

## Quick Start

```js
const {
    CommitDatabase, CommitStateBuilder, CommitMutableState,
} = require('@digitalsubstrate/dsviper');

// Create an in-memory commit database and grow its schema from definitions.
const db = CommitDatabase.createInMemory();
db.extendDefinitions(defs.const());

// Stage writes on a mutable state built from the empty initial snapshot.
const state = new CommitMutableState(CommitStateBuilder.initialState(db));
const mutating = state.attachmentMutating();
mutating.set(attachment, key, document); // a Document_Set opcode is recorded

// Seal the staged mutations into a new commit.
db.commitMutations('Add document', state);

// Read back from a reconstructed snapshot at the latest commit.
const getting = CommitStateBuilder.state(db, db.lastCommitId()).attachmentGetting();
const value = getting.get(attachment, key); // a ValueOptional

db.close();
```

```{note}
INT64 documents unwrap to a JS `bigint` (`getting.get(att, key).unwrap()` is
`42n`, not `42`). Compare keys and values with `.equals`, never `==`. Operations
on a closed `CommitDatabase` throw a `ViperError` (a JS `Error` whose
`.name === 'ViperError'`).
```

## Choosing the right class

| Use case | Class | Example |
|----------|-------|---------|
| Create an in-memory commit database | {js:class}`CommitDatabase` | `CommitDatabase.createInMemory()` |
| Read state at a specific commit | {js:class}`CommitStateBuilder` | `CommitStateBuilder.state(db, id)` |
| Prepare mutations | {js:class}`CommitMutableState` | `new CommitMutableState(CommitStateBuilder.initialState(db))` |
| Write documents (`set`, `update`, `unionInSet`, …) | `attachmentMutating()` | `state.attachmentMutating().set(att, key, doc)` |
| Read documents (`get`, `keys`, `has`) | `attachmentGetting()` | `CommitStateBuilder.state(db, id).attachmentGetting()` |
| Inspect commit metadata | {js:class}`CommitHeader` | `db.commitHeader(id)` |
| Redux-style store (dispatch, undo/redo) | {js:class}`CommitStore` | `store.use(db); store.dispatch(label, fn)` |
| Reconcile a merge | {js:class}`CommitMergeAnalyzer` | see below |
| Serve a database over a socket | {js:class}`CommitDatabaseServer` | see [Serving a database](#serving-a-database) below |

## Merge reconciliation

`CommitMergeAnalyzer` is an additive, application-level supervisor over the
public `CommitDatabase` API. The engine reduces concurrent streams mechanically
and signals no conflict; this layer **reconstructs** a notion of conflict over a
merge — already persisted, or computed from the two heads — and lets a caller
make a chosen value survive. It adds no engine, storage-format, or runtime
change.

```js
const { CommitMergeAnalyzer, CommitMergeResolution } = require('@digitalsubstrate/dsviper');

const merge = db.mergeCommit('merge', ours, theirs);
const analysis = CommitMergeAnalyzer.analyzeMerge(db, merge);

// The supervisor decides per conflict; here, keep ours at every locus.
const resolutions = analysis.conflicts().map(
    (c) => new CommitMergeResolution(c, c.oursValue().unwrap()),
);
const survivor = CommitMergeAnalyzer.reconcile(db, merge, resolutions, 'reconcile');
```

Accepting the merge for every conflict (resolving each with `mergedValue()`)
makes `reconcile` return the merge commit unchanged. When the two heads share no
unambiguous base, `analyzeMerge` degrades to a base-free 2-way scan
(`analysis.twoWay()` is `true`, `analysis.base()` is `undefined`) rather than
erroring. For the model behind identify / surface / reconcile, see
{doc}`../../commit/index`.

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Serving a database

A Node host can **serve** a commit database, not only consume one:
{js:class}`CommitDatabaseServer` opens the database behind a passive socket and serves each
client on its own C++ thread. The client side is unchanged —
{js:class}`CommitDatabaseRemote` (`connectLocal` / `connect`).

The loop belongs to the host. `step(timeoutInSec)` is a *bounded* wait, so the server must
yield to the event loop between calls; a loop that never yields starves timers, I/O and
signal delivery.

```js
const { CommitDatabase, CommitDatabaseServer, Cancelation, Socket, LoggerNull } =
    require('@digitalsubstrate/dsviper');

CommitDatabase.create(databasePath).close();

const cancelation = new Cancelation();
const socket = Socket.createPassiveLocal(socketPath);
const server = new CommitDatabaseServer(databasePath, socket,
                                        new LoggerNull().logging(), cancelation);

process.on('SIGINT', () => cancelation.cancel());   // honoured within one timeout

const tick = () => {
    if (!server.step(1) || cancelation.requested()) { server.finishBefore(5); return; }
    setImmediate(tick);
};
server.start(); tick();
```

`finishBefore(timeoutInSec)` bounds the teardown and **returns the number of client threads
it could not join** — zero means every client ended, non-zero means the process is not idle
yet. `finish()` waits without a bound.

`Socket` exposes only the passive factories a server needs (`createPassiveLocal`,
`createPassiveInet`): a host consumes a service through the `*Remote` classes, it does not
drive a socket by hand. A passive local socket **is a file on disk**, and V8 releases nothing
on a schedule a host can rely on — release it explicitly with `socket.close()`, or through
`[Symbol.dispose]`: `using socket = Socket.createPassiveLocal(socketPath)`.

```{note}
On macOS and Linux a unix-domain socket path is limited to ~104 bytes; a longer path fails
`bind` with a misleading "Address already in use".
```

Available from the Node binding 1.2.9 (runtime 1.2.24) — see {doc}`../../changelog`.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`Commit` | A class used to represent a commit |
| {js:class}`CommitData` | A class used to represent data associated with a commit during the synchronization of two databases |
| {js:class}`CommitDatabase` | A Commit database keeps the history of mutations in a DAG of commit |
| {js:class}`CommitDatabaseFlattener` | Flattens a CommitDatabase commit into a single-commit CommitDatabase |
| {js:class}`CommitDatabaseHelper` | A utility class for a Commit Database |
| {js:class}`CommitDatabaseRemote` | A low-level class used to represent a remote Commit database through the CommitDatabasing interface |
| {js:class}`CommitDatabaseSQLite` | A low-level class used to represent the database based on SQLite3 through the CommitDatabasing interface |
| {js:class}`CommitDatabaseServer` | Serve a CommitDatabase over a socket, one C++ thread per client |
| {js:class}`CommitDatabaseToDatabaseConverter` | Converts a CommitDatabase into a Database |
| {js:class}`CommitDatabasing` | An interface used to abstract the implementation of the persistence layer for a Commit database |
| {js:class}`CommitEvalAction` | A class used by the evaluator to reconstruct a value by executing mutation opcodes |
| {js:class}`CommitHeader` | A class used to represent the header of a commit |
| {js:class}`CommitMergeAnalysis` | The result of a 3-way merge analysis: the merge base and the list of reconstructed conflicts between the two branches |
| {js:class}`CommitMergeAnalyzer` | Additive, post-merge 3-way reconciliation over a CommitDatabase |
| {js:class}`CommitMergeConflict` | A single locus, anchored on a path, where one branch's intent did not survive the merge, reconstructed as base/ours/theirs/merged values |
| {js:class}`CommitMergeDocument` | All conflicts of one document (attachment, key) — the unit reconcile operates on |
| {js:class}`CommitMergeResolution` | A supervisor's decree for one conflict: the chosen value should survive at the conflict's locus |
| {js:class}`CommitMutableState` | A class used to register the mutations of a value executed through the attachmentMutating interface |
| {js:class}`CommitNode` | A class used to represent a node in the commit DAG |
| {js:class}`CommitNodeGrid` | A class used to represent the location of a commit node in the grid |
| {js:class}`CommitNodeGridBuilder` | A class used to build the grid layout of the commit DAG |
| {js:class}`CommitState` | A class used to represent data at a specific commit |
| {js:class}`CommitStateBuilder` | A utility class to build CommitState |
| {js:class}`CommitStateTrace` | A class used to represent traced opcode |
| {js:class}`CommitStateTraceProgram` | A class used to represent traced opcode |
| {js:class}`CommitStateTracing` | An interface used to trace a value (aka document) |
| {js:class}`CommitStore` | A high-level application class used to implement the store, dispatch, undo/redo and notification concepts inspired by the redux approach |
| {js:class}`CommitStoreNotifying` | An interface used to represent the notification emitted by a store |
| {js:class}`CommitSyncData` | A class used to represent data exchanged during the synchronization of two databases |
| {js:class}`CommitSynchronizer` | A class used to synchronize two concrete databases through the CommitDatabasing interface (low-level driver interface) |
| {js:class}`CommitSynchronizerInfo` | A class used to represent data exchanged during the synchronization of two databases |
| {js:class}`CommitSynchronizerInfoTransmit` | A class used to represent statistics of data exchanged during the synchronization of two databases |

## Reference

```{js:autoclass} Commit
:members:
```

```{js:autoclass} CommitData
:members:
```

```{js:autoclass} CommitDatabase
:members:
```

```{js:autoclass} CommitDatabaseFlattener
:members:
```

```{js:autoclass} CommitDatabaseHelper
:members:
```

```{js:autoclass} CommitDatabaseRemote
:members:
```

```{js:autoclass} CommitDatabaseSQLite
:members:
```

```{js:autoclass} CommitDatabaseServer
:members:
```

```{js:autoclass} CommitDatabaseToDatabaseConverter
:members:
```

```{js:autoclass} CommitDatabasing
:members:
```

```{js:autoclass} CommitEvalAction
:members:
```

```{js:autoclass} CommitHeader
:members:
```

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

```{js:autoclass} CommitMutableState
:members:
```

```{js:autoclass} CommitNode
:members:
```

```{js:autoclass} CommitNodeGrid
:members:
```

```{js:autoclass} CommitNodeGridBuilder
:members:
```

```{js:autoclass} CommitState
:members:
```

```{js:autoclass} CommitStateBuilder
:members:
```

```{js:autoclass} CommitStateTrace
:members:
```

```{js:autoclass} CommitStateTraceProgram
:members:
```

```{js:autoclass} CommitStateTracing
:members:
```

```{js:autoclass} CommitStore
:members:
```

```{js:autoclass} CommitStoreNotifying
:members:
```

```{js:autoclass} CommitSyncData
:members:
```

```{js:autoclass} CommitSynchronizer
:members:
```

```{js:autoclass} CommitSynchronizerInfo
:members:
```

```{js:autoclass} CommitSynchronizerInfoTransmit
:members:
```
