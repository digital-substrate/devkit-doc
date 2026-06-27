# Binary Data (Blobs)

Blobs hold raw binary data — images, meshes, audio, any byte buffer — with a
typed layout that gives the bytes meaning. From Node they interoperate directly
with the standard `Buffer`. The Python equivalent is {doc}`../dsviper/blobs`; the
type system is identical, only the idiom differs (value semantics, `Buffer`
instead of `bytes`).

Examples assume the binding is in scope:

```js
const {
  Definitions, Type, TypeStructureDescriptor,
  ValueBlob, ValueBlobId, BlobLayout,
  CommitDatabase, CommitMutableState, CommitStateBuilder,
} = require('@digitalsubstrate/dsviper');
```

---

## Blob vs blob_id

Viper offers two ways to carry binary data:

| Type      | Use case                       | Storage                     |
|-----------|--------------------------------|-----------------------------|
| `blob`    | Small data (thumbnails, icons) | Inline in the document      |
| `blob_id` | Large data (textures, meshes)  | Database blob API (by hash) |

A `blob` (`ValueBlob`) stores its bytes directly. A `blob_id` (`ValueBlobId`) is
a SHA-1 hash that **references** a blob managed by the database blob API. The id
is computed from the layout plus the content, so identical content under the same
layout always yields the same id — storage is content-addressable.

## ValueBlob

A `ValueBlob` holds inline binary data. Construct it from a `Buffer`, a
`Uint8Array`, or a base64 string; pull the bytes back with `encoded()`:

```js
const blob = new ValueBlob(Buffer.from([1, 2, 3, 4]));
blob.size();                        // 4
blob.encoded();                     // <Buffer 01 02 03 04>
blob.at(0);                         // 1  (byte access)

new ValueBlob().size();             // 0  (empty by default)
new ValueBlob('aGVsbG8=').size();   // 5  (decoded from base64)
```

`encoded()` returns an independent copy — mutating the returned `Buffer` leaves
the blob untouched. The content hash is available as a hex digest:

```js
new ValueBlob(Buffer.from('hello')).sha1();
// 'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d'
```

Blobs are values, so they follow Java-like value semantics: compare with
`.equals` / `.compare`, never `==` (which is reference equality). `.equals` also
accepts a native `Buffer` directly:

```js
const a = new ValueBlob(Buffer.from('hello'));
a.equals(new ValueBlob(Buffer.from('hello')));   // true
a.equals(Buffer.from('hello'));                  // true
a.equals(new ValueBlob(Buffer.from('world')));   // false
```

## BlobLayout

A `BlobLayout` describes how to interpret the bytes of a blob: a data type plus a
component count. This is metadata that gives raw bytes their meaning. The default
layout is `uchar-1` (a plain byte blob):

```js
new BlobLayout().representation();           // 'uchar-1'
new BlobLayout('float', 3).representation();  // 'float-3'
new BlobLayout('double', 16).representation(); // 'double-16'
```

The data type is one of `uchar`, `char`, `ushort`, `short`, `uint`, `int`,
`ulong`, `long`, `half`, `float`, `double`; the component count is in the range
`[1-255]`. Inspect a layout or parse one from its string form:

```js
const layout = BlobLayout.parse('float-3');
layout.dataTypeRepresentation();    // 'float'
layout.components();                // 3
layout.byteCount();                 // 12  (3 components * 4 bytes)
layout.dataTypeByteCount();         // 4

new BlobLayout('float', 0);         // throws (components out of range [1-255])
BlobLayout.parse('float');          // throws (bad format — missing -N)
```

Layouts compare by value — `.equals` for equality, `.compare` for ordering:

```js
new BlobLayout('float', 3).equals(new BlobLayout('float', 3));   // true
new BlobLayout('uchar', 1).equals(new BlobLayout());             // true
```

## ValueBlobId

A `ValueBlobId` references external binary data. The id is derived
deterministically from a layout and the blob content:

```js
const layout = new BlobLayout('uchar', 1);
const content = new ValueBlob(Buffer.from([1, 2, 3, 4]));
const blobId = new ValueBlobId(layout, content);

blobId.equals(new ValueBlobId(layout, content));    // true — same layout + content

ValueBlobId.tryParse('zzzzzzzz');                   // undefined (not valid hex)
```

Because the id includes the layout, the same bytes under a different layout
produce a different id — `float-3` over 12 bytes is not the same blob as `int-1`
over the same 12 bytes.

## Storing and reading blobs in a database

The database blob API lives on the `CommitDatabase` (and on the value-system
`Database`). Use `createBlob(layout, blob)` to store, then `blobIds`, `blobInfo`,
`blob`, and `readBlob` to query. Writes to a `CommitDatabase` go through a
low-level transaction obtained from `commitDatabasing()`:

```js
const db = CommitDatabase.createInMemory();

const layout = BlobLayout.parse('uchar-1');
const content = new ValueBlob(Buffer.from([1, 2, 3, 4]));

const databasing = db.commitDatabasing();
databasing.beginTransaction();
const blobId = db.createBlob(layout, content);
databasing.commit();

// The stored id matches one computed directly from layout + content.
blobId.equals(new ValueBlobId(layout, content));    // true
[...db.blobIds()][0].equals(blobId);                // true

db.close();
```

`createBlob` is content-addressable: storing identical content twice returns the
same id and keeps a single copy, and rolling back the transaction discards the
blob entirely.

### Inspecting a stored blob

`blobInfo(blobId)` returns a `BlobInfo` with the id, layout, and size. The size
getters are `bigint` in some APIs — bridge to a JS number with `Number(...)`
when comparing:

```js
const databasing = db.commitDatabasing();
databasing.beginTransaction();
const blobId = db.createBlob(BlobLayout.parse('uchar-1'),
                            new ValueBlob(Buffer.from([1, 2, 3, 4])));
databasing.commit();

const info = db.blobInfo(blobId);
info.blobId().equals(blobId);               // true
info.blobLayout().representation();         // 'uchar-1'
Number(info.size());                        // 4
```

### Reading the bytes back

`blob(blobId)` returns the full `ValueBlob`; `readBlob(blobId, size, offset)`
reads `size` bytes starting at `offset`:

```js
const full = db.blob(blobId);
full.size();                                // 4
full.encoded();                             // <Buffer 01 02 03 04>

// Reading the whole blob is readBlob over its full size from offset 0.
const all = db.readBlob(blobId, info.size(), 0);
all.equals(full);                           // true
```

### Database-wide statistics

`blobStatistics()` summarises all stored blobs:

```js
const stats = db.blobStatistics();
Number(stats.count());          // number of unique blobs
Number(stats.totalSize());      // total bytes
Number(stats.minSize());
Number(stats.maxSize());
```

## Referencing a blob from a structure

A structure field of type `Type.BLOB_ID` holds a `ValueBlobId`. Declare it on the
descriptor alongside the other fields:

```js
const ds = new TypeStructureDescriptor('S');
ds.addField('f_i', Type.INT64);
ds.addField('f_s', Type.STRING);
ds.addField('f_b', Type.BLOB_ID);
```

The referenced blob must already exist in the database. Committing a structure
whose `blob_id` has no matching blob is a hard error — the commit throws. Always
`createBlob` the content **before** committing a document that references it:

```js
const mutableState = new CommitMutableState(CommitStateBuilder.initialState(db));
const attachmentMutating = mutableState.attachmentMutating();

// blobId points at a blob that was never stored
attachmentMutating.set(att, key, att.createStructure({ f_b: blobId }));

// The referenced blob is missing, so the commit throws.
db.commitMutations('Add doc', mutableState);
```

Store the blob first, and the same commit succeeds — the `blob_id` then resolves
to real bytes through the blob API shown above.

## When to use each type

| Scenario             | Recommendation                        |
|----------------------|---------------------------------------|
| Thumbnails, icons    | `blob` (inline)                       |
| Textures (> 1 MB)    | `blob_id` (database blob API)         |
| Mesh geometry        | `blob_id` (database blob API)         |
| Audio / video        | `blob_id` (database blob API)         |

For typed numeric arrays backed by a blob — meshes, vertex buffers — see
`BlobArray` and `BlobEncoder`, which encode flat JS arrays into a laid-out blob
you can then store with `createBlob`. Error handling across the blob API follows
the model in {doc}`errors`; for the surrounding commit and transaction flow see
{doc}`database`.
