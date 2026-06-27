# Binary data (blobs)

Blobs store raw binary payloads — images, meshes, buffers — under a typed
{js:class}`BlobLayout` that records the element data type (`float`, `int`,
`uchar`, ...) and its component count. A blob's bytes live in a
{js:class}`ValueBlob`; storing one in a database yields a content-addressable
{js:class}`ValueBlobId` (the SHA-1 of layout + bytes), so identical payloads
deduplicate automatically.

**When to use**: reach for blobs when a value is best expressed as a packed
byte buffer rather than a structured Viper value. {js:class}`BlobLayout`
describes the element shape; {js:class}`BlobEncoder` packs typed elements into a
{js:class}`ValueBlob`; {js:class}`BlobArray` and {js:class}`BlobView`
reinterpret those bytes as a sequence of typed elements; and the database blob
API (`createBlob`, `blob`, `blobInfo`) persists and retrieves them by id.

## Quick Start

```js
const {
  BlobLayout, BlobEncoder, BlobArray, ValueBlob, ValueBlobId, Database,
} = require('@digitalsubstrate/dsviper');

// A layout: 3-component float elements (e.g. vec3 positions).
const layout = new BlobLayout('float', 3);
layout.representation();   // 'float-3'
layout.components();       // 3
layout.byteCount();        // 12  (3 * 4 bytes)

// Layouts also parse from their string form.
BlobLayout.parse('uchar-1').representation();   // 'uchar-1'

// Pack typed elements into a blob with an encoder. The Node BlobArray is a
// read-only view, so build data through BlobEncoder, then reinterpret it.
const enc = new BlobEncoder(layout);
enc.write([1.0, 2.0, 3.0]);   // one 3-component element
enc.write([4.0, 5.0, 6.0]);
const blob = enc.endEncoding();   // -> ValueBlob

// Reinterpret the bytes as a typed array; iterate to read elements back.
const array = BlobArray.fromBlob(layout, blob);
const elems = [...array];     // ValueVec rows of 3 components
elems[0].at(0);               // 1.0

// Raw bytes round-trip through ValueBlob directly.
const raw = new ValueBlob(Buffer.from([1, 2, 3, 4]));
raw.size();                   // 4
raw.sha1();                   // hex digest of the bytes

// Persist to a database: createBlob returns a content-addressable id.
const db = Database.createInMemory();
db.beginTransaction();
const blobId = db.createBlob(layout, blob);
db.commit();

const info = db.blobInfo(blobId);
Number(info.size());                  // byte count (BlobInfo.size() is a BigInt)
info.blobLayout().representation();   // 'float-3'
db.blob(blobId).equals(blob);         // true
db.close();
```

**Content-addressable storage**: `createBlob` hashes layout plus bytes,
so writing the same payload twice yields the same {js:class}`ValueBlobId` and is
stored once. A different layout over the same bytes is a different id.

## Choosing the right class

| Need | Class | Example |
|------|-------|---------|
| Raw byte payload | {js:class}`ValueBlob` | `new ValueBlob(Buffer.from([...]))` |
| Element shape (data type + components) | {js:class}`BlobLayout` | `new BlobLayout('float', 3)` |
| Pack typed elements into bytes | {js:class}`BlobEncoder` | `enc.write(...)`, `enc.endEncoding()` |
| Read bytes back as typed elements | {js:class}`BlobArray` / {js:class}`BlobView` | `BlobArray.fromBlob(layout, blob)` |
| Database reference (content-addressed) | {js:class}`ValueBlobId` | `new ValueBlobId(layout, blob)` |
| Stored-blob metadata and stats | {js:class}`BlobInfo` / {js:class}`BlobStatistics` | `db.blobInfo(id)` |
| Stream a large blob in chunks | {js:class}`BlobStream` | `db.blobStreamCreate(layout, size)` |

{tip}
The full database blob surface — `createBlob`, `createBlobFromBuffer`,
`blobIds`, `blob`, `readBlob`, `blobInfo`, `blobInfos`, `blobStatistics`, and
the `blobStreamCreate`/`blobStreamAppend`/`blobStreamClose` streaming API — is
documented on {doc}`database`. The Python counterpart of this page is
{doc}`../../dsviper/api/blobs`.
{/tip}

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`BlobArray` | A class used to reinterpret the blob of the internal BlobView as an array<blob_layout.data_type> |
| {js:class}`BlobData` | A class used to represent the data associated with a blob during the synchronization of two databases |
| {js:class}`BlobEncoder` | A class used to encode a blob |
| {js:class}`BlobEncoderLayout` | A class used to represent the layout of one element |
| {js:class}`BlobGetting` | An interface used to retrieve blobs from a persistence layer |
| {js:class}`BlobInfo` | A class used to represent various information of a blob in the persistence layer |
| {js:class}`BlobLayout` | A class used to describe the layout of the element in a blob |
| {js:class}`BlobPack` | A class used to implements memory regions in one blob |
| {js:class}`BlobPackDescriptor` | A class used to describe binary regions |
| {js:class}`BlobPackRegion` | A class used for a region that implement the buffer protocol |
| {js:class}`BlobStatistics` | A class used to represent the statistics about blobs |
| {js:class}`BlobStream` | A class used to copy a huge blob (> 2GB) to a database |
| {js:class}`BlobView` | A class used to interpret the bytes of a blob from the layout |

## Reference

```{js:autoclass} BlobArray
:members:
```

```{js:autoclass} BlobData
:members:
```

```{js:autoclass} BlobEncoder
:members:
```

```{js:autoclass} BlobEncoderLayout
:members:
```

```{js:autoclass} BlobGetting
:members:
```

```{js:autoclass} BlobInfo
:members:
```

```{js:autoclass} BlobLayout
:members:
```

```{js:autoclass} BlobPack
:members:
```

```{js:autoclass} BlobPackDescriptor
:members:
```

```{js:autoclass} BlobPackRegion
:members:
```

```{js:autoclass} BlobStatistics
:members:
```

```{js:autoclass} BlobStream
:members:
```

```{js:autoclass} BlobView
:members:
```
