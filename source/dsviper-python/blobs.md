# Binary Data (Blobs)

Blobs provide efficient binary data storage with typed layouts and zero-copy NumPy
integration.

**When to use**: Use blobs for binary data like images, meshes, and raw buffers.
`BlobArray` for typed arrays, `BlobPack` for structured multi-region data.

---

## Blob vs BlobId

Viper C++ offers two DSM types for binary data:

| Type      | Use Case                       | Storage            |
|-----------|--------------------------------|--------------------|
| `blob`    | Small data (thumbnails, icons) | Inline in document |
| `blob_id` | Large data (textures, meshes)  | Database blob API  |

### blob (Inline)

A `blob` field stores binary data directly in the document. No special API needed.

### blob_id (Reference)

A `blob_id` is a SHA-1 hash referencing a blob managed by the Database blob API. This
requires the dedicated blob API:

```{doctest}
>>> layout = BlobLayout()
>>> content = ValueBlob(bytes([1, 2, 3, 4, 5]))

>>> blob_id = db.create_blob(layout, content)
>>> blob_id
f07d73c81ed1a91165a75c5cc22253cc7895a8b2

>>> db.blob(blob_id)
blob(5)

>>> blob_id in db.blob_ids()
True

>>> info = db.blob_info(blob_id)
>>> info.size()
5
```

**Content-addressable**: The `blob_id` is computed from layout + content (SHA-1).
Identical content always produces the same `blob_id`.

**Constraint**: A document referencing a `blob_id` cannot be committed unless the blob
exists in the database. Always call `create_blob()` before using the
`blob_id` in a document.

## ValueBlob

A `ValueBlob` holds inline binary data. To pull the bytes back out, use the
`bytes()` builtin (the buffer protocol) — there is no `.bytes()` method:

```{doctest}
>>> data = bytes([1, 2, 3, 4, 5])
>>> blob = ValueBlob(data)

>>> bytes(blob)
b'\x01\x02\x03\x04\x05'

>>> len(blob)
5
```

## ValueBlobId

A `ValueBlobId` references external binary data. The id is computed from the layout
and content (deterministic SHA-1):

```{doctest}
>>> layout = BlobLayout()
>>> content = ValueBlob(bytes([1, 2, 3, 4]))
>>> blob_id = ValueBlobId(layout, content)
>>> blob_id
6b8f3ca756046be29244d9bdb6b5ca5c00468ad5

>>> ValueBlobId.try_parse("6b8f3ca756046be29244d9bdb6b5ca5c00468ad5")
6b8f3ca756046be29244d9bdb6b5ca5c00468ad5
```

## BlobLayout - Metadata Everywhere

A `BlobLayout` describes how to interpret blob bytes. This is the **Metadata Everywhere**
principle applied to binary data: the layout is metadata that gives meaning to raw bytes.

```{doctest}
>>> BlobLayout()
'uchar-1'

>>> BlobLayout('float', 3)
'float-3'

>>> BlobLayout('uint', 3)
'uint-3'

>>> BlobLayout('float', 2)
'float-2'
```

The layout enables:

- Type-safe interpretation of binary data
- Cross-platform compatibility (endianness handled)
- Validation at decode time

## Writing and reading: two sides, never the same object

A `ValueBlob` is a value. Its bytes do not change once it is made: its hash is
computed from them and kept, its `BlobId` names that content, and a server shares
it across the threads serving its clients. So writing happens **before** there is a
value, on a builder that owns the bytes; sealing hands them over.

| | by value, element by element | binary, flat |
|---|---|---|
| **write** | `BlobEncoder` → `end_encoding()` | `BlobArrayBuilder` → `build()` |
| **read** | `BlobView` | `BlobArray` |

The two readings answer the same bytes differently: `BlobView` gives one element
at a time, typed; `BlobArray` gives components and the raw bytes, without a copy.

## BlobArrayBuilder — filling one typed array

Layout and count are fixed at construction, as `std::array<T, n>` fixes them:
there is no append and no resize. Write by index, in bulk with `copy()`, or
straight through the buffer protocol.

```{doctest}
>>> builder = BlobArrayBuilder(BlobLayout('float', 3), 100)
>>> len(builder)          # components: 100 elements x 3
300
>>> builder.byte_count()
1200

>>> builder[0] = 1.5
>>> builder.copy(bytes(1200))       # a whole array at the exact size

>>> blob = builder.build()          # seals: the bytes become a value
>>> blob.size()
1200
```

`build()` **moves** the bytes rather than copying them, so no writer keeps a way
in. A spent builder refuses everything:

```{doctest}
>>> builder.is_built()
True
>>> builder[0] = 2.0
Traceback (most recent call last):
    ...
dsviper.ViperError: ...the builder handed its bytes over to a blob...
```

## BlobView — reading a blob element by element

A `BlobView` interprets an existing blob with a given layout. When the layout has
more than one component per element, indexing answers a tuple:

```{doctest}
>>> builder = BlobArrayBuilder(BlobLayout('float', 3), 100)
>>> for i in range(100):
...     builder[i * 3], builder[i * 3 + 1], builder[i * 3 + 2] = float(i), float(i * 2), float(i * 3)
>>> raw = builder.build()

>>> view = BlobView(BlobLayout('float', 3), raw)
>>> view.count()
100
>>> view[0]
(0.0, 0.0, 0.0)
>>> view[99]
(99.0, 198.0, 297.0)
```

## BlobArray — reading a blob as flat binary

`BlobArray.from_blob` reads the same bytes flat, one component per index, and
hands them out through the buffer protocol — read-only, and without a copy:

```{doctest}
>>> array = BlobArray.from_blob(BlobLayout('float', 3), raw)
>>> len(array)
300
>>> array[3]
1.0
>>> memoryview(array).readonly
True
```

## BlobPack — several regions in one blob

A `BlobPack` groups named regions of different layouts into a single blob, and
the blob carries their table: a reader finds the names, layouts and counts
without being told. It suits data written once and read whole — a buffer bound
for the GPU, a payload that travels together. Data edited attribute by attribute
is better kept as one blob per attribute, where content-addressing dedups them
and an edit rewrites only what changed.

### Example: 3D Mesh Storage

Describe the regions, fill them, seal:

```{doctest}
>>> descriptor = BlobPackDescriptor()
>>> descriptor.add_region('positions', BlobLayout('float', 3), 4)
>>> descriptor.add_region('normals', BlobLayout('float', 3), 4)
>>> descriptor.add_region('uvs', BlobLayout('float', 2), 4)
>>> descriptor.add_region('indices', BlobLayout('uint', 3), 2)

>>> builder = BlobPackBuilder(descriptor)
>>> list(builder)
['positions', 'normals', 'uvs', 'indices']
>>> builder.byte_count('positions')
48
```

`builder[name]` answers a writable `memoryview` bounded to that region and typed
by its layout. NumPy writes straight into it — reshape the flat view to assign
per-element tuples:

```{doctest}
>>> import numpy as np
>>> with builder['positions'] as region:
...     np.asarray(region).reshape(4, 3)[:] = [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0],
...                                            [1.0, 1.0, 0.0], [-1.0, 1.0, 0.0]]
>>> with builder['normals'] as region:
...     np.asarray(region).reshape(4, 3)[:] = [[0.0, 0.0, 1.0]] * 4
>>> with builder['uvs'] as region:
...     np.asarray(region).reshape(4, 2)[:] = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
>>> builder.copy('indices', np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32).tobytes())

>>> blob = builder.build()
```

The `with` block matters: a region view keeps the builder's bytes exported, and
sealing under an open view would leave that view pointing into a value. The
builder refuses, exactly as a `bytearray` refuses to resize under a `memoryview`:

```{doctest}
>>> other = BlobPackBuilder(descriptor)
>>> region = other['positions']
>>> other.build()
Traceback (most recent call last):
    ...
BufferError: cannot build while 1 region buffer(s) of this builder are live
>>> region.release()
>>> _ = other.build()
```

### Read it back

```{doctest}
>>> mesh = BlobPack.from_blob(blob)
>>> list(mesh)
['positions', 'normals', 'uvs', 'indices']
>>> mesh['positions'].count()
4
>>> mesh['positions'].blob_layout()
'float-3'

>>> np.frombuffer(mesh['positions'], dtype=np.float32).reshape(4, 3)[0].tolist()
[-1.0, -1.0, 0.0]
>>> np.frombuffer(mesh['indices'], dtype=np.uint32).reshape(2, 3)[1].tolist()
[0, 2, 3]
```

### Region Access

```{doctest}
>>> 'positions' in mesh
True
>>> 'colors' in mesh
False

>>> mesh['positions'].name()
'positions'
>>> mesh['positions'].byte_count()
48
>>> mesh['missing']
Traceback (most recent call last):
    ...
dsviper.ViperError: ...no such region missing...
```

## NumPy Integration

Both sides work without a copy, and the direction is the type: a builder's buffer
is writable, a blob's is not.

```{doctest}
>>> import numpy as np
>>> builder = BlobArrayBuilder(BlobLayout('float', 3), 100)
>>> np.asarray(builder).reshape(100, 3)[0] = [1.0, 2.0, 3.0]
>>> blob = builder.build()

>>> read = np.frombuffer(blob, dtype=np.float32)
>>> read.flags.writeable
False
>>> read[:3].tolist()
[1.0, 2.0, 3.0]
```

Prefer `np.frombuffer(blob, ...)` over `bytes(blob)`: the first hands out the
blob's own bytes, the second copies them.

## Blob in Attachments

Blobs can be used in attachments:

```dsm
// Small data inline
struct Thumbnail {
uint16 width;
uint16 height;
blob data;
// Inline binary
};

// Large data by reference
struct Texture {
uint16 width;
uint16 height;
blob_id pixels;
// External reference
};
```

## Storing Blobs in Database

### Inline Blobs

Inline blobs are stored directly in the document. The Tuto fixture
exposes a `Thumbnail` struct with a `blob` field, attached to `User` as
`avatar`:

```{doctest}
>>> user_key = TUTO_A_USER_AVATAR.create_key()

>>> thumb = TUTO_A_USER_AVATAR.create_document()
>>> thumb.width = 64
>>> thumb.height = 64
>>> thumb.data = ValueBlob(bytes([1, 2, 3, 4, 5]))
>>> thumb
{width=64, height=64, data=blob(5)}

>>> ms = CommitMutableState(CommitStateBuilder.initial_state(db))
>>> ms.attachment_mutating().set(TUTO_A_USER_AVATAR, user_key, thumb)
>>> avatar_commit = db.commit_mutations("Add avatar", ms)

>>> CommitStateBuilder.state(db, avatar_commit).attachment_getting().get(TUTO_A_USER_AVATAR, user_key)
Optional({width=64, height=64, data=blob(5)})
```

### Referenced Blobs (blob_id)

Use the database blob API to store and retrieve. The Tuto fixture
exposes a `Texture` struct with a `blob_id` field, attached to `User`
as `portrait`:

```{doctest}
>>> mesh_layout = BlobLayout()
>>> mesh_content = ValueBlob(bytes([10, 20, 30, 40]))
>>> texture_blob_id = db.create_blob(mesh_layout, mesh_content)

>>> texture = TUTO_A_USER_PORTRAIT.create_document()
>>> texture.width = 1024
>>> texture.height = 1024
>>> texture.pixels = texture_blob_id

>>> ms = CommitMutableState(CommitStateBuilder.state(db, avatar_commit))
>>> ms.attachment_mutating().set(TUTO_A_USER_PORTRAIT, user_key, texture)
>>> portrait_commit = db.commit_mutations("Add portrait", ms)

>>> CommitStateBuilder.state(db, portrait_commit).attachment_getting().get(TUTO_A_USER_PORTRAIT, user_key)
Optional({width=1024, height=1024, pixels=...})
```

### Retrieving Blobs

```{doctest}
>>> stored_id = db.create_blob(BlobLayout(), ValueBlob(bytes([10, 20, 30, 40, 50])))
>>> bytes(db.blob(stored_id))
b'\n\x14\x1e(2'

>>> db.read_blob(stored_id, size=2, offset=0)
blob(2)
```

### BlobStream (Large Blobs)

For very large blobs, use streaming to avoid loading everything in memory.

**Required for blobs > 2GB**: The standard `create_blob()` API has a 2GB size limit. Use
BlobStream for larger data:

```{doctest}
>>> stream = db.blob_stream_create(BlobLayout('uchar', 1), size=10)

>>> db.blob_stream_append(stream, ValueBlob(bytes([1, 2, 3, 4, 5])))
>>> db.blob_stream_append(stream, ValueBlob(bytes([6, 7, 8, 9, 10])))

>>> stream_blob_id = db.blob_stream_close(stream)
>>> bytes(db.blob(stream_blob_id))
b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'
```

This is essential for:

- 3D meshes with millions of vertices
- Video/audio data

## When to Use Each Type

| Scenario            | Recommendation                    |
|---------------------|-----------------------------------|
| Thumbnails (< 64KB) | Use `blob` (inline)               |
| Textures (> 1MB)    | Use `blob_id` (Database blob API) |
| Mesh geometry       | Use `blob_id` (Database blob API) |
| Icons, small images | Use `blob` (inline)               |
| Audio/video         | Use `blob_id` (Database blob API) |

