Binary Data (Blobs)
===================

Blobs provide efficient binary data storage with typed layouts and zero-copy
NumPy integration.

**When to use**: Use blobs for binary data like images, meshes, and raw buffers.
``BlobArray`` for typed arrays, ``BlobPack`` for structured multi-region data.

Quick Start
-----------

.. code-block:: python

   from dsviper import BlobLayout, BlobArray, BlobPack, BlobPackDescriptor
   import numpy as np

   # Typed array: 100 vec3 positions (float, 3 components)
   layout = BlobLayout('float', 3)
   positions = BlobArray(layout, 100)

   # Zero-copy NumPy access
   np_view = np.array(positions, copy=False)
   np_view[0] = [1.0, 2.0, 3.0]  # Modifies original

   # Structured blob: mesh with multiple regions
   desc = BlobPackDescriptor()
   desc.add_region('positions', BlobLayout('float', 3), 100)
   desc.add_region('normals', BlobLayout('float', 3), 100)
   desc.add_region('indices', BlobLayout('uint', 3), 50)
   mesh = BlobPack(desc)

   # Access region as NumPy array
   pos_np = np.array(mesh['positions'], copy=False)

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
