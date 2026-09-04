Attachments
===========

Attachments connect values to documents via keys. They are the fundamental
mechanism for associating typed data with document instances.

**When to use**: Use attachments to store and retrieve values associated with
document keys. The ``AttachmentGetting`` interface provides read access,
while ``AttachmentMutating`` extends it with write operations.

Quick Start
-----------

>>> from dsviper import *
>>> MODEL = """
... namespace MyApp {8f14e45f-ceea-467a-9575-1c14b48f0b7e} {
...     concept User;
...     struct Profile { string city; uint16 age; };
...     attachment<User, Profile> profile;
... };
... """
>>> builder = DSMBuilder()
>>> builder.append("model.dsm", MODEL)
>>> report, dsm_defs, defs = builder.parse()
>>> report.has_error()
False
>>> defs.inject(globals())             # MY_APP_T_USER, MY_APP_A_USER_PROFILE, …
>>> key = ValueKey.create(MY_APP_T_USER, "0d2f0e1a-1111-4222-8333-444455556666")
>>> document = Value.create(MY_APP_S_PROFILE, {"city": "Paris", "age": 30})

``AttachmentGetting`` reads and ``AttachmentMutating`` writes. Both are
reached from a state, never constructed directly:

>>> db = CommitDatabase.create_in_memory()
>>> db.extend_definitions(defs).count()
3
>>> mutable = CommitMutableState(CommitStateBuilder.initial_state(db))
>>> mutating = mutable.attachment_mutating()
>>> mutating.set(MY_APP_A_USER_PROFILE, key, document)
>>> commit_id = db.commit_mutations("Add user", mutable)

>>> getting = CommitStateBuilder.state(db, commit_id).attachment_getting()
>>> value = getting.get(MY_APP_A_USER_PROFILE, key)
>>> value.is_nil()
False
>>> Value.dumps(value.unwrap())
{'city': 'Paris', 'age': 30}

A key that holds nothing is not an error — the optional is simply empty:

>>> absent = ValueKey.create(MY_APP_T_USER, "ffffffff-0000-4000-8000-000000000000")
>>> getting.get(MY_APP_A_USER_PROFILE, absent).is_nil()
True

Core Classes
------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Attachment

Attachment Interfaces
---------------------

These interfaces provide read (getting) and write (mutating) access to
attached values.

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.AttachmentGetting
   dsviper.AttachmentMutating

Attachment Functions
--------------------

User-defined functions that operate on attached values, defined via DSM.

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.AttachmentGettingFunction
   dsviper.AttachmentMutatingFunction
   dsviper.AttachmentFunctionPool
   dsviper.AttachmentFunctionPoolFunctions
