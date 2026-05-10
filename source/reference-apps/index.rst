Reference Applications
======================

Applications that exercise the **whole ecosystem end-to-end** — DSM
modeling, Kibo code generation, the viper template, dsviper-components, and
the dsviper runtime. They are canonical "putting it all together" exemplars,
**not** products in their own right.

Use them as worked examples when learning how the pieces fit together. Each
wires the full chain in real code, in a different shell — desktop, Blender
add-on, web.


Applications
------------

ge-py
~~~~~

Graph Editor — PySide6 desktop application demonstrating dsviper end-to-end
with a graph database visualization. Built on the Qt Widgets variant of
dsviper-components.

* **Source repository** —
  `digital-substrate/ge-py <https://github.com/digital-substrate/ge-py>`_.
* **Walk-through** — :doc:`ge-py`.

ge-qml
~~~~~~

Graph Editor — QML port of ge-py, built on the Qt Quick variant of
dsviper-components. Same value chain, same business logic, same
``CommitStore`` facade — the UI is QML driven by Python ``QObject``
models registered as QML context properties.

* **Source repository** —
  `digital-substrate/ge-qml <https://github.com/digital-substrate/ge-qml>`_.
* **Walk-through** — :doc:`ge-qml`.

dsviper-blender
~~~~~~~~~~~~~~~

Blender 4.x add-on that bundles the ``dsviper`` runtime from PyPI inside
Blender, so the type system and commit DAG are usable from Blender's Python
console and operators.

* **Source repository** —
  `digital-substrate/dsviper-blender
  <https://github.com/digital-substrate/dsviper-blender>`_.
* **License** — GPL-3.0-or-later (Blender add-on constraint).

web-cdbe
~~~~~~~~

Flask web application demonstrating a Commit Database Editor on top of
dsviper. HTML5, no JavaScript — illustrates how the runtime integrates into
a server-rendered web app.

* **Source repository** —
  `digital-substrate/web-cdbe <https://github.com/digital-substrate/web-cdbe>`_.


Status
------

.. note::

   Per-application walk-throughs are being added incrementally. ``ge-py``
   and ``ge-qml`` have one (:doc:`ge-py`, :doc:`ge-qml`); the others still
   point only to their GitHub repository for now.


.. toctree::
   :hidden:

   ge-py
   ge-qml
