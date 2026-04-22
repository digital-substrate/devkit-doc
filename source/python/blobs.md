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
# Store blob → get blob_id
>>> blob_id = db.create_blob(layout, content)

# Retrieve blob by blob_id
>>> content = db.blob(blob_id)

# List all blob_ids in database
>>> db.blob_ids()

# Get blob metadata
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

A `ValueBlob` holds inline binary data:

```pycon
>>> from dsviper import *

# Create blob from bytes
>>> data = bytes([1, 2, 3, 4, 5])
>>> blob = ValueBlob(data)

# Access bytes
>>> blob.bytes()
b'\x01\x02\x03\x04\x05'

>>> len(blob)
5
```

## ValueBlobId

A `ValueBlobId` references external binary data. The ID is computed from the blob's layout
and content:

```pycon
# Create blob_id from layout and content
>>> layout = BlobLayout()
>>> content = ValueBlob(bytes([1, 2, 3, 4]))
>>> blob_id = ValueBlobId(layout, content)
>>> blob_id
'6b8f3ca756046be29244d9bdb6b5ca5c00468ad5'

# Parse blob_id from string
>>> blob_id = ValueBlobId.try_parse("6b8f3ca756046be29244d9bdb6b5ca5c00468ad5")
```

## BlobLayout - Metadata Everywhere

A `BlobLayout` describes how to interpret blob bytes. This is the **Metadata Everywhere**
principle applied to binary data: the layout is metadata that gives meaning to raw bytes.

```pycon
>>> from dsviper import *

# Default layout: array of unsigned bytes
>>> BlobLayout()
'uchar-1'

# 3D positions: array of (float, float, float)
>>> BlobLayout('float', 3)
'float-3'

# Triangle indices: array of (uint, uint, uint)
>>> BlobLayout('uint', 3)
'uint-3'

# UV coordinates: array of (float, float)
>>> BlobLayout('float', 2)
'float-2'
```

The layout enables:

- Type-safe interpretation of binary data
- Cross-platform compatibility (endianness handled)
- Validation at decode time

## BlobView (Read-Only)

A `BlobView` interprets an existing blob with a given layout (read-only):

```pycon
>>> from dsviper import *

# Existing blob from database
>>> blob = db.blob(blob_id)

# Interpret as vec3 positions
>>> view = BlobView(BlobLayout('float', 3), blob)
>>> view.count()
100

# Read elements
>>> view[0]
(1.0, 2.0, 3.0)
>>> view[99]
(10.0, 20.0, 30.0)
```

Use `BlobView` when you need to read blob data without copying.

## BlobArray (Read-Write)

A `BlobArray` is a typed array backed by a blob:

```pycon
# Create array of 100 vec3 positions
>>> layout = BlobLayout('float', 3)
>>> array = BlobArray(layout, 100)

# Write elements as tuples
>>> array[0] = (1.0, 2.0, 3.0)
>>> array[1] = (4.0, 5.0, 6.0)

# Read back
>>> array[0]
(1.0, 2.0, 3.0)

# Properties
>>> array.count()       # 100 elements
>>> array.data_count()  # 300 floats (100 × 3)
>>> array.byte_count()  # 1200 bytes (300 × 4)
```

## BlobPack - Structured Binary Data

A `BlobPack` groups multiple named regions with different layouts into a single blob. This
is ideal for complex structures like 3D meshes.

### Example: 3D Mesh Storage

A mesh has positions, normals, UVs, and triangle indices—each with a different layout:

```pycon
>>> from dsviper import *

# Define the mesh structure
>>> descriptor = BlobPackDescriptor()
>>> descriptor.add_region('positions', BlobLayout('float', 3), 4)  # 4 vec3
>>> descriptor.add_region('normals', BlobLayout('float', 3), 4)    # 4 vec3
>>> descriptor.add_region('uvs', BlobLayout('float', 2), 4)        # 4 vec2
>>> descriptor.add_region('indices', BlobLayout('uint', 3), 2)     # 2 triangles

# Create the pack
>>> mesh = BlobPack(descriptor)
>>> len(mesh)
4
```

### Fill the Mesh Data

```pycon
# Quad vertices (4 corners)
>>> mesh['positions'][0] = (-1.0, -1.0, 0.0)
>>> mesh['positions'][1] = (1.0, -1.0, 0.0)
>>> mesh['positions'][2] = (1.0, 1.0, 0.0)
>>> mesh['positions'][3] = (-1.0, 1.0, 0.0)

# Normals (all facing +Z)
>>> for i in range(4):
...     mesh['normals'][i] = (0.0, 0.0, 1.0)

# UVs
>>> mesh['uvs'][0] = (0.0, 0.0)
>>> mesh['uvs'][1] = (1.0, 0.0)
>>> mesh['uvs'][2] = (1.0, 1.0)
>>> mesh['uvs'][3] = (0.0, 1.0)

# Two triangles forming the quad
>>> mesh['indices'][0] = (0, 1, 2)
>>> mesh['indices'][1] = (0, 2, 3)
```

### Serialize and Restore

```pycon
# Serialize to a single blob
>>> blob = mesh.blob()

# Store in database
>>> blob_id = db.create_blob(BlobLayout(), blob)

# Later: restore from blob
>>> restored = BlobPack.from_blob(blob)
>>> restored['positions'][0]
(-1.0, -1.0, 0.0)
>>> restored['indices'][1]
(0, 2, 3)
```

### Region Access

```pycon
# Check if region exists
>>> 'positions' in mesh
True
>>> 'colors' in mesh
False

# Get region info
>>> vertices = mesh['positions']
>>> vertices.name()
'positions'
>>> vertices.count()
4
>>> vertices.blob_layout()
'float-3'
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

```pycon
>>> import numpy as np
>>> from dsviper import *

# Create a BlobArray of vec3 positions
>>> layout = BlobLayout('float', 3)
>>> positions = BlobArray(layout, 100)

# Get NumPy view (no copy!)
>>> np_view = np.array(positions, copy=False)
>>> np_view.shape
(100, 3)
>>> np_view.dtype
dtype('float32')
```

### Bidirectional Modifications

Changes through NumPy affect the original BlobArray:

```pycon
# Modify via NumPy
>>> np_view[0] = [10.0, 20.0, 30.0]

# Original is updated
>>> positions[0]
(10.0, 20.0, 30.0)
```

### Direct Memory Access

```pycon
# memoryview for low-level access
>>> mv = memoryview(positions)
>>> mv.nbytes
1200  # 100 × 3 × 4 bytes

# Bulk copy from bytes
>>> source = b'\x00\x00\x80\x3f...'  # binary data
>>> positions.copy(source)
```

### BlobPack Regions

`BlobPackRegion` also supports the Buffer Protocol:

```pycon
# Access mesh regions as NumPy arrays
>>> positions_np = np.array(mesh['positions'], copy=False)
>>> normals_np = np.array(mesh['normals'], copy=False)
>>> uvs_np = np.array(mesh['uvs'], copy=False)

>>> positions_np.shape
(4, 3)
>>> uvs_np.shape
(4, 2)

# Transform all positions at once
>>> positions_np *= 2.0  # Scale mesh
>>> mesh['positions'][0]
(-2.0, -2.0, 0.0)
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
# Store blob via Database blob API
>>> layout = BlobLayout('float', 3)
>>> content = ValueBlob(mesh_bytes)
>>> blob_id = db.create_blob(layout, content)

# Use blob_id in document
>>> texture = Value.create(t_texture)
>>> texture.width = 1024
>>> texture.height = 1024
>>> texture.pixels = blob_id

>>> mutating.set(attachment, key, texture)
```

### Retrieving Blobs

```pycon
# Get blob by ID
>>> content = db.blob(blob_id)
>>> content.bytes()
b'...'

# Partial read (for large blobs)
>>> chunk = db.read_blob(blob_id, size=1024, offset=0)
```

### BlobStream (Large Blobs)

For very large blobs, use streaming to avoid loading everything in memory.

**Required for blobs > 2GB**: The standard `create_blob()` API has a 2GB size limit. Use
BlobStream for larger data:

```pycon
# Create a stream for a 100MB blob
>>> layout = BlobLayout('uchar', 1)
>>> stream = db.blob_stream_create(layout, size=100_000_000)

# Write in chunks
>>> for chunk in read_file_in_chunks("large_file.bin"):
    ...
db.blob_stream_append(stream, ValueBlob(chunk))

# Close stream → get blob_id
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
