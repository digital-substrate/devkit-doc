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


DevKit, dsviper, Viper C++
--------------------------

Three names appear across this documentation, referring to different things —
the **distribution** (DevKit), the **Python runtime** (dsviper), and the
**C++ engine** (Viper C++). See :doc:`ecosystem/naming` for the canonical
disambiguation, and :doc:`ecosystem/value-chains` for how every component
fits together.


Two Ways to Work
----------------

**Static API** - Generate type-safe Python packages from your DSM definitions.
Get IDE autocompletion, type checking, and domain-specific APIs.

**Dynamic API** - Use Viper C++'s runtime metadata directly. No code generation needed.
Load definitions at runtime, introspect types, build tools that work with any schema.

Both approaches use the same Viper C++ runtime. Choose based on your needs.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   ecosystem/index
   dsm/index
   kibo/index
   kibo-template-viper/index
   dsviper/index
   commit/index
   services/index
   dsviper/api/index
   dsviper-tools/index
   dsviper-components/index
   commit-apps/index
   legal/index


Indices
-------

* :ref:`genindex` - All classes and methods
* :ref:`search` - Full-text search
