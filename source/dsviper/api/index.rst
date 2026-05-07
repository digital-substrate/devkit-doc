API Reference
=============

This reference documents all public classes in the ``dsviper`` module, organized
by functional domain.

.. toctree::
   :maxdepth: 1
   :caption: Domains

   types
   values
   attachments
   database
   commit
   blobs
   serialization
   dsm
   web
   core

Overview
--------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Domain
     - Description
   * - :doc:`types`
     - Type system (``Type``, ``TypeVector``, ``TypeMap``, etc.)
   * - :doc:`values`
     - Value instances (``Value``, ``ValueString``, ``ValueVector``, etc.)
   * - :doc:`attachments`
     - Attachments (``Attachment``, ``AttachmentGetting``, ``AttachmentMutating``, etc.)
   * - :doc:`database`
     - Persistence (``Database``, ``DatabaseSQLite``, etc.)
   * - :doc:`commit`
     - Versioned persistence (``CommitDatabase``, ``CommitState``, ``AttachmentMutating``, etc.)
   * - :doc:`blobs`
     - Binary data (``BlobArray``, ``BlobPack``, ``BlobLayout``, etc.)
   * - :doc:`serialization`
     - Encoding/decoding (``Codec``, ``StreamEncoder``, etc.)
   * - :doc:`dsm`
     - Model introspection (``DSMBuilder``, ``DSMDefinitions``, etc.)
   * - :doc:`web`
     - HTML rendering (``DocumentNode``, ``Html``, etc.)
   * - :doc:`core`
     - Core utilities (``Definitions``, ``NameSpace``, ``Path``, etc.)

Reference Applications
----------------------

To see the full dsviper API in action, explore ``cdbe.py`` (CDB Editor) and
``dbe.py`` (Database Editor) in the ``tools/`` directory. These Qt/PySide6
applications demonstrate the complete capabilities of dsviper:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Capability
     - API Used
   * - **Type System**
     - ``Type``, ``TypeVector``, ``TypeMap`` for schema definition and validation
   * - **Value Handling**
     - ``Value``, ``ValueStructure``, ``ValueKey`` for typed data manipulation
   * - **Versioned Persistence**
     - ``CommitDatabase``, ``CommitState`` for DAG-based history
   * - **Mutation Context**
     - ``CommitMutableState``, ``AttachmentMutating`` for isolated evaluation
   * - **Path-Based Mutations**
     - ``Path``, ``AttachmentMutating.update()`` for multiplayer editing
   * - **Undo/Redo**
     - ``CommitStore`` for application-level undo with full state restoration
   * - **Synchronization**
     - ``CommitSynchronizer`` for fetch/push/sync with remote servers
   * - **Live Sync**
     - ``CommitStoreNotifying`` for real-time multi-user updates
   * - **Binary Assets**
     - ``BlobGetting``, ``ValueBlobId`` for large binary data management
   * - **Schema Introspection**
     - ``DSMDefinitions``, ``Definitions`` for runtime type discovery
   * - **HTML Rendering**
     - ``Html.dsm_definitions()``, ``Html.value()`` for visual inspection
   * - **Error Handling**
     - ``ViperError``, ``Error.parse()`` for structured error reporting
   * - **Logging**
     - ``Logging``, ``LoggerConsole`` for operation tracing

These tools serve as comprehensive examples for building your own dsviper applications.
