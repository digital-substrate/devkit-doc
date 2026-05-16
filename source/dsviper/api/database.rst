Database
========

Database classes provide persistence for Viper C++ documents using SQLite or remote
connections.

**When to use**: Use ``Database`` for simple key-value persistence without
history tracking. For versioned data, see :doc:`commit`.

Quick Start
-----------

.. code-block:: python

   from dsviper import Database, DSMBuilder

   # Create or open database
   db = Database.create("data.vdb")

   # Load definitions from DSM
   builder = DSMBuilder.assemble("model.dsm")
   report, dsm_defs, defs = builder.parse()
   db.extend_definitions(defs)

   # Write (requires transaction)
   db.begin_transaction()
   db.set(attachment, key, document)
   db.commit()

   # Read
   result = db.get(attachment, key)
   if not result.is_nil():
       doc = result.unwrap()

   # Delete
   db.begin_transaction()
   db.delete(attachment, key)
   db.commit()

.. seealso::

   For detailed examples with concrete attachments, see :doc:`../database`.

Choosing the Right Class
------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 25 35

   * - Use Case
     - Class
     - Note
   * - Simple CRUD, no history
     - :class:`Database`
     - Creates ``.vdb`` files
   * - Need version history
     - :class:`CommitDatabase`
     - See :doc:`commit`
   * - Remote database access
     - :class:`DatabaseRemote`
     - Client-server mode

Core Classes
------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Database
   dsviper.DatabaseSQLite
   dsviper.DatabaseRemote
   dsviper.Databasing

Low-Level
---------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.SQLite
