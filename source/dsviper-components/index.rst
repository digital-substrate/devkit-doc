dsviper-components
==================

Shared component library on top of :term:`dsviper` — dialogs, views, and
helpers reusable by any Python application built on the runtime. Available
as two parallel variants:

* **Qt Widgets** — `dsviper-components`
* **Qt Quick / QML** — `dsviper-components-qml`

Most :term:`reference applications <reference application>` use one or both
of these to avoid re-implementing common UI for typed-data manipulation.


Place in the ecosystem
----------------------

* **Depends on** — :term:`dsviper`, Qt (Widgets or Quick depending on
  variant).
* **Consumed by** — :term:`reference applications <reference application>`
  (``ge-py``, ``ge-qml``, ``dsviper-blender``) and any custom Python
  application built on dsviper.
* **Source repositories** —

  * `digital-substrate/dsviper-components
    <https://github.com/digital-substrate/dsviper-components>`_
    — Qt Widgets variant.
  * `digital-substrate/dsviper-components-qml
    <https://github.com/digital-substrate/dsviper-components-qml>`_
    — Qt Quick / QML variant.

* **Distribution** — installed as Python packages, typically alongside
  ``dsviper``.


Status
------

.. note::

   Stub. The component catalogue, usage examples, and integration patterns
   are forthcoming. Until then, refer to the GitHub repositories and to the
   :term:`reference applications <reference application>` that consume
   them.
