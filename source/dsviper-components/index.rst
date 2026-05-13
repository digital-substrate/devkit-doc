dsviper-components
==================

Shared component library on top of :term:`dsviper` — the **standard
administrative, collaborative and scripting surface** of any Commit
application, ready to compose into a domain-specific UI. Available as
two parallel variants:

* **Qt Widgets** — ``dsviper-components``
* **Qt Quick / QML** — ``dsviper-components-qml``

Most :term:`Commit Applications <Commit Application>` use one or
both of these to avoid re-implementing common UI for typed-data
manipulation.


What it provides
----------------

The library covers the four areas every Commit application ends up
needing:

* **Administration / introspection** — commit-DAG browser, undo-stack
  navigator, attachment inspector, blob browser, per-commit document
  and settings dialogs.
* **Collaboration** — connect-to-server dialog, threaded synchroniser,
  fetch / push / sync log.
* **Embedded scripting** — Python script editor with a runtime model
  that exposes the live application context to user scripts.
* **Conventions / helpers** — the ``DSCommitStoreNotifier`` adapter,
  geometry persistence, item delegates, settings wrapper.

See :doc:`architecture` for the design pattern that ties these
together, and :doc:`widgets` for the full catalogue.


Place in the ecosystem
----------------------

* **Depends on** — :term:`dsviper`, Qt (Widgets or Quick depending on
  variant).
* **Consumed by** — :term:`Commit Applications <Commit Application>`
  (``ge-py``, ``ge-qml``) and any custom Python application built on
  dsviper.
* **Source repositories** —

  * `digital-substrate/dsviper-components
    <https://github.com/digital-substrate/dsviper-components>`_
    — Qt Widgets variant.
  * `digital-substrate/dsviper-components-qml
    <https://github.com/digital-substrate/dsviper-components-qml>`_
    — Qt Quick / QML variant.

* **Distribution** — installed as Python packages, typically alongside
  ``dsviper``.


Topics
------

.. toctree::
   :maxdepth: 2

   architecture
   widgets
