Commit Engine
=============

The **Commit Engine** is Viper's versioned persistence layer. It turns a
state described in :doc:`DSM <../dsm/index>` into an immutable, content-addressed
DAG of commits — the substrate that makes time travel, undo/redo,
multi-head exploration, and mechanical convergence between concurrent
streams possible.

It is a Viper subsystem first and a Python API second. The Python
exposure lives in :doc:`dsviper <../dsviper/index>` (``CommitDatabase``,
``CommitMutableState``, ``commit_mutations``); Qt-side tools live in
:doc:`dsviper-tools <../dsviper-tools/index>` and
:doc:`dsviper-components <../dsviper-components/index>`. The pages below
document the engine itself — its guarantees, its modes of use, and the
contract it asks of the application that consumes its output.


Place in the ecosystem
----------------------

* **Depends on** — :doc:`DSM <../dsm/index>` (defines the shape of the
  data being committed) and the Viper C++ engine (see
  :doc:`../ecosystem/naming`).
* **Consumed by** — :term:`dsviper` (Python exposure of the commit API),
  :term:`dsviper-tools` (server, editors, ``dsm_util``),
  :term:`dsviper-components` (Qt Widgets and QML observers of a
  ``CommitStore``),
  :term:`Commit Applications <Commit Application>` (all three are
  commit-based — see below).
* **Distribution** — no standalone package. The engine ships inside Viper
  and reaches Python through
  `dsviper on PyPI <https://pypi.org/project/dsviper/>`_.


Where it sits in the value chain
--------------------------------

Without the Commit Engine, ``dsviper`` reads and writes against the plain
``Database`` backend — flat key-value, no history. The Commit Engine adds
versioning: an immutable DAG, undo/redo, multi-head exploration, and
deterministic convergence between concurrent streams. See
:doc:`../ecosystem/value-chains` for the broader picture.


Tools that ship with the DevKit
-------------------------------

Several DevKit artefacts operate directly on the Commit Engine:

* :doc:`cdbe.py <../dsviper-tools/editors>` — Commit Database Editor (Qt Widgets).
* :doc:`commit_database_server.py <../dsviper-tools/server>` — network access + ``commit_admin.py``.
* :doc:`dsm_util.py create_commit_database <../dsviper-tools/dsm_util>` — create a ``CommitDatabase`` from DSM.
* :doc:`dsviper-components <../dsviper-components/index>` — Qt-side observers on the ``CommitStore`` notifier.

``dbe.py`` is *not* in this list — it targets the non-versioned ``Database``
backend.


Commit Applications
-------------------

For Commit Applications built on the engine (``ge-py``, ``ge-qml``,
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
