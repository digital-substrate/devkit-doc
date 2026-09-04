Merge Reconciliation
====================

``CommitMergeAnalyzer`` is an additive, application-level supervisor over the
public ``CommitDatabase`` API. The engine reduces concurrent streams
mechanically and signals no conflict; this layer **reconstructs** a notion of
conflict over a merge — already persisted, or computed from the two heads
before it is written — and lets a caller make a chosen value survive. It adds
no engine, storage-format, or runtime change.

**When to use**: Use this family when the application, not the engine, must
decide which value survives where two streams touched the same locus. If
mechanical reduction is acceptable, none of this is needed.

.. seealso::

   :doc:`/commit/commit_collaboration` — the model, the headless
   identify / surface / reconcile triad, and its bounds.

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

Two commits made from the same parent leave the database with two heads:

>>> db = CommitDatabase.create_in_memory()
>>> db.extend_definitions(defs).count()
3
>>> mutable = CommitMutableState(CommitStateBuilder.initial_state(db))
>>> mutable.attachment_mutating().set(MY_APP_A_USER_PROFILE, key, document)
>>> root = db.commit_mutations("base", mutable)

>>> def commit_city(label, city):
...     m = CommitMutableState(CommitStateBuilder.state(db, root))
...     m.attachment_mutating().set(
...         MY_APP_A_USER_PROFILE, key, Value.create(MY_APP_S_PROFILE, {"city": city, "age": 30}))
...     return db.commit_mutations(label, m)
>>> ours, theirs = commit_city("ours", "Lyon"), commit_city("theirs", "Nice")
>>> len(db.head_commit_ids())
2

>>> merge = db.merge_commit("merge", ours, theirs)
>>> analysis = CommitMergeAnalyzer.analyze_merge(db, merge)
>>> len(analysis.conflicts())
1

The supervisor decides per conflict; here, keep ours at every locus. A
resolution pairs the conflict with the value to make survive at its path —
``ours_value()`` already reads that value at the conflict's locus:

>>> resolutions = [
...     CommitMergeResolution(c, c.ours_value().unwrap())
...     for c in analysis.conflicts()
... ]
>>> survivor = CommitMergeAnalyzer.reconcile(db, merge, resolutions, "reconcile")
>>> Value.dumps(CommitStateBuilder.state(db, survivor)
...             .attachment_getting().get(MY_APP_A_USER_PROFILE, key).unwrap())
{'city': 'Lyon', 'age': 30}

Accepting the merge for every conflict makes ``reconcile`` return the merge
commit unchanged.

The same three steps run before the merge commit exists:
``analyze_virtual_merge(db, ours, theirs)`` — whose analysis carries no anchor,
``CommitMergeAnalysis.merge_commit()`` is empty — then
``reconcile_state(merge_state, resolutions)`` to render the arbitrated state in
memory (writing nothing), and ``materialize_merge(db, ours, theirs, resolutions,
merge_label, survival_label)`` to write the merge and its survival child
together. The merge state comes from
``CommitStateBuilder.merge_state(db, ours, theirs)``. See
:doc:`/commit/commit_collaboration`.

Classes
-------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.CommitMergeAnalyzer
   dsviper.CommitMergeAnalysis
   dsviper.CommitMergeDocument
   dsviper.CommitMergeConflict
   dsviper.CommitMergeResolution
