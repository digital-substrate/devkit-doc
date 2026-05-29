Merge Reconciliation
====================

``CommitMergeAnalyzer`` is an additive, application-level supervisor over the
public ``CommitDatabase`` API. The engine converges concurrent streams
mechanically and signals no conflict; this layer **reconstructs** a notion of
conflict *after* a merge and lets a caller make a chosen value survive. It adds
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
