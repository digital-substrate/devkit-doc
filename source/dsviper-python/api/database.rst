Database
========

Database classes provide persistence for Viper C++ documents using SQLite or remote
connections.

**When to use**: Use ``Database`` for simple key-value persistence without
history tracking. For the mutation DAG, see :doc:`commit`.

Quick Start
-----------

>>> from dsviper import *
>>> MODEL = """
... namespace MyApp {8f14e45f-ceea-467a-9575-1c14b48f0b7e} {
...     concept User;
...     struct Profile { string city; uint16 age; };
...     attachment<User, Profile> profile;
... };
... """
>>> builder = DSMBuilder()
>>> builder.append("model.dsm", MODEL)
>>> report, dsm_defs, defs = builder.parse()
>>> report.has_error()
False
>>> defs.inject(globals())             # MyApp.User, MyApp.attachments.User.profile, …
>>> key = ValueKey.create(MyApp.User, "0d2f0e1a-1111-4222-8333-444455556666")
>>> document = Value.create(MyApp.Profile, {"city": "Paris", "age": 30})

A ``Database`` holds one state, with no history. Writes go in a
transaction:

>>> db = Database.create_in_memory()
>>> db.extend_definitions(defs).count()
3
>>> db.begin_transaction()
>>> db.set(MyApp.attachments.User.profile, key, document)
True
>>> db.commit()

``get`` always returns a ``ValueOptional`` — never ``None``. Ask
``is_nil()`` whether it holds anything, and ``unwrap()`` for the document:

>>> result = db.get(MyApp.attachments.User.profile, key)
>>> result.is_nil()
False
>>> Value.dumps(result.unwrap())
{'city': 'Paris', 'age': 30}

>>> db.begin_transaction()
>>> db.delete(MyApp.attachments.User.profile, key)
True
>>> db.commit()
>>> db.get(MyApp.attachments.User.profile, key).is_nil()
True

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

.. seealso::

   To copy a ``Database``, or move content to and from a ``CommitDatabase``,
   see :doc:`transfer`.

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
