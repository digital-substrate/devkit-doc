Database Transfer
=================

Four converters move documents and blobs between :class:`Database` and
:class:`CommitDatabase` stores, in every combination of the two.

Each converter takes **pre-opened source and target handles** — never
filesystem paths — so a transfer works over both local and remote transports.
Every direction returns a :class:`DatabaseTransferInfo` reporting how many
documents and blobs it moved.

**When to use**: Use a converter when data must change store kind or be
replicated — not to read or mutate it in place, which is what
:doc:`database` and :doc:`commit` are for.

.. seealso::

   :doc:`/commit/commit_database` — the ``CommitDatabase`` model, including
   the **Flatten** pattern that :class:`CommitDatabaseFlattener` automates.

The four directions
-------------------

.. list-table::
   :header-rows: 1
   :widths: 18 18 36 28

   * - From
     - To
     - Class / method
     - Blobs kept
   * - ``Database``
     - ``Database``
     - :class:`DatabaseCopier` — ``.copy(source, target)``
     - **All**, including orphans — a faithful replica
   * - ``Database``
     - ``CommitDatabase``
     - :class:`DatabaseToCommitDatabaseConverter` — ``.convert(source, target, label)``
     - Only those the documents reference
   * - ``CommitDatabase``
     - ``Database``
     - :class:`CommitDatabaseToDatabaseConverter` — ``.convert(source, commit_id, target)``
     - Only those the chosen commit references
   * - ``CommitDatabase``
     - ``CommitDatabase``
     - :class:`CommitDatabaseFlattener` — ``.flatten(source, commit_id, target, label)``
     - Only those the chosen commit references

The two converters that target a ``CommitDatabase`` write the source state as a
**single commit** under an explicit ``label``; the two that read from one take
an explicit ``commit_id`` and reconstruct that commit's state. There is no
implicit current commit.

Blob handling
-------------

Only :class:`DatabaseCopier` preserves orphan blobs, because it is the one
faithful 1:1 replica. The three converters that *narrow* — into a commit, into
a flat state, or into a single-commit history — first collect the blobs the
resulting state actually references and copy only those, dropping orphans on
the ``Database`` side and superseded history blobs on the ``CommitDatabase``
side.

Blobs are streamed in 64 MiB chunks, so payloads larger than 2 GB transfer
without failing.

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
>>> defs.inject(globals())             # MY_APP_T_USER, MY_APP_A_USER_PROFILE, …
>>> key = ValueKey.create(MY_APP_T_USER, "0d2f0e1a-1111-4222-8333-444455556666")
>>> document = Value.create(MY_APP_S_PROFILE, {"city": "Paris", "age": 30})

Build a source with two commits:

>>> source = CommitDatabase.create_in_memory()
>>> source.extend_definitions(defs).count()
3
>>> mutable = CommitMutableState(CommitStateBuilder.initial_state(source))
>>> mutable.attachment_mutating().set(MY_APP_A_USER_PROFILE, key, document)
>>> first = source.commit_mutations("first", mutable)
>>> mutable = CommitMutableState(CommitStateBuilder.state(source, first))
>>> mutable.attachment_mutating().set(
...     MY_APP_A_USER_PROFILE, key, Value.create(MY_APP_S_PROFILE, {"city": "Lyon", "age": 31}))
>>> head_commit_id = source.commit_mutations("second", mutable)

Flatten collapses a chosen commit into a fresh single-commit
``CommitDatabase``, discarding history and superseded blobs:

>>> target = CommitDatabase.create_in_memory()
>>> target.extend_definitions(defs).count()
3
>>> info = CommitDatabaseFlattener().flatten(
...     source, head_commit_id, target, "flattened baseline")
>>> print(info.documents, "documents,", info.blobs, "blobs")
1 documents, 0 blobs

Converting materializes one commit's state into a plain, history-free
``Database``:

>>> flat_db = Database.create_in_memory()
>>> flat_db.extend_definitions(defs).count()
3
>>> CommitDatabaseToDatabaseConverter().convert(source, head_commit_id, flat_db).documents
1
>>> Value.dumps(flat_db.get(MY_APP_A_USER_PROFILE, key).unwrap())
{'city': 'Lyon', 'age': 31}

``source``, ``target`` and ``flat_db`` are already-open database handles; see
:doc:`database` and :doc:`commit` for opening and creating each kind.

Progress reporting
------------------

Pass a :class:`StepperDelegate` subclass as ``progress=`` to observe a
long-running transfer. Override ``step(action, percent)``:

.. code-block:: python

   from dsviper import DatabaseCopier, StepperDelegate

   class Progress(StepperDelegate):
       def step(self, action, percent):
           print(f"{action}: {percent:.0f}%")

   DatabaseCopier().copy(source, target, progress=Progress())

Classes
-------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.DatabaseCopier
   dsviper.DatabaseToCommitDatabaseConverter
   dsviper.CommitDatabaseToDatabaseConverter
   dsviper.CommitDatabaseFlattener
   dsviper.DatabaseTransferInfo
   dsviper.StepperDelegate
