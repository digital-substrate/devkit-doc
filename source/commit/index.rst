Commit
======

**Commit** is Viper's versioned-state technology — an immutable,
content-addressed DAG of commits derived from a
:doc:`DSM <../dsm/index>` model, with deterministic mechanical
convergence between concurrent streams, plus the runtime wrapper and
the architectural pattern that turn it into the substrate of an
interactive application.

It is structured as three layers, from the disk upward:

* :doc:`Commit Database <commit_database>` — the persistence layer
  itself. An immutable DAG of commits, opened by path, mutated through
  explicit commit ids. No current state, no undo, no notifications.
* :doc:`CommitStore <commit_store>` — the in-memory wrapper. Holds the
  current state, dispatches typed mutations as commits, maintains
  undo / redo, notifies observers through a framework-agnostic
  protocol. The runtime surface an application actually uses.
* :doc:`Commit Application Model <commit_application_model>` — the
  architectural pattern. An Application Context owns the
  ``CommitStore``, exposes domain state, dispatches user actions, and
  routes notifications to the UI.

A fourth page, :doc:`The Dual-Layer Contract <commit_contract>`,
formalises what the three layers guarantee structurally and what
remains the application's semantic responsibility. A fifth page,
:doc:`Cooperative Editing Patterns <commit_cooperation>`, gives the
operational discipline — scope decomposition — that lets you stay
inside the engine's structural guarantees without having to consume
the contract at read time.

It is a Viper C++ subsystem first and a Python API second. The Python
exposure lives in :doc:`dsviper <../dsviper/index>` (``CommitDatabase``,
``CommitStore``, ``CommitMutableState``); Qt-side tools live in
:doc:`dsviper-tools <../dsviper-tools/index>` and
:doc:`dsviper-components <../dsviper-components/index>`. Concrete
walk-throughs of the Model are gathered under
:doc:`Commit Applications <../commit-apps/index>`.


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
versioning over the same backend: an immutable DAG of commits with
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

   commit_database
   commit_store
   commit_application_model
   commit_contract
   commit_cooperation


Status
------

Part of DevKit 1.2.x (LTS, feature-locked).
