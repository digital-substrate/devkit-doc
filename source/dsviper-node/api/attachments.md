# Attachments

An attachment connects values to documents via keys. It is the fundamental
mechanism for associating typed data with document instances: each attachment
is, in effect, a typed map from a key to a document.

An attachment is declared on a pair of types — a concept (or club, or
`ANY_CONCEPT`) and a value type:

```js
const att = defs.createAttachment(ns, 'A_I', conceptType, Type.INT64);
```

Keys are minted from the attachment and projected to match how the value is
filed: `att.createKey().toParentKey()` for the parent concept,
`.toClubKey(club)` for a club membership, and `.toAnyConceptKey()` for an
`ANY_CONCEPT` attachment.

**When to use**: reach for an attachment whenever you need to store and
retrieve values keyed by document. {js:class}`AttachmentGetting` provides
read access (`keys`, `get`, `has`); {js:class}`AttachmentMutating` extends it
with write operations (`set`, `update`, and the collection-field ops
`unionInSet` / `subtractInSet`, `unionInMap` / `subtractInMap`,
`insertInXarray` / `updateInXarray` / `removeInXarray`).

## Quick Start

```js
const {
    CommitDatabase, CommitStateBuilder, CommitMutableState, Type,
} = require('@digitalsubstrate/dsviper');

const db = CommitDatabase.createInMemory();
db.extendDefinitions(defs.const());

// Write via AttachmentMutating
const mutableState = new CommitMutableState(CommitStateBuilder.initialState(db));
const mutating = mutableState.attachmentMutating();
mutating.set(att, key, 42);                 // INT64 document
db.commitMutations('Set A_I', mutableState);

// Read via AttachmentGetting, off the last commit
const state = CommitStateBuilder.state(db, db.lastCommitId());
const getting = state.attachmentGetting();

for (const k of getting.keys(att)) {        // keys(att) is iterable
    const doc = getting.get(att, k);        // ValueOptional
    console.log(doc.unwrap());              // INT64 unwraps to a bigint (42n)
}

db.close();
```

For a structured value type, build the document from the attachment itself:

```js
const att_s = defs.createAttachment(ns, 'ac_S', Type.ANY_CONCEPT, structType);
mutating.set(att_s, key.toAnyConceptKey(), att_s.createStructure({ f_i: 42, f_s: 'a string' }));
```

Operations on a closed `CommitDatabase`, or a commit that violates an
attachment's type constraints, throw a JS `Error` whose `name` is
`'ViperError'`.

See also: the Python {doc}`reference <../../dsviper/api/attachments>`, the
{doc}`database guide <../database>`, and the {doc}`commit <commit>` API.

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`Attachment` | A class used to represent an attachment |
| {js:class}`AttachmentGetting` | An interface used to retrieve a value (aka document) state |
| {js:class}`AttachmentMutating` | An interface used to express fine-grained mutations of a value |

## Reference

```{js:autoclass} Attachment
:members:
```

```{js:autoclass} AttachmentGetting
:members:
```

```{js:autoclass} AttachmentMutating
:members:
```
