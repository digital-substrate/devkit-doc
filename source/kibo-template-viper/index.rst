kibo-template-viper
===================

The first-party :term:`Kibo template` for the dsviper / Viper ecosystem.
Consumed by :term:`Kibo` to emit C++ and Python surfaces from a DSM model.

This is the template that sits in the third slot of the
:doc:`code-generation pipeline <../ecosystem/pipeline>`: ``DSM → Kibo →
kibo-template-viper`` produces a typed Python package usable from
:term:`dsviper`, plus C++ surfaces for embedding in a Viper application.


Place in the ecosystem
----------------------

* **Depends on** — :term:`Kibo`, :term:`DSM`, the Viper runtime.
* **Consumed by** — ``kibo`` invocations targeting the dsviper / Viper
  runtime. Not used directly by end users — it is invoked through the
  ``kibo`` CLI (or via ``dsm_util.py create_python_package``, which calls
  Kibo with this template under the hood).
* **Source repository** —
  `digital-substrate/kibo-template-viper
  <https://github.com/digital-substrate/kibo-template-viper>`_.
* **Distribution** — bundled in the DevKit ZIP alongside ``kibo`` and the
  rest of the toolchain.


What it produces
----------------

Two surfaces from one DSM model:

* **A typed Python package** — classes, functions, and type hints mirroring
  the model. Importable as ``import <namespace>`` and usable through the
  :term:`dsviper` runtime.
* **C++ surfaces** — headers and implementation files for type definitions,
  attachments, persistence, serialization, and function pools, designed to
  link against the Viper C++ engine.

Each generated surface is the output of one or more **templated features**.
The catalogue is in :doc:`features`.


The Dual Reality
----------------

The code produced by kibo-template-viper is not a runtime in its own
right — it is a typed **adapter layer** over Viper's dynamic API. The
runtime is metadata-driven and dynamic ; the generated code gives
developers and IDEs a static, idiomatic surface (typed classes, STL in
C++, type hints in Python) that delegates to the dynamic runtime
transparently.

This split is the :term:`Dual Reality` pattern :

* **Developer Reality** — static, typed, what the IDE sees.
* **Runtime Reality** — dynamic, metadata-driven, what the engine
  actually manipulates.

Both realities coexist for the same data; the generated adapters translate
between them, sharing one engine — no parallel implementation, no C++/Python
divergence. Applications that do not need the typed comfort can bypass the
static side and work directly against the dynamic runtime (see
:term:`static API / dynamic API`) — that is what generic tools like
:doc:`cdbe.py <../dsviper-tools/editors>` do.


Topics
------

.. toctree::
   :maxdepth: 2

   features
   wheels


Status
------

Part of DevKit 1.2.x (LTS, feature-locked). For Kibo's CLI, the generic
template format, and how to write your own template targeting another
runtime, see the :doc:`Kibo section <../kibo/index>`.
