Serialization
=============

Serialization classes provide binary and token-based encoding/decoding.

**When to use**: Use ``Value.encode()`` / ``Value.decode()`` for binary
serialization. Use streams for low-level I/O and custom protocols.

Quick Start
-----------

.. code-block:: python

   from dsviper import Value, ValueString, Type, Definitions

   # Create a value
   value = ValueString("hello")

   # Encode to binary blob
   blob = Value.encode(value)

   # Decode from binary (requires type and definitions)
   defs = Definitions()
   decoded = Value.decode(blob, Type.STRING, defs.const())

   # Works with any type
   from dsviper import TypeVector, ValueVector
   t_vec = TypeVector(Type.INT64)
   vec = Value.create(t_vec, [1, 2, 3])
   blob = Value.encode(vec)
   decoded = Value.decode(blob, t_vec, defs.const())

JSON Serialization
------------------

For web integration and REST APIs, use ``Value.json_encode()`` and ``Value.json_decode()``.

.. code-block:: python

   from dsviper import Value, ValueString, Type, Definitions

   # Encode primitive to JSON
   value = ValueString("hello")
   json_str = Value.json_encode(value)  # '"hello"'

   # Decode JSON (requires type and definitions)
   defs = Definitions()
   decoded = Value.json_decode(json_str, Type.STRING, defs.const())

Flask REST API Example
^^^^^^^^^^^^^^^^^^^^^^

Real-world pattern for exposing Viper C++ data via REST:

.. code-block:: python

   from flask import Flask, make_response
   from dsviper import CommitDatabase, Value

   app = Flask(__name__)

   @app.get("/material/<uuid:instance_id>")
   def material_api(instance_id):
       db = CommitDatabase.open("model.cdb")
       doc = db.state(db.last_commit_id()).attachment_getting().get(
           MYAPP_A_Material, ValueKey.create(MYAPP_C_Material, str(instance_id))
       )
       db.close()

       # Encode document to JSON with indentation
       json_string = Value.json_encode(doc, indent=2)
       res = make_response(json_string)
       res.mimetype = "application/json"
       return res

DSM schema can also be exported for client-side validation:

.. code-block:: python

   @app.get("/schema")
   def schema_api():
       db = CommitDatabase.open("model.cdb")
       dsm_defs = db.definitions().to_dsm_definitions()
       db.close()

       json_string = dsm_defs.json_encode(indent=2)
       res = make_response(json_string)
       res.mimetype = "application/json"
       return res

Choosing the Right Approach
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - Use Case
     - API
     - Note
   * - Binary serialization
     - ``Value.encode()``
     - Default codec
   * - Binary deserialization
     - ``Value.decode()``
     - Requires type + definitions
   * - JSON for web APIs
     - ``Value.json_encode()``
     - REST/web integration
   * - Custom codec
     - ``Codec.STREAM_*``
     - Raw, binary, token formats
   * - File I/O
     - ``StreamWriterFile``
     - Low-level streaming

Codec
-----

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Codec
   dsviper.StreamCodecInstancing

Binary Streams
--------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.StreamBinaryReader
   dsviper.StreamBinaryWriter
   dsviper.StreamTokenBinaryReader
   dsviper.StreamTokenBinaryWriter

Stream I/O
----------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.StreamReaderBlob
   dsviper.StreamReaderFile
   dsviper.StreamReaderSharedMemory
   dsviper.StreamWriterBlob
   dsviper.StreamWriterFile
   dsviper.StreamWriterSharedMemory

Protocols
---------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.StreamReading
   dsviper.StreamWriting
   dsviper.StreamEncoding
   dsviper.StreamDecoding
   dsviper.StreamSizing

Raw Streams
-----------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.StreamRawReader
   dsviper.StreamRawWriter
   dsviper.StreamRawReading
   dsviper.StreamRawWriting
