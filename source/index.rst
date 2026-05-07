DevKit Documentation
====================

**Define your data model. Get type safety, versioning, and Python bindings for free.**

DevKit is the Digital Substrate Python toolkit for metadata-driven data
modeling. Define your data structures in DSM (a purpose-built DSL), and the
dsviper runtime gives you:

- **Strong typing** - Type mismatches raise exceptions immediately, not silently corrupt data
- **Version control for data** - Every mutation is tracked in a commit DAG (like git for your data)
- **Seamless Python integration** - Work with native Python types, dsviper handles conversions

.. code-block:: python

   from dsviper import CommitDatabase, CommitMutableState
   import model.attachments as ma

   # Open a versioned database
   db = CommitDatabase.open("model.cdb")

   # Create and modify typed data
   key = ma.Tuto_UserKey.create()
   login = ma.Tuto_Login()
   login.nickname = "alice"

   # Commit with full history
   state = CommitMutableState(db.initial_state())
   ma.tuto_user_login_set(state.attachment_mutating(), key, login)
   db.commit_mutations("Add user", state)


DevKit, dsviper, Viper — what's what?
-------------------------------------

Three names appear across this documentation. Here is how they layer.

**DevKit** — *What you download.*
   The Digital Substrate Python toolkit, distributed as a single ZIP — bundles
   dsviper, the Kibo code generator, templates, CLI tools, and offline
   documentation.

**dsviper** — *What runs in your Python apps.*
   The Python runtime distributed on PyPI. Strong-typed Python API over the
   Viper C++ engine. Installed via ``pip install dsviper`` — *not* bundled in
   the DevKit ZIP.

**Viper** — *The C++ engine behind dsviper.*
   The underlying metadata-driven C++ runtime — type system, commit DAG,
   database tier. Currently used internally; not yet distributed standalone.


Two Ways to Work
----------------

**Static API** - Generate type-safe Python packages from your DSM definitions.
Get IDE autocompletion, type checking, and domain-specific APIs.

**Dynamic API** - Use Viper's runtime metadata directly. No code generation needed.
Load definitions at runtime, introspect types, build tools that work with any schema.

Both approaches use the same Viper runtime. Choose based on your needs.

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: Ecosystem

   ecosystem/index

.. toctree::
   :maxdepth: 2
   :caption: DSM - Data Modeling

   dsm/index

.. toctree::
   :maxdepth: 2
   :caption: Kibo

   kibo/index

.. toctree::
   :maxdepth: 2
   :caption: Python Guide

   python/index

.. toctree::
   :maxdepth: 2
   :caption: Python API

   python/api/index

.. toctree::
   :maxdepth: 2
   :caption: dsviper-tools

   dsviper-tools/index

.. toctree::
   :maxdepth: 2
   :caption: kibo-template-viper

   kibo-template-viper/index

.. toctree::
   :maxdepth: 2
   :caption: dsviper-components

   dsviper-components/index

.. toctree::
   :maxdepth: 2
   :caption: Reference Applications

   reference-apps/index

.. toctree::
   :maxdepth: 1
   :caption: Legal

   legal/index


Indices
-------

* :ref:`genindex` - All classes and methods
* :ref:`search` - Full-text search
