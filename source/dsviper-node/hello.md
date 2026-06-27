# Hello dsviper

The shortest possible end-to-end use of the runtime from Node.js — define a
tiny schema, write a record in a commit, read it back. This is the Node twin
of the Python {doc}`../dsviper/hello` page.

```js
const {
  Definitions, NameSpace, ValueUUId, Type,
  CommitDatabase, CommitMutableState, CommitStateBuilder,
} = require('@digitalsubstrate/dsviper');

// 1. Describe a schema: one namespace, one concept, one attachment.
//    An attachment<User, INT64> maps a User key to an INT64 document.
const defs = new Definitions();
const ns = new NameSpace(ValueUUId.create(), 'Tuto');
const User = defs.createConcept(ns, 'User');
const score = defs.createAttachment(ns, 'score', User, Type.INT64);

// 2. Open an in-memory database and seal the schema into it.
const db = CommitDatabase.createInMemory();
db.extendDefinitions(defs.const());

// 3. Mint a typed key and stage a write on a mutable state.
const alice = score.createKey();              // a fresh User key
const state = new CommitMutableState(CommitStateBuilder.initialState(db));
state.attachmentMutating().set(score, alice, 42);

// 4. Land the staged mutations as a single commit.
db.commitMutations('Set alice score', state);

// 5. Read back through the state at the latest commit.
const getting = CommitStateBuilder.state(db, db.lastCommitId()).attachmentGetting();
const got = getting.get(score, alice);        // a ValueOptional
console.log(got.unwrap());                     // 42n  (INT64 round-trips as bigint)

// 6. Release the native handle.
db.close();
console.log(db.isClosed());                    // true
```

What this exercises:

- **Typed schema** — `Definitions` collects the type universe. `createConcept`
  declares the `User` identity, and `createAttachment` declares an
  `attachment<User, INT64>`: a typed map from a `User` key to an INT64
  document. `defs.const()` freezes the schema so the database can adopt it via
  `extendDefinitions`.
- **Typed handles** — `score` is the runtime handle for that attachment.
  `createKey()` mints a fresh `User` key; passing a JS `42` to `set` is coerced
  into the attachment's INT64 document type at the boundary.
- **Transactional write** — `CommitMutableState` accumulates the staged
  mutations; `commitMutations()` lands them as a single commit in the DAG.
- **Type-safe read** — read back through the state at the latest commit via
  `attachmentGetting().get(...)`, which returns a `ValueOptional`. Calling
  `.unwrap()` peels it to the native value — here a `bigint`, because INT64
  values round-trip as JS `bigint` (e.g. `42n`). A type mismatch on either
  side would have raised at the boundary.

```{note}
Values follow Java-like semantics: compare with `.equals()` (which accepts a
native argument directly), never `==`. A thrown Viper runtime error surfaces as
a JS `Error` whose `.name` is `'ViperError'` — see {doc}`errors`.
```

In real projects you obtain these handles either by importing the
Kibo-generated package (the static API) or by loading a DSM model at runtime
(the dynamic API — see {doc}`dsm`).

For the full lifecycle — values and types, collections, structures, blobs, and
the mutation DAG — continue with {doc}`types_values`, {doc}`database`, and the
other pages in this section.
