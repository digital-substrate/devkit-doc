Attachments
===========

Attachments connect values to documents via keys. They are the fundamental
mechanism for associating typed data with document instances.

**When to use**: Use attachments to store and retrieve values associated with
document keys. The ``AttachmentGetting`` interface provides read access,
while ``AttachmentMutating`` extends it with write operations.

Quick Start
-----------

.. code-block:: python

   from dsviper import CommitDatabase, CommitStateBuilder, CommitMutableState

   db = CommitDatabase.open("model.cdb")
   db.definitions().inject()

   # Read via AttachmentGetting
   state = CommitStateBuilder.state(db, db.last_commit_id())
   getting = state.attachment_getting()
   value = getting.get(MYAPP_A_USER, user_key)

   # Write via AttachmentMutating
   mutable = CommitMutableState(state)
   mutating = mutable.attachment_mutating()
   mutating.set(MYAPP_A_USER, user_key, document)

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
