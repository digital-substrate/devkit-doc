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
  :term:`reference applications <reference application>` (all three are
  commit-based — see below).
* **Distribution** — no standalone package. The engine ships inside Viper
  and reaches Python through
  `dsviper on PyPI <https://pypi.org/project/dsviper/>`_.


Where it sits in the value chain
--------------------------------

The four links of the toolchain compose as follows:

1. **DSM** declares the *shape* of the data — concepts, structures,
   attachments, function pools.
2. **The Commit Engine** persists that data as a versioned, content-
   addressed DAG, with deterministic convergence between concurrent
   streams.
3. **dsviper** (Python) and Viper (C++) expose the engine to application
   code, plus the supporting type and value systems.
4. **Applications** consume the result — typed editors, web tools,
   reference apps.

Without the Commit Engine, ``dsviper`` reads and writes typed data
against the plain ``Database`` backend — flat key-value, no history,
no DAG. The Commit Engine is what adds versioning on top: an immutable
commit DAG, undo/redo, multi-head exploration, and deterministic
convergence between concurrent streams.


Tools that ship with the DevKit
-------------------------------

Several artefacts in the DevKit operate directly on the Commit Engine.
The canonical generic editor is the Qt Widgets tool ``cdbe.py``; the rest
are infrastructure around it.

* :doc:`cdbe.py <../dsviper-tools/editors>` — the canonical **Commit
  Database Editor**. A full-featured Qt Widgets GUI that opens any
  ``CommitDatabase``, browses the commit DAG, applies typed mutations,
  drives undo/redo, syncs with a remote commit server, and embeds a
  Python editor. This is the production editor the DevKit ships for
  Commit Engine inspection.
* :doc:`commit_database_server.py <../dsviper-tools/server>` — exposes a
  ``CommitDatabase`` over the network for multi-client synchronisation,
  paired with ``commit_admin.py`` for head-convergence and reset
  operations.
* :doc:`dsm_util.py create_commit_database <../dsviper-tools/dsm_util>` —
  creates a new ``CommitDatabase`` from a DSM model.
* :doc:`dsviper-components <../dsviper-components/index>` — Qt-side
  observers built on the ``CommitStore`` notifier pattern, reused by
  ``cdbe.py``, ``ge-py``, and ``ge-qml``.

Note that ``dbe.py`` is **not** part of this list: it is the standard
CRUD editor for the non-versioned ``Database`` backend and does not
touch the Commit Engine.


Reference applications built on the Commit Engine
-------------------------------------------------

Three reference applications demonstrate distinct usage regimes on top
of the engine:

* :doc:`ge-py <../reference-apps/ge-py>` — Graph Editor (Qt Widgets):
  a desktop application built on a ``CommitStore`` facade, exercising
  undo/redo and a typed domain on top of the engine.
* :doc:`ge-qml <../reference-apps/ge-qml>` — Graph Editor (QML): same
  domain and ``CommitStore`` facade as ``ge-py``, ported to the Qt Quick
  variant of ``dsviper-components``.
* :doc:`web-cdbe <../reference-apps/web-cdbe>` — a Flask web demo that
  ports the generic Commit-database-editor idea (the same role ``cdbe.py``
  plays in Qt Widgets) to a browser context, with deliberately minimal
  surface — HTML5, no JavaScript. Useful as a worked example, not as a
  substitute for ``cdbe.py``.

See :doc:`../reference-apps/index` for the full list and the engineering
context around each app.


Topics
------

.. toctree::
   :maxdepth: 2

   commit
   commit_contract


Status
------

Part of DevKit 1.2.x. The engine is stable; the dual-layer contract and
modes-of-use vocabulary above are the canonical framing for any code that
relies on the engine's guarantees.
