dsviper Documentation
=====================

**Define your data model. Get type safety, versioning, and Python bindings for free.**

Viper is a metadata-driven runtime that turns data modeling into a first-class
development experience. Define your data structures in DSM (a purpose-built DSL),
and Viper gives you:

- **Strong typing** - Type mismatches raise exceptions immediately, not silently corrupt data
- **Version control for data** - Every mutation is tracked in a commit DAG (like git for your data)
- **Seamless Python integration** - Work with native Python types, Viper handles conversions

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
   :caption: DSM - Data Modeling

   dsm/index

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
   :caption: Toolchain

   tools/index

.. toctree::
   :maxdepth: 2
   :caption: Viper Concepts

   concepts/index


Indices
-------

* :ref:`genindex` - All classes and methods
* :ref:`search` - Full-text search
