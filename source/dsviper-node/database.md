# Database

`CommitDatabase` is the commit-based persistence layer: an immutable,
append-only mutation DAG with full history. A *state* is never stored on its
own — it is rebuilt on demand from the trace of mutations leading to a commit.

| Concept                | Role                                              |
|------------------------|---------------------------------------------------|
| `CommitDatabase`       | The store — the mutation DAG and its blobs        |
| `CommitMutableState`   | Stages writes, then sealed into a commit          |
| `CommitState`          | A read-only snapshot reconstructed at a commit    |
| `Path`                 | Navigates / edits a portion of a nested value     |

This page is the Node twin of the Python {doc}`../dsviper/database` and its
companion {doc}`../commit/index` overview, which explain the reconstruction
pipeline (the DAG, linearization, last-writer-wins) in depth. Here we cover the
Node lifecycle: create, define, mutate, commit, read — and the `Path` primitive
that the {doc}`structures` page relies on for deep mutation.

```js
const {
  Definitions, NameSpace, ValueUUId, Type, TypeStructureDescriptor,
  CommitDatabase, CommitMutableState, CommitStateBuilder, Path,
} = require('@digitalsubstrate/dsviper');
```

---

## Creating a database

```js
const db = CommitDatabase.createInMemory();

db.path();          // 'InMemory'
db.codecName();     // 'StreamBinary'
db.documentation(); // 'In Memory'
db.uuid().isValid(); // true
```

---

## Setting up definitions

A database is empty until you extend it with a set of definitions — the schema
your documents conform to. `extendDefinitions` takes a *const* (frozen) view:

```js
const defs = new Definitions();
const ns = new NameSpace(ValueUUId.create(), 'Test');

// Types
const t_A = defs.createConcept(ns, 'A');

const ds_S = new TypeStructureDescriptor('S');
ds_S.addField('f_i', Type.INT64);
ds_S.addField('f_s', Type.STRING);
const t_S = defs.createStructure(ns, ds_S);

// Attachments — a key type and a document type
const a_A = defs.createAttachment(ns, 'A_I', t_A, Type.INT64);
const a_S = defs.createAttachment(ns, 'A_S', Type.ANY_CONCEPT, t_S);

db.extendDefinitions(defs.const());
defs.const().isEqual(db.definitions()); // true
```

In your own code the definitions usually come from a parsed DSM model rather
than being assembled by hand — see {doc}`dsm`.

---

## Writing — stage, then commit

All writes go through a `CommitMutableState` built from the database's initial
state. You stage documents on its mutating handle, then seal the batch into a
single commit:

```js
const state = new CommitMutableState(CommitStateBuilder.initialState(db));
const m = state.attachmentMutating();

const key = a_A.createKey().toParentKey();

m.set(a_A, key, 42);
m.set(a_S, key.toAnyConceptKey(), a_S.createStructure({ f_i: 42, f_s: 'a string' }));

const commitId = db.commitMutations('Initial import', state);
```

`commitMutations` returns the `ValueCommitId` of the sealed commit. The same id
is available afterwards as `db.lastCommitId()`.

The staged values are readable back from the mutable state before the commit —
its `attachmentMutating()` exposes `get`, `keys` and `has`, and its
`attachmentGetting()` gives the same read-only view. `keys(att)` is an iterable
set; `get(att, key)` is a `ValueOptional`:

```js
[...m.keys(a_A)][0].equals(key); // true
m.get(a_A, key).unwrap();        // 42n  (INT64 unwraps to bigint)
```

---

## Reading — reconstruct a snapshot

A read is a *reconstruction*, not a retrieval: `CommitStateBuilder.state`
replays the linearized mutation trace onto the initial state up to a commit and
hands you an immutable `CommitState`.

```js
const s = CommitStateBuilder.state(db, db.lastCommitId());
const g = s.attachmentGetting();

[...g.keys(a_A)][0].equals(key); // true
g.get(a_A, key).unwrap();        // 42n
```

`get` returns a `ValueOptional` — `.unwrap()` peels it to the document. Value
semantics are Java-like: compare with `.equals()` (which accepts a native
argument), never with `==` between two Values (that is reference equality).

How a document unwraps depends on its type:

```js
// INT64 -> bigint
g.get(a_A, key).unwrap();                        // 42n

// structure -> ValueStructure; read fields via .at(), compare via .equals()
const doc = g.get(a_S, key.toAnyConceptKey()).unwrap();
doc.at('f_i');                                   // 42n
doc.equals(a_S.createStructure({ f_i: 42, f_s: 'a string' })); // true
```

A scalar stored under an `ANY` attachment comes back boxed in a `ValueAny`, so
it needs a second `.unwrap()` to reach the native; a container (e.g. a
`ValueTuple`) under `ANY` comes back directly.

---

## Lifecycle and closed-database errors

Close a database when you are done with it:

```js
db.close();
db.isClosed(); // true
```

A thrown Viper runtime error is an ordinary JS `Error` whose `.name` is
`'ViperError'`. Calling into a closed database throws it:

```js
const isViperError = (e) => e.name === 'ViperError';

const closed = CommitDatabase.createInMemory();
closed.close();

assert.throws(() => closed.definitions(),   isViperError);
assert.throws(() => closed.uuid(),          isViperError);
assert.throws(() => closed.codecName(),     isViperError);
assert.throws(() => closed.headCommitIds(), isViperError);
```

---

## Path — navigating a nested value

`Path` is the spine of the mutating API. A path locates one portion of a nested
value, and the same path object can both *read* and *edit* that location. It is
how deep updates address a field inside a structure, an element of a vector, an
entry of a map, and so on. The {doc}`structures` page links here whenever a
mutation reaches below the top level of a document.

### Building a path

A path is a chain of components. Construct one with a static factory and extend
it fluently. Because JavaScript has no operator overloading, the `/` operator
the Python API uses (`path / 'f'`) maps to the fluent `.field('f')` here — they
are the same building block:

```js
// these two are equivalent
Path.fromField('f_x');
new Path().field('f_x');
```

Each step appends a component and returns the path, so steps chain:

```js
const p = new Path()
  .field('f_opt_s') // into a structure field
  .unwrap()         // through an optional
  .field('f_x')     // into a nested structure field
  .const();
```

Calling `.const()` freezes the path into its read-only `PathConst` view, which
is what you navigate and serialize with.

The component kinds (and their fluent / static forms):

| Step          | Fluent           | Static                | Navigates                    |
|---------------|------------------|-----------------------|------------------------------|
| Field         | `.field('f')`    | `Path.fromField('f')` | a structure field            |
| Index         | `.index(0)`      | `Path.fromIndex(0)`   | a vector / tuple position     |
| Key           | `.key(k)`        | `Path.fromKey(k)`     | a map entry by key           |
| Position      | `.position(uuid)`| `Path.fromPosition(uuid)` | an xarray slot by position |
| Unwrap        | `.unwrap()`      | `Path.fromUnwrap()`   | through an optional          |

### Navigating and editing a value

A `PathConst` reads the located value with `.at(value)` and writes it with
`.set(value, native)`. Validate the shape against a schema first with
`.checkType(struct)`, which returns the leaf type:

```js
const value = a_S.createStructure({ f_i: 7, f_s: 'x' });

const fp = new Path().field('f_i').const();
fp.checkType(t_S);   // returns the leaf type (INT64)
fp.at(value);        // 7n
fp.set(value, 9);
fp.at(value);        // 9n
```

`.isApplicable(value)` reports whether a path actually resolves on a given value
at runtime (e.g. an optional it crosses is present, an index is in bounds),
without throwing. Navigating past a nil optional or an out-of-range index throws
a `ViperError`.

### Inspecting components

`.components()` returns the path's `PathComponent` list. A component reports its
`.type()` (`'Field'`, `'Index'`, `'Key'`, `'Position'`, `'Unwrap'`, …) and its
`.value()` as a native:

```js
const c = Path.fromField('f_x').const().components()[0];
c.type();  // 'Field'
c.value(); // 'f_x'

Path.fromIndex(42).const().components()[0].value(); // 42n  (Index -> bigint)
Path.fromUnwrap().const().components()[0].value();  // null (Unwrap has no value)
```

A `Field` component's value is a string, an `Index` is a `bigint`, a scalar
`Key` is the native number/string, and a tuple `Key` is a wrapped Value.

### Serializing a path

A path encodes to a `ValueBlob` through the default binary stream codec, and
`Path.decode` is its inverse — it needs the const definitions to resolve the
types it crosses:

```js
const p = new Path().field('f_i').const();
const blob = p.encode();

const decoded = Path.decode(blob, defs.const());
p.representation() === decoded.const().representation(); // true
```

---

## Deep mutation through a path

The mutating handle uses a path to update inside a staged document without
re-setting it whole. `update` rewrites a single location; collection fields have
their own operations — `unionInSet` / `subtractInSet`, `unionInMap` /
`subtractInMap`, and `insertInXarray` / `updateInXarray` / `removeInXarray`:

```js
const state = new CommitMutableState(CommitStateBuilder.initialState(db));
const m = state.attachmentMutating();
const acKey = a_A.createKey().toAnyConceptKey();

m.set(a_S, acKey, a_S.createStructure());
m.update(a_S, acKey, new Path().field('f_i').const(), 42);

m.get(a_S, acKey).unwrap().at('f_i'); // 42n
```

See {doc}`structures` for the full set of collection-field operations and the
value handles (`ValueSet`, `ValueMap`, `ValueXArray`) they take.
