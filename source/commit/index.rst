Commit
======

**Commit** is a deterministic, best-effort convergence engine over an
immutable, content-addressed mutation DAG on a
:doc:`DSM <../dsm/index>` model. For a **single author it is
lossless** — every read returns exactly what you wrote. For
**concurrent authors it has no notion of conflict**: overlapping intent
is silently collapsed by structural rules — structurally sound,
semantically untrusted. It is **not** a collaboration substrate.

Start here
----------

Most of this chapter is reference material you can skip. The pages you
need turn on **one question**: can more than one author write to the
database?

- **No — a single author (the common case).** Read
  :doc:`Commit Database <commit_database>`,
  :doc:`CommitStore <commit_store>` and
  :doc:`Commit Application Model <commit_application_model>`. Skip the
  rest: with a linear history, every read returns exactly what you
  wrote.
- **Yes — several authors writing concurrently.** The engine will
  silently collapse overlapping intent; your task is to keep writes
  inside the envelope where that cannot happen, or coordinate above it.
  Start with the :doc:`Modes of Use <commit_modes>` diagnostic; it tells
  you which of the remaining pages apply, and how much.

Unsure — or might a second author appear later? The choice is hard to
reverse once a model is sealed, so read
:doc:`Modes of Use <commit_modes>` before you settle on single-stream.

.. _three-regimes:

Three regimes of multi-author work
----------------------------------

Commit provides exactly one of them:

- **Mechanical convergence — what Commit is.** Streams are linearised
  deterministically, with no notion of "conflict": overlapping intent is
  silently collapsed by structural rules (last-writer-wins by
  linearisation order). Nothing is detected, signalled, or reconciled —
  structurally sound, semantically untrusted.
- **Cooperation — the safe envelope you engineer.** Disjoint or
  accretive contributions converge with every intent surviving. This is
  the *only* concurrent writing the engine folds without loss, and
  reaching it is a modelling task
  (:doc:`Cooperative Discipline <commit_cooperation>`).
- **Collaboration — what Commit is not.** Arbitrating overlapping
  intentions *before* convergence (manual-merge / review) needs a
  supervisor *above* the engine; Commit provides none.

Commit is structured as three layers, from the disk upward:

* :doc:`Commit Database <commit_database>` — the persistence layer
  itself. An immutable mutation DAG, opened by path, mutated through
  explicit commit ids. No current state, no undo, no notifications.
* :doc:`CommitStore <commit_store>` — the in-memory wrapper. Holds the
  current state, dispatches typed mutations as commits, maintains
  undo / redo, notifies observers through a framework-agnostic
  protocol. The runtime surface an application actually uses.
* :doc:`Commit Application Model <commit_application_model>` — the
  architectural pattern. An Application Context owns the
  ``CommitStore``, exposes domain state, dispatches user actions, and
  routes notifications to the UI.

Three transverse pages complete the chapter:

* :doc:`The Dual-Layer Contract <commit_contract>` — formalises what
  the three layers guarantee structurally and what remains the
  application's semantic responsibility.
* :doc:`Cooperative Discipline <commit_cooperation>` — scope
  decomposition: how to keep concurrent writes inside the disjoint
  envelope, the only region where no intent is silently lost.
* :doc:`Database synchronisation <commit_synchronization>` —
  how ``CommitSynchronizer`` replicates the mutation DAG between
  separate ``CommitDatabase`` instances, and what it implies for the
  diagnostic and the contract.

Place in the ecosystem
----------------------

* **Depends on** — :doc:`DSM <../dsm/index>` (defines the shape of the
  data being committed) and the :term:`Viper C++` engine.
* **Consumed by** — :term:`dsviper`, :term:`dsviper-tools`, :term:`dsviper-components`, :term:`Commit Applications <Commit Application>`
* **Distribution** — no standalone package. The engine ships inside Viper and reaches Python through
  `dsviper on PyPI <https://pypi.org/project/dsviper/>`_.


Where it sits in the value chain
--------------------------------

Without the Commit Database, ``dsviper`` reads and writes against the plain
``Database`` backend — flat key-value, no history. The Commit Database adds
versioning over the same backend: an immutable mutation DAG with
deterministic convergence between concurrent streams. A
:doc:`CommitStore <commit_store>` adds the navigation, dispatch, and
notifications on top. See :doc:`../ecosystem/value-chains` for the broader
picture.


Tools that ship with the DevKit
-------------------------------

Several DevKit artefacts operate directly on the Commit Database:

* :doc:`cdbe.py <../dsviper-tools/editors>` — Commit Database Editor.
* :doc:`commit_database_server.py <../dsviper-tools/server>` — network access + ``commit_admin.py``.
* :doc:`dsm_util.py create_commit_database <../dsviper-tools/dsm_util>` — create a ``CommitDatabase`` from DSM.
* :doc:`dsviper-components <../dsviper-components/index>` — Qt-side observers on the ``CommitStore`` notifier.

``dbe.py`` is *not* in this list — it targets the non-versioned ``Database``
backend.


Commit Applications
-------------------

For Commit Applications built on the Commit Database (``ge-py``, ``ge-qml``,
``web-cdbe``), see :doc:`../commit-apps/index`.


Topics
------

.. toctree::
   :maxdepth: 2

   commit_modes
   commit_database
   commit_store
   commit_application_model
   commit_contract
   commit_cooperation
   commit_synchronization


Status
------

Part of DevKit 1.2.x (LTS, feature-locked).
