dsviper
=======

The **dsviper** Python runtime is the strongly typed Python API over the
Viper C++ engine. It carries the type system, value system, commit DAG,
database tier, serialization, and RPC, and exposes them as Python classes
and functions. Most user code in the ecosystem imports ``dsviper`` and is
built on top of it.

dsviper is the **runtime layer** of the ecosystem. It consumes typed Python
packages produced by Kibo (the static API), or loads DSM models directly at
runtime (the dynamic API). See :doc:`../ecosystem/value-chains` for the
broader picture and :doc:`../ecosystem/naming` for how dsviper relates to
DevKit and the Viper engine.


Place in the ecosystem
----------------------

* **Depends on** — Viper (the C++ engine — see :doc:`../ecosystem/naming`).
* **Consumed by** — :term:`dsviper-components` (Qt Widgets and QML variants),
  :term:`dsviper-tools` (Qt Widgets and QML variants),
  :term:`Commit Applications <Commit Application>` (``ge-py``,
  ``ge-qml``, ``web-cdbe``).
* **Source repository** — the ``dsviper`` PyPI package is built from the
  Viper source. There is no separate ``dsviper`` repository on GitHub. See
  :doc:`../ecosystem/naming` for the distinction between distribution names
  and repository names.
* **Distribution** —
  `dsviper on PyPI <https://pypi.org/project/dsviper/>`_
  (``pip install dsviper``). Not bundled in the DevKit ZIP — the ZIP carries
  the toolchain (kibo, dsviper-tools, offline docs), but ``dsviper`` itself
  must be installed separately from PyPI.


Quickstart
----------

Install:

.. code-block:: bash

   pip install dsviper

Open a versioned database, write a typed value, commit:

.. code-block:: python

   from dsviper import CommitDatabase, CommitMutableState
   import model.attachments as ma

   db = CommitDatabase.open("model.cdb")

   key = ma.Tuto_UserKey.create()
   login = ma.Tuto_Login()
   login.nickname = "alice"

   state = CommitMutableState(db.initial_state())
   ma.tuto_user_login_set(state.attachment_mutating(), key, login)
   db.commit_mutations("Add user", state)

The ``model.attachments`` module above is a generated package — the
:term:`static API <static API / dynamic API>` produced by Kibo from a DSM
model. For the dynamic API (no code generation, definitions loaded at
runtime), see :doc:`dsm`.


The Metadata Everywhere Principle
---------------------------------

Viper carries its type information as runtime metadata, and every subsystem
draws on the same source: types, values, functions, serialization, database
persistence, and RPC. You describe your data once — either through the
static API generated from a DSM model, or directly through the dynamic
API — and the runtime handles conversion, validation, and cross-language
interoperability for you. This is why Python natives (``list``, ``dict``,
``tuple``) can be passed directly to typed ``dsviper`` functions: the
metadata drives the bridge, so there is nothing to register and nothing to
glue by hand.


A complete wrapper
------------------

``dsviper`` is **not** a curated subset of Viper — it is a complete
wrapper. The full surface of the C++ engine — types, values, runtime,
database tier, commit engine, serialization, RPC — is reachable from
Python, exposed as Python classes and functions. Learning ``dsviper``
therefore teaches Viper itself, from the low-level type and value APIs up
to the application-level model (commits, databases, attachments, function
pools, RPC). A Python developer fluent in ``dsviper`` can read and reason
about a Viper C++ application without learning a parallel API; conversely,
a C++ engineer familiar with Viper finds the same vocabulary in this
guide, transposed into Python.

The Commit Engine
-----------------

``dsviper`` exposes Viper's **Commit Engine** — the versioned, content-
addressed persistence layer that ``CommitDatabase`` and
``CommitMutableState`` belong to. Its guarantees, its modes of use, and
the dual-layer contract it asks of consuming code are documented in the
dedicated :doc:`Commit <../commit/index>` section, peer to this one.


Further examples
----------------

This guide and its API reference cover the curated, doctested surface. For
a broader corpus of runnable usage examples — covering edge cases and
combinations not shown here — see the public test suite at
`digital-substrate/dsviper-tests
<https://github.com/digital-substrate/dsviper-tests>`_. It exercises every
API surface and is a useful grounding source for both human readers and
LLM-driven assistants exploring ``dsviper`` patterns.


Topics
------

.. toctree::
   :maxdepth: 2

   installation
   hello
   tutorial
   types_values
   collections
   structures
   errors
   dsm
   database
   blobs
   serialization


API reference
-------------

The complete class reference is in :doc:`api/index`, organised by domain:
types, values, attachments, database, commit, blobs, serialization, DSM
introspection, web rendering, and core utilities.


Status
------

Part of DevKit 1.2.x. The runtime is stable; new APIs are added carefully
with backward compatibility in mind.
