Merge Reconciliation
====================

``CommitMergeAnalyzer`` is an additive, application-level supervisor over the
public ``CommitDatabase`` API. The engine reduces concurrent streams
mechanically and signals no conflict; this layer **reconstructs** a notion of
conflict over a merge — already persisted, or computed from the two heads
before it is written — and lets a caller make a chosen value survive. It adds
no engine, storage-format, or runtime change.

.. seealso::

   :doc:`/commit/commit_collaboration` — the model, the headless
   identify / surface / reconcile triad, and its bounds.

Example
-------

.. code-block:: python

   from dsviper import CommitMergeAnalyzer, CommitMergeResolution

   merge = db.merge_commit("merge", ours, theirs)
   analysis = CommitMergeAnalyzer.analyze_merge(db, merge)

   # The supervisor decides per conflict; here, keep ours at every locus.
   # A resolution pairs the conflict with the value to make survive at its
   # path — ``ours_value()`` already reads that value at the conflict's locus.
   resolutions = [
       CommitMergeResolution(c, c.ours_value().unwrap())
       for c in analysis.conflicts()
   ]
   survivor = CommitMergeAnalyzer.reconcile(db, merge, resolutions, "reconcile")

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
