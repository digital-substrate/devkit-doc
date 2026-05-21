dsviper
=======

The **dsviper** Python runtime is the strongly typed Python API over the
Viper C++ engine. It carries the type system, value system, mutation DAG,
database tier, serialization, and RPC, and exposes them as Python classes
and functions. Most user code in the ecosystem imports ``dsviper`` and is
built on top of it.

dsviper is the **runtime layer** of the ecosystem. It consumes typed Python
packages produced by Kibo (the static API), or loads DSM models directly at
runtime (the dynamic API). See :doc:`../ecosystem/value-chains` for the
broader picture.


Place in the ecosystem
----------------------

* **Depends on** — :term:`Viper C++`.
* **Consumed by** — :term:`dsviper-components`, :term:`dsviper-tools`, :term:`Commit Applications <Commit Application>`
* **Source repository** — the ``dsviper`` PyPI package is built from the
  Viper C++ source. There is no separate ``dsviper`` repository on GitHub.
* **Distribution** —
  `dsviper on PyPI <https://pypi.org/project/dsviper/>`_
  (``pip install dsviper``). Not bundled in the DevKit ZIP — the ZIP carries
  the toolchain (Kibo, kibo-template-viper, dsviper-tools), but ``dsviper`` itself
  must be installed separately from PyPI.


Quickstart
----------

Install:

.. code-block:: bash

   pip install dsviper

Open a commit database, write a typed value, commit:

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

``dsviper`` is a complete wrapper over Viper C++ — the full C++ surface
(types, values, runtime, database tier, Commit Database, serialization, RPC)
is reachable from Python. The Commit Database in particular is documented in
the peer :doc:`Commit <../commit/index>` section.


Further examples
----------------

For a broader corpus of runnable usage examples, see the public test
suite at `digital-substrate/dsviper-tests
<https://github.com/digital-substrate/dsviper-tests>`_.


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

Part of DevKit 1.2.x (LTS, feature-locked).
