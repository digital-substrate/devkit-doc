# Binary Data (Blobs)

Blobs provide efficient binary data storage with typed layouts and zero-copy NumPy
integration.

**When to use**: Use blobs for binary data like images, meshes, and raw buffers.
`BlobArray` for typed arrays, `BlobPack` for structured multi-region data.

---

## Blob vs BlobId

Viper offers two DSM types for binary data:

| Type      | Use Case                       | Storage            |
|-----------|--------------------------------|--------------------|
| `blob`    | Small data (thumbnails, icons) | Inline in document |
| `blob_id` | Large data (textures, meshes)  | Database blob API  |

### blob (Inline)

A `blob` field stores binary data directly in the document. No special API needed.

### blob_id (Reference)

A `blob_id` is a SHA-1 hash referencing a blob managed by the Database blob API. This
requires the dedicated blob API:

```pycon
>>> blob_id = db.create_blob(layout, content)

>>> content = db.blob(blob_id)

>>> db.blob_ids()

>>> info = db.blob_info(blob_id)
>>> info.size()
1024
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

## BlobView (Read-Only)

A `BlobView` interprets an existing blob with a given layout (read-only). When
the layout has more than one component per element, indexing returns a tuple:

```{doctest}
>>> import struct
>>> _buf = bytearray()
>>> for i in range(100):
...     _ = _buf.extend(struct.pack('<fff', float(i), float(i*2), float(i*3)))
>>> raw = ValueBlob(bytes(_buf))

>>> view = BlobView(BlobLayout('float', 3), raw)
>>> view.count()
100
>>> view[0]
(0.0, 0.0, 0.0)
>>> view[99]
(99.0, 198.0, 297.0)
```

Use `BlobView` when you need to read blob data without copying.

## BlobArray (Read-Write)

A `BlobArray` is a typed array backed by a blob. Writes and reads use the
NumPy buffer protocol — the array exposes a *flat* `(N*components,)` view, so
reshape it to `(N, components)` to assign per-element tuples:

```{doctest}
>>> import numpy as np
>>> layout = BlobLayout('float', 3)
>>> array = BlobArray(layout, 100)

>>> np_view = np.array(array, copy=False).reshape(100, 3)
>>> np_view[0] = [1.0, 2.0, 3.0]
>>> np_view[1] = [4.0, 5.0, 6.0]

>>> view = BlobView(layout, array.blob())
>>> view[0]
(1.0, 2.0, 3.0)
>>> view[1]
(4.0, 5.0, 6.0)
```

## BlobPack - Structured Binary Data

A `BlobPack` groups multiple named regions with different layouts into a single blob. This
is ideal for complex structures like 3D meshes.

### Example: 3D Mesh Storage

A mesh has positions, normals, UVs, and triangle indices — each with a different layout.
Define the structure with a descriptor, then create the pack:

```{doctest}
>>> descriptor = BlobPackDescriptor()
>>> descriptor.add_region('positions', BlobLayout('float', 3), 4)
>>> descriptor.add_region('normals', BlobLayout('float', 3), 4)
>>> descriptor.add_region('uvs', BlobLayout('float', 2), 4)
>>> descriptor.add_region('indices', BlobLayout('uint', 3), 2)

>>> mesh = BlobPack(descriptor)
>>> len(mesh)
4
```

### Fill the Mesh Data

Each region exposes a flat NumPy view; reshape to write per-vertex tuples:

```{doctest}
>>> import numpy as np
>>> pos = np.array(mesh['positions'], copy=False).reshape(4, 3)
>>> pos[:] = [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0],
...           [ 1.0,  1.0, 0.0], [-1.0,  1.0, 0.0]]

>>> normals = np.array(mesh['normals'], copy=False).reshape(4, 3)
>>> normals[:] = [[0.0, 0.0, 1.0]] * 4

>>> uvs = np.array(mesh['uvs'], copy=False).reshape(4, 2)
>>> uvs[:] = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

>>> indices = np.array(mesh['indices'], copy=False).reshape(2, 3)
>>> indices[:] = [[0, 1, 2], [0, 2, 3]]
```

### Serialize and Restore

```{doctest}
>>> blob = mesh.blob()
>>> restored = BlobPack.from_blob(blob)

>>> np.array(restored['positions'], copy=False).reshape(4, 3)[0].tolist()
[-1.0, -1.0, 0.0]
>>> np.array(restored['indices'], copy=False).reshape(2, 3)[1].tolist()
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
>>> mesh['positions'].count()
4
>>> mesh['positions'].blob_layout()
'float-3'
>>> mesh['positions'].data_count()
12
>>> mesh['positions'].byte_count()
48
```

### Why BlobPack?

| Benefit             | Description                        |
|---------------------|------------------------------------|
| **Single blob**     | All mesh data in one blob_id       |
| **Typed regions**   | Each region has its own layout     |
| **Self-describing** | Layout metadata embedded in header |
| **Efficient**       | Direct memory mapping, no parsing  |

## NumPy Integration

`BlobArray` implements the Python Buffer Protocol, enabling zero-copy interoperability
with NumPy and other array libraries.

### Zero-Copy View

The buffer is exposed as a flat 1D array of components — reshape to give it
the geometric shape you want:

```{doctest}
>>> import numpy as np
>>> layout = BlobLayout('float', 3)
>>> positions = BlobArray(layout, 100)

>>> np_view = np.array(positions, copy=False)
>>> np_view.shape
(300,)
>>> np_view.dtype
dtype('float32')

>>> np_view.reshape(100, 3).shape
(100, 3)
```

### Bidirectional Modifications

Changes through NumPy affect the original BlobArray:

```{doctest}
>>> reshaped = np.array(positions, copy=False).reshape(100, 3)
>>> reshaped[0] = [10.0, 20.0, 30.0]

>>> view = BlobView(layout, positions.blob())
>>> view[0]
(10.0, 20.0, 30.0)
```

### Direct Memory Access

```{doctest}
>>> mv = memoryview(positions)
>>> mv.nbytes
1200
```

### BlobPack Regions

`BlobPackRegion` also supports the Buffer Protocol — same flat-then-reshape
idiom:

```{doctest}
>>> positions_np = np.array(mesh['positions'], copy=False).reshape(4, 3)
>>> normals_np = np.array(mesh['normals'], copy=False).reshape(4, 3)
>>> uvs_np = np.array(mesh['uvs'], copy=False).reshape(4, 2)

>>> positions_np.shape
(4, 3)
>>> uvs_np.shape
(4, 2)

>>> positions_np *= 2.0
>>> positions_np[0].tolist()
[-2.0, -2.0, 0.0]
```

### Why Zero-Copy Matters

| Scenario           | Without Zero-Copy   | With Zero-Copy |
|--------------------|---------------------|----------------|
| 1M vertices        | Copy 12MB           | Share pointer  |
| GPU upload         | Python → copy → C++ | Direct access  |
| Scientific compute | Data duplication    | In-place ops   |

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

Inline blobs are stored directly in the document:

```pycon
>>> thumb = Value.create(t_thumbnail)
>>> thumb.width = 64
>>> thumb.height = 64
>>> thumb.data = ValueBlob(image_bytes)

>>> mutating.set(attachment, key, thumb)
```

### Referenced Blobs (blob_id)

Use the database blob API to store and retrieve:

```pycon
>>> layout = BlobLayout('float', 3)
>>> content = ValueBlob(mesh_bytes)
>>> blob_id = db.create_blob(layout, content)

>>> texture = Value.create(t_texture)
>>> texture.width = 1024
>>> texture.height = 1024
>>> texture.pixels = blob_id

>>> mutating.set(attachment, key, texture)
```

### Retrieving Blobs

```pycon
>>> content = db.blob(blob_id)
>>> bytes(content)
b'...'

>>> chunk = db.read_blob(blob_id, size=1024, offset=0)
```

### BlobStream (Large Blobs)

For very large blobs, use streaming to avoid loading everything in memory.

**Required for blobs > 2GB**: The standard `create_blob()` API has a 2GB size limit. Use
BlobStream for larger data:

```pycon
>>> layout = BlobLayout('uchar', 1)
>>> stream = db.blob_stream_create(layout, size=100_000_000)

>>> for chunk in read_file_in_chunks("large_file.bin"):
...     db.blob_stream_append(stream, ValueBlob(chunk))

>>> blob_id = db.blob_stream_close(stream)
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

## What's Next

- [Serialization](serialization.md) - JSON and binary encoding
