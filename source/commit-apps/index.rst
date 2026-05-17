Commit Applications
===================

Concrete walk-throughs of the
:doc:`Commit Application Model <../commit/commit_application_model>`,
in different languages and on different presentation tiers. The Model
itself — Application Context, dispatch surface, notification contract,
language profiles — is documented in the :doc:`Commit <../commit/index>`
chapter; this chapter is **instances**.

The pattern stripped of its domain first (``cdbe``), then with a domain
on top (``ge-py``, ``ge-qml``), then re-stripped on a different tier
(``web-cdbe``). They are not products in their own right — read them as
worked examples.


cdbe
----

The minimal, generic incarnation of the pattern — a PySide6 desktop
application that opens **any** commit database with no domain, no
Kibo output, no business logic. The central widget is itself a
generic component (``DSDocumentsCommitStore``) driven by runtime
introspection. cdbe is essentially ``dsviper-components`` wired up
into a Qt main window. Read this walkthrough first to see the
pattern stripped of its domain — the bare skeleton of the Application
Context.

* **Source repository** — ships inside
  `digital-substrate/dsviper-tools <https://github.com/digital-substrate/dsviper-tools>`_.
* **Walk-through** — :doc:`cdbe`.

ge-py
-----

Graph Editor — PySide6 desktop application demonstrating dsviper
end-to-end with a graph database visualization. Built on the Qt
Widgets infrastructure (:doc:`dsviper-components <../dsviper-components/index>`).
Re-introduces the domain on top of the cdbe skeleton: a DSM model,
Kibo-generated typed accessors, business functions, and a ``Context``
class that owns the domain state.

* **Source repository** —
  `digital-substrate/ge-py <https://github.com/digital-substrate/ge-py>`_.
* **Walk-through** — :doc:`ge-py`.

ge-qml
------

Graph Editor — QML port of ge-py, built on the Qt Quick
infrastructure (``dsviper-components-qml``). Same value chain, same
business logic, same ``CommitStore`` facade — the UI is QML driven by
Python ``QObject`` models registered as QML context properties.

* **Source repository** —
  `digital-substrate/ge-qml <https://github.com/digital-substrate/ge-qml>`_.
* **Walk-through** — :doc:`ge-qml`.

web-cdbe
--------

Flask web application — a generic Commit Database Editor. Pure
HTML5, no JavaScript. Same model-agnostic posture as cdbe, ported to
a server-rendered HTML/CSS surface.

* **Source repository** —
  `digital-substrate/web-cdbe <https://github.com/digital-substrate/web-cdbe>`_.
* **Walk-through** — :doc:`web-cdbe`.


C++ realizations
----------------

Concrete C++ realizations of the same pattern exist in parallel — a Qt
profile and an AppKit (macOS) profile, with a generic Commit Database
Editor and a Graph Editor mirroring ``cdbe`` and ``ge-py``. They follow
the six-layer C++ profile described in
:doc:`../commit/commit_application_model` and ship alongside
:term:`Viper C++`. :doc:`Contact us <../ecosystem/naming>` for access.


.. toctree::
   :hidden:

   cdbe
   ge-py
   ge-qml
   web-cdbe
