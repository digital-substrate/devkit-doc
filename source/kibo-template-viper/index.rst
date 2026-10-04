kibo-template-viper
===================

The first-party :term:`Kibo template` pack. From a DSM model, it produces
**C++** for :term:`Viper C++`, a typed **Python package** over
:term:`dsviper`, and a typed **TypeScript package** over the
``@digitalsubstrate/dsviper`` Node binding — three idiomatic surfaces over one
:term:`Viper` runtime.

This section documents the kibo 2 line of the pack: ``kibo-template-viper``
2.0.0, which consumes Template Model 2.


Place in the ecosystem
----------------------

* **Depends on** — :term:`Kibo` 2, :term:`DSM`, the Viper runtime of each
  target (see `Versioning`_).
* **Driven by** — :doc:`kibo-project <../kibo/kibo-project>`, which reads a
  project's ``kibo.toml``, resolves the features and runs kibo once per
  template.
* **Source repository** —
  `digital-substrate/kibo-template-viper
  <https://github.com/digital-substrate/kibo-template-viper>`_.


What it produces
----------------

Three surfaces from one DSM model. One DSM namespace is one **unit**: a
file-name prefix and a C++ ``namespace``, a Python or TypeScript module
directory — so two namespaces of one model may declare the same name.

* **C++** — value types (structures, enumerations, keys), the codec that
  crosses them to a Viper ``Value`` through the runtime's static layer, field
  constants, attachments and function pools, compiled against the
  :term:`Viper C++` runtime.
* **A Python package** over ``dsviper`` — one module per namespace, the
  container classes the model uses, the attachments grouped by concept, and
  ``definitions()``. It carries a small runtime of its own, ``_codegen``, and
  becomes an installable, typed wheel with the ``Wheel`` feature
  (:doc:`wheels`).
* **A TypeScript package** over ``@digitalsubstrate/dsviper`` — the same
  surface as an ES module package, with its own ``_codegen`` runtime, built
  with ``tsc`` from the ``package.json`` and ``tsconfig.json`` of the
  ``Package`` feature (:doc:`node`).

A project selects **features**, and the pack's ``features.json`` maps each one
to the templates it renders. The catalogue is in :doc:`features`.

The **C++ surface is the base reference**: the Python and TypeScript packages
offer what it offers, with its restrictions. Python and TypeScript are one
design in two idioms (:doc:`parity`).


The Dual Reality
----------------

The code produced by kibo-template-viper is not a runtime in its own
right — it is a static **adapter layer** over Viper's dynamic API. The
runtime deals in ``Value`` objects whose type identity is checked at run
time, against the definitions built from DSM: that type catalogue is the
single source of truth. The generated adapter gives developers and IDEs a
static, idiomatic surface (typed classes, STL in C++, type hints in Python,
typed declarations in TypeScript) over it. The static surface does not add
type safety — it makes visible, at edit time, the safety that already lives
in the runtime.

This split is the :term:`Dual Reality` pattern:

* **Developer Reality** — statically typed at edit/compile time, what
  the IDE sees.
* **Runtime Reality** — dynamically typed via the metadata catalogue,
  what the engine actually manipulates.

Both realities hold the same data; only the bridge between them differs
per target:

* **Python and TypeScript** — a generated object is a box around one runtime
  ``Value``, with the API of the class it faces, and delegates every operation
  to it. It holds no parallel state, and follows the runtime's reference
  semantics: ``wrap_value`` / ``wrapValue`` and a constructor given a Viper
  value box it without copying; a copy is explicit.
* **C++** — a generated type is a real ``struct`` with native fields, and a
  generated codec crosses ``struct ⇄ Value`` at the boundaries through the
  runtime's static layer. A second representation, never a second
  implementation: type identity and serialization stay the runtime's.

The generated code is an adapter, never a second implementation, so there is
no divergence across surfaces. Applications that do not need the typed
comfort can bypass the static side and work directly against the dynamic
runtime (see :term:`static API / dynamic API`) — that is what generic tools
like :doc:`cdbe.py <../dsviper-tools/editors>` do.


Versioning
----------

The pack versions itself: its number is its own, and says nothing about what
it sits between. Those are declared separately.

**What it consumes** — Template Model 2, exposed by kibo ``>=2.0.0``
(``generator.kibo`` in ``features.json``). This is a floor, not a co-version:
a later kibo exposing the same Template Model renders the pack too, and that
the pack is at 2.0.0 while it consumes Template Model 2 is a coincidence, not
a rule.

**What each target runs on** — each target states its runtime and the range
it needs. The runtime's ``MAJOR.MINOR`` is the compatibility contract; its
patch is versioned independently per binding, so the floors differ:

.. list-table::
   :header-rows: 1

   * - Target
     - Runtime
     - Range
   * - ``cpp``
     - ``viper`` (C++ runtime)
     - 1.2, with its static layer
   * - ``python``
     - ``dsviper`` (PyPI wheel)
     - ``>=1.2.29, <1.3``
   * - ``typescript``
     - ``@digitalsubstrate/dsviper`` (npm)
     - ``>=1.2.14 <1.3.0``

A floor lives in the generated output, where the consumer's build reads it:
the generated ``pyproject.toml`` declares the ``dsviper`` range, the generated
``package.json`` the ``@digitalsubstrate/dsviper`` range. The C++ code
crosses to a ``Value``, and hashes, through the runtime's static layer
(``Viper_StaticType``, ``Viper_StaticWriter``, ``Viper_StaticReader``,
``Viper_StaticHash``), so a C++ project builds a ``viper`` 1.2 runtime that
carries it.

Every generated source file's header names what produced it, and every file
that imports the runtime names the runtime and its range; a manifest
(``pyproject.toml``, ``package.json``) declares the same range as a dependency.
Here, a C++ header of a model named ``features``:

.. code-block:: cpp

   // Demo -- the types this namespace declares.
   //
   // Generated from features.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
   // Templates: kibo-template-viper 2.0.0 (MIT), Template Model 2.
   // Runtime: this file links against the `viper` C++ runtime 1.2.x,
   // distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
   // Commercial use requires a Commercial Licence from Digital Substrate.

A Python module says ``this file imports `dsviper` >=1.2.29 <1.3.0``, a
TypeScript module ``this file imports `@digitalsubstrate/dsviper` >=1.2.14
<1.3.0``. A consumer holding generated code can answer "which runtime?"
without this page.

What the generated code exposes is a public API: renaming a generated class,
field or operation breaks the code written against it, and is a breaking
change of the pack, recorded in its changelog. Code written against the 1.2
pack's output migrates as the pack's ``CHANGELOG.md`` says (2.0.0,
*Migrating from 1.2*); where each 1.2 feature went is in
:ref:`features-from-1-2`.

The templates are MIT. The generated code is not standalone: running it
requires the runtime of its target, distributed under
``LicenseRef-DigitalSubstrate-Commercial-1.2``.


Topics
------

.. toctree::
   :maxdepth: 2

   features
   wheels
   node
   parity


Status
------

kibo-template-viper 2 — Template Model 2, over the 1.2 runtime; the 1.2 pack
is documented in the 1.2 version of this documentation. For Kibo's CLI, the
generic template format, and how to write your own template targeting
another runtime, see the :doc:`Kibo section <../kibo/index>`.
