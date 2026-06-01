Commit Database
===============

The Commit Database provides transactional persistence with history tracking.

**When to use**: Use ``CommitDatabase`` for versioned persistence with history,
divergence, and sync. A ``CommitStore`` wraps an open database to expose
undo/redo and the dispatch surface for mutations.

Quick Start
-----------

.. code-block:: python

   from dsviper import CommitDatabase, CommitMutableState

   # Open commit database (created with dsm_util.py)
   db = CommitDatabase.open("model.cdb")
   db.definitions().inject()

   # Create mutable state from latest commit
   state = db.state(db.last_commit_id())
   mutable = CommitMutableState(state)

   # Apply mutations via AttachmentMutating interface
   mutating = mutable.attachment_mutating()
   mutating.set(MYAPP_A_USER, key, document)

   # Commit changes → returns new commit ID
   commit_id = db.commit_mutations("Add user", mutable)

.. seealso::

   For detailed examples and the Dual-Layer Contract, see
   :doc:`/commit/commit_database` and :doc:`/commit/commit_contract`.

Path-Based Mutations
--------------------

Use ``Path`` with ``update()`` to modify specific fields without replacing
the entire document. This enables disjoint concurrent writes — changes to
different fields converge automatically.

.. code-block:: python

   from dsviper import CommitDatabase, CommitMutableState, Path

   db = CommitDatabase.open("model.cdb")
   db.definitions().inject()

   # Build a path to a nested field: document.address.city
   path_city = Path.from_field("address").field("city").const()

   # Create mutable state
   state = db.state(db.last_commit_id())
   mutable = CommitMutableState(state)
   mutating = mutable.attachment_mutating()

   # Update only the city field (not the whole document)
   mutating.update(MYAPP_A_USER, user_key, path_city, "Paris")

   # Commit
   db.commit_mutations("Update city", mutable)

With ``set()``, concurrent edits to the same document silently lose one (last-writer-wins). With ``update()``,
edits to **different** fields converge without loss.

Supervised Reconciliation
-------------------------

Reconciling a merge — ``CommitMergeAnalyzer`` and friends — is an additive
supervisor over this API, documented on its own page:
:doc:`reconciliation`.

Database ↔ CommitDatabase Transfer
----------------------------------

Moving content between the flat ``Database`` and the versioned
``CommitDatabase`` — convert, materialize, faithful copy, and flatten — is a
set of converters documented on its own page: :doc:`transfer`.

Choosing the Right Class
------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - Use Case
     - Class
     - Example
   * - Open commit database
     - :class:`CommitDatabase`
     - ``db = CommitDatabase.open(path)``
   * - Read state at specific commit
     - :class:`CommitState`
     - ``state = db.state(commit_id)``
   * - Prepare mutations
     - :class:`CommitMutableState`
     - ``mutable = CommitMutableState(state)``
   * - Read documents (get, keys, has)
     - :class:`AttachmentGetting`
     - ``getting = state.attachment_getting()``
   * - Write documents (set, update)
     - :class:`AttachmentMutating`
     - ``mutating = mutable.attachment_mutating()``
   * - Inspect commit metadata
     - :class:`CommitHeader`
     - ``header = db.commit_header(id)``

Core Classes
------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Commit
   dsviper.CommitDatabase
   dsviper.CommitDatabaseSQLite
   dsviper.CommitDatabaseRemote
   dsviper.CommitDatabaseServer
   dsviper.CommitDatabasing

State Access
------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.CommitState
   dsviper.CommitMutableState

History & DAG
-------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.CommitNode
   dsviper.CommitNodeGrid
   dsviper.CommitNodeGridBuilder
   dsviper.CommitHeader
   dsviper.CommitData
   dsviper.CommitEvalAction

Synchronization
---------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.CommitStore
   dsviper.CommitStoreNotifying
   dsviper.CommitSynchronizer
   dsviper.CommitSynchronizerInfo
   dsviper.CommitSynchronizerInfoTransmit
   dsviper.CommitSyncData

Tracing
-------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.CommitStateTracing
   dsviper.CommitStateTrace
   dsviper.CommitStateTraceProgram
   dsviper.ValueProcessorTrace
   dsviper.ValueProcessorTraceOpcode
