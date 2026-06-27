# Database

{js:class}`Database` provides transactional, CRUD-style persistence for Viper
documents — backed by SQLite on disk or held entirely in memory. Documents are
addressed by a typed `(attachment, key, value)` triple; writes are bracketed by
a transaction, reads return a {js:class}`ValueOptional` that you peel with
`.unwrap()`.

This page also covers the helpers that move a `Database` around: the faithful
{js:class}`DatabaseCopier` (one `Database` into another, blobs and all) and the
{js:class}`DatabaseToCommitDatabaseConverter` (importing a flat `Database` into
the versioned tier).

## When to use

Reach for `Database` when you want a plain document store with **no history** —
the latest value for each key, nothing more. If you need an append-only mutation
DAG with full version history, use {js:class}`CommitDatabase` instead; see
{doc}`commit`. The two tiers interconvert through the converter classes below.

| Use case | Class | Note |
|----------|-------|------|
| Simple CRUD, no history | {js:class}`Database` | SQLite file or in-memory |
| Need version history | {js:class}`CommitDatabase` | See {doc}`commit` |
| Copy a `Database` faithfully | {js:class}`DatabaseCopier` | Replicates every blob, orphans included |
| Import a `Database` into the versioned tier | {js:class}`DatabaseToCommitDatabaseConverter` | Copies only referenced blobs |

## Quick Start

```js
const {
  Database, Definitions, NameSpace, ValueUUId, Type,
} = require('@digitalsubstrate/dsviper');

// Build a schema and create or open a database
const defs = new Definitions();
const ns = new NameSpace(ValueUUId.create(), 'Demo');
const concept = defs.createConcept(ns, 'Item');
const att = defs.createAttachment(ns, 'Count', concept, Type.INT64);

const db = Database.createInMemory();        // or Database.create('data.db')
db.extendDefinitions(defs.const());          // seed/grow the schema incrementally

// Write — requires a transaction
const key = att.createKey();
db.beginTransaction();
db.set(att, key, 42);
db.commit();                                 // db.rollback() discards instead

// Read — get() returns a ValueOptional
const result = db.get(att, key);
if (!result.isNil()) {
  const count = result.unwrap();             // INT64 comes back as a bigint
  console.log(count === 42n);                // true
}

// Enumerate keys, then delete (inside a transaction)
for (const k of db.keys(att)) { /* ... */ }

db.beginTransaction();
db.delete(att, key);                         // no error if the key is absent
db.commit();

db.close();
```

Open an existing database read-only with `Database.open(path, true)`, and probe
a file first with `Database.isCompatible(path)`. A failed operation (opening a
missing file, writing through a read-only handle, using a closed database)
throws a JS `Error` whose `.name === 'ViperError'`.

For the same API in Python, see {doc}`../../dsviper/api/database`.

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`Database` | A Database is a CRUD like transactional database |
| {js:class}`DatabaseCopier` | Copies a Database into another Database |
| {js:class}`DatabaseRemote` | A low-level class used to access a CRUD like database from a remote repository through the Databasing interface |
| {js:class}`DatabaseSQLite` | A low-level class used to represent a CRUD like database based on SQLite3 through the Databasing interface |
| {js:class}`DatabaseToCommitDatabaseConverter` | Converts a Database into a CommitDatabase |
| {js:class}`DatabaseTransferInfo` | Result of a database conversion: counts of copied documents and blobs |

## Reference

```{js:autoclass} Database
:members:
```

```{js:autoclass} DatabaseCopier
:members:
```

```{js:autoclass} DatabaseRemote
:members:
```

```{js:autoclass} DatabaseSQLite
:members:
```

```{js:autoclass} DatabaseToCommitDatabaseConverter
:members:
```

```{js:autoclass} DatabaseTransferInfo
:members:
```
