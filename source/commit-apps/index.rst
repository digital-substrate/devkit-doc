Commit Applications
===================

Applications that exercise the **whole ecosystem end-to-end** — DSM
modeling, Kibo code generation, the viper template, dsviper-components, and
the dsviper runtime. They are canonical "putting it all together" exemplars,
**not** products in their own right.

Use them as worked examples when learning how the pieces fit together. Each
wires the full chain in real code, in a different shell — Qt Widgets
desktop, QML desktop, and a server-rendered web app.


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

web-cdbe
~~~~~~~~

Flask web application — a generic Commit Database Editor. Pure HTML5,
no JavaScript. Opens any commit database, walks it through dsviper's
introspection API (no domain code, no Kibo output), and renders editable
HTML forms that ``POST`` back to a commit mutation.

* **Source repository** —
  `digital-substrate/web-cdbe <https://github.com/digital-substrate/web-cdbe>`_.
* **Walk-through** — :doc:`web-cdbe`.


.. toctree::
   :hidden:

   ge-py
   ge-qml
   web-cdbe
