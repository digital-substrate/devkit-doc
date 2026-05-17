Commit Database
===============

The **Commit Database** is Viper's versioned persistence layer — an
immutable, content-addressed DAG of commits derived from a
:doc:`DSM <../dsm/index>` model, with deterministic mechanical convergence
between concurrent streams.

A ``CommitStore`` wraps an open Commit Database in memory and exposes the
navigation operations on top — time travel, undo/redo, multi-head
exploration — plus a dispatch surface for typed mutations and a notifier
for observers.

It is a Viper C++ subsystem first and a Python API second. The Python
exposure lives in :doc:`dsviper <../dsviper/index>` (``CommitDatabase``,
``CommitMutableState``, ``commit_mutations``); Qt-side tools live in
:doc:`dsviper-tools <../dsviper-tools/index>` and
:doc:`dsviper-components <../dsviper-components/index>`. The pages below
document the subsystem itself — its guarantees, its modes of use, and the
contract it asks of the application that consumes its output.


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
deterministic convergence between concurrent streams. A ``CommitStore``
adds the navigation on top — undo/redo, multi-head exploration. See
:doc:`../ecosystem/value-chains` for the broader picture.


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

   commit
   commit_contract


Status
------

Part of DevKit 1.2.x (LTS, feature-locked).
