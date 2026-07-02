Database Transfer
=================

Four converters move documents and blobs between :class:`Database` and
:class:`CommitDatabase` stores, in every combination of the two.

Each converter takes **pre-opened source and target handles** — never
filesystem paths — so a transfer works over both local and remote transports.
Every direction returns a :class:`DatabaseTransferInfo` reporting how many
documents and blobs it moved.

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

Example
-------

.. code-block:: python

   from dsviper import (
       CommitDatabaseFlattener,
       CommitDatabaseToDatabaseConverter,
   )

   # Collapse a chosen commit into a fresh single-commit CommitDatabase,
   # discarding history and superseded blobs (the Flatten pattern).
   info = CommitDatabaseFlattener().flatten(
       source, head_commit_id, target, "flattened baseline"
   )
   print(info.documents, "documents,", info.blobs, "blobs")

   # Materialize one commit's state into a plain, history-free Database.
   CommitDatabaseToDatabaseConverter().convert(source, commit_id, flat_db)

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
