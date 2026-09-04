Binary Data (Blobs)
===================

Blobs provide efficient binary data storage with typed layouts and zero-copy
NumPy integration.

**When to use**: Use blobs for binary data like images, meshes, and raw buffers.
``BlobArray`` for typed arrays, ``BlobPack`` for structured multi-region data.

Quick Start
-----------

>>> from dsviper import BlobLayout, BlobArray, BlobPack, BlobPackDescriptor
>>> import numpy as np

A ``BlobArray`` is a typed array: here 100 positions of 3 floats each.

>>> layout = BlobLayout('float', 3)
>>> positions = BlobArray(layout, 100)

The NumPy view is zero-copy and **flat** — 300 floats, not a 100x3 matrix.
Reshape it to address elements:

>>> flat = np.array(positions, copy=False)
>>> flat.shape
(300,)
>>> view = flat.reshape(100, 3)
>>> view[0] = [1.0, 2.0, 3.0]
>>> np.array(positions, copy=False)[:3]      # the write went through
array([1., 2., 3.], dtype=float32)

A ``BlobPack`` holds several regions in one blob:

>>> desc = BlobPackDescriptor()
>>> desc.add_region('positions', BlobLayout('float', 3), 100)
>>> desc.add_region('normals', BlobLayout('float', 3), 100)
>>> desc.add_region('indices', BlobLayout('uint', 3), 50)
>>> mesh = BlobPack(desc)
>>> np.array(mesh['positions'], copy=False).shape
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
     - ``BlobArray(layout, count)``
   * - Multiple regions
     - :class:`BlobPack`
     - Mesh with pos/normals/indices
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
   dsviper.BlobPack
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
