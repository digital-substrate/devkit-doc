kibo-template-viper
===================

The first-party :term:`Kibo template`. From a DSM model, it produces
**C++ surfaces** for :term:`Viper C++`, a typed **Python package** for
:term:`dsviper`, and a typed **TypeScript package** for the dsviper Node
binding — three idiomatic surfaces over one :term:`Viper` runtime.


Place in the ecosystem
----------------------

* **Depends on** — :term:`Kibo`, :term:`DSM`, the Viper C++ runtime.
* **Consumed by** — ``kibo`` invocations targeting the Viper runtime.
* **Source repository** —
  `digital-substrate/kibo-template-viper
  <https://github.com/digital-substrate/kibo-template-viper>`_.
* **Distribution** — bundled in the DevKit ZIP


What it produces
----------------

Three surfaces from one DSM model:

* **C++ surfaces** — headers and implementation files for type definitions,
  attachments, persistence, serialization, and function pools, designed to
  link against the :term:`Viper C++` engine (commercial).
* **A typed Python package** — classes, functions, and type hints mirroring
  the model. Importable as ``import <namespace>`` and usable through the
  :term:`dsviper` runtime (PyPI).
* **A typed TypeScript package** — classes and type declarations mirroring
  the model, published as an npm package and usable through the
  ``@digitalsubstrate/dsviper`` Node binding.

Each generated surface is the output of one or more **templated features**.
The catalogue is in :doc:`features`.


The Dual Reality
----------------

The code produced by kibo-template-viper is not a runtime in its own
right — it is a static **adapter layer** over Viper's dynamic API.
Both APIs are strongly typed ; the type catalog, built from DSM at
runtime, is the single source of truth. The generated adapter gives
developers and IDEs a static, idiomatic surface (typed classes, STL
in C++, type hints in Python, typed declarations in TypeScript) that
delegates to the dynamic runtime transparently. The static surface does not add type safety — it adds
editor ergonomics on top of safety that already lives in the runtime.

This split is the :term:`Dual Reality` pattern :

* **Developer Reality** — statically typed at edit/compile time, what
  the IDE sees.
* **Runtime Reality** — dynamically typed via the metadata catalog,
  what the engine actually manipulates.

Both realities coexist for the same data; the generated adapters translate
between them, sharing one engine — no parallel implementation, no divergence across
surfaces. Applications that do not need the typed comfort can bypass the
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
