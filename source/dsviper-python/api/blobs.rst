Binary Data (Blobs)
===================

Blobs provide efficient binary data storage with typed layouts and zero-copy
NumPy integration.

**When to use**: Use blobs for binary data like images, meshes, and raw buffers.
A builder fills the bytes, ``build()`` seals them into a ``ValueBlob``, and a
reader reads them: ``BlobArray`` flat and binary, ``BlobView`` element by
element, ``BlobPack`` region by region.

Quick Start
-----------

>>> from dsviper import (BlobLayout, BlobArray, BlobArrayBuilder, BlobPack,
...                      BlobPackBuilder, BlobPackDescriptor)
>>> import numpy as np

A blob's bytes never change once it is made, so writing happens on a builder that
owns them: here 100 positions of 3 floats each.

>>> layout = BlobLayout('float', 3)
>>> builder = BlobArrayBuilder(layout, 100)

Its buffer is writable and **flat** — 300 floats, not a 100x3 matrix. Reshape it
to address elements:

>>> flat = np.asarray(builder)
>>> flat.shape
(300,)
>>> flat.reshape(100, 3)[0] = [1.0, 2.0, 3.0]

``build()`` hands the bytes over, and the value reads back read-only:

>>> del flat
>>> positions = builder.build()
>>> np.frombuffer(positions, dtype=np.float32)[:3]
array([1., 2., 3.], dtype=float32)
>>> np.frombuffer(positions, dtype=np.float32).flags.writeable
False

A ``BlobPack`` holds several regions in one blob, and carries their table:

>>> desc = BlobPackDescriptor()
>>> desc.add_region('positions', BlobLayout('float', 3), 100)
>>> desc.add_region('normals', BlobLayout('float', 3), 100)
>>> desc.add_region('indices', BlobLayout('uint', 3), 50)

>>> pack_builder = BlobPackBuilder(desc)
>>> with pack_builder['positions'] as region:
...     np.asarray(region).reshape(100, 3)[0] = [1.0, 2.0, 3.0]
>>> mesh = BlobPack.from_blob(pack_builder.build())
>>> np.frombuffer(mesh['positions'], dtype=np.float32).shape
(300,)

Choosing the Right Class
------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - Data Type
     - Class
     - Example
   * - Raw bytes
     - :class:`ValueBlob`
     - ``ValueBlob(bytes_data)``
   * - Typed array
     - :class:`BlobArray`
     - ``BlobArray.from_blob(blob)``
   * - Multiple regions
     - :class:`BlobPack`
     - Mesh with pos/normals/indices
   * - Bytes, before they are a value
     - :class:`BlobArrayBuilder`, :class:`BlobPackBuilder`
     - ``BlobArrayBuilder(layout, count)`` → ``build()``
   * - Database reference
     - :class:`ValueBlobId`
     - SHA-1 hash reference
   * - Large files (>2GB)
     - :class:`BlobStream`
     - Streaming upload

Core Classes
------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.BlobLayout
   dsviper.BlobArray
   dsviper.BlobArrayBuilder
   dsviper.BlobPack
   dsviper.BlobPackBuilder
   dsviper.BlobPackDescriptor
   dsviper.BlobPackRegion

Blob I/O
--------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.BlobStream
   dsviper.BlobEncoder
   dsviper.BlobEncoderLayout
   dsviper.BlobView
   dsviper.BlobData

Database Integration
--------------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.BlobGetting
   dsviper.BlobInfo
   dsviper.BlobStatistics
