# Cooperative Discipline

If you have chosen
[multi-stream usage](commit_modes.md), this page is
the modelling discipline that keeps you on the safe side of the
diagnostic — in
[Multi-stream with local invariants](commit_modes.md#multi-stream-with-local-invariants),
where the [Dual-Layer Contract](commit_contract.md) stays reference
material.

Outside a narrow envelope, concurrent writes lose data **silently**.
The engine has no notion of conflict: when two streams touch the same
granule it collapses them by structural rule (last-writer-wins) and
signals nothing — the dropped write is gone, with no error and no
notification.

That envelope is **disjoint writes**: concurrent authors operating on
structurally disjoint targets, where convergence has nothing to pick
between and every submitted intent survives. Reaching it is a modelling
task, not a runtime one — shape the DSM model so the engine never has
anything semantically meaningful to choose. That shaping is **scope
decomposition**.

This is the path for multi-stream usage, not a back-stop when the
[Dual-Layer Contract](commit_contract.md) bites. The
[import outcomes](commit_contract.md#import-outcomes) are what remains
*if* the discipline fails on a specific path.

## Not a Commit quirk

The limit is structural, not a peculiarity of this engine. Any system
that merges automatically without supervision — no human at the
merge, no semantic rule allowed to refuse — faces the same dual-layer
contract.

- CRDTs converge with semantic validity *only* where semantic equals
  structural: counters, grow-only sets, two-phase sets.
- Rich-document CRDTs (Automerge, Yjs) guarantee that characters or
  nodes do not duplicate or vanish, but cannot guarantee the resulting
  document means what either author intended.
- Operational Transformation (Google-Docs-style) needs a central
  server that arbitrates operation order. Remove the server and OT
  collapses back to mechanical reduction.
- Line-based text auto-merge succeeds silently on textually disjoint
  edits even when they are semantically incompatible — the "successful
  merge, broken build" pattern.

Mechanical reduction is the strongest guarantee any unsupervised
system can deliver. Richer guarantees require a supervisor. The
discipline below lets you stay unsupervised by ensuring the engine
never has anything semantically meaningful to pick between.

## Principle: scope ownership

If two writers operate on disjoint attachments — or on disjoint paths
within a shared attachment — convergence has nothing to pick between.
The result is the union of disjoint mutations, and every submitted
intent survives intact. But survival is not yet trust: disjointness earns it
only when it **matches ownership** — when each writer's whole intent *is* the
scope they touch. Then the union is every author's owned intent and nothing is
invented. Let a scope be a *fragment* of a larger intent and disjointness still
holds, yet the union answers to no one (see
[Re-entering the graph](commit_contract.md#re-entering-the-graph)).

The shape of that disjointness is application-specific. This page
does not prescribe a recipe — what works in one domain may not
transfer to another, and no pattern has been validated at scale as
a general solution.

### Modelling levers

Disjointness is engineered in the `.dsm`, not at runtime. The DSM
language provides the levers — none of them new:

- **Multiple attachments per concept** rather than one monolithic
  struct. Concurrent writers touching different attachments do not
  collide. See
  [Attachments](../dsm/attachments.md#recommended-pattern-multiple-attachments).
- **`set` / `map` / `xarray` containers** for concurrently-edited
  collections — commutative where used **accretively or on disjoint
  granules**: grow-only `set` union and writes to non-overlapping
  keys / paths / positions. `xarray` insert is **accretive but not
  commutative**: no concurrent insert is lost, yet the relative order
  of inserts from different streams is fixed by fusion order, not by
  their positions — rely on the element set, not on its order.
  Concurrent writes to the *same* element collapse to last-writer-wins,
  silently dropping one value. Prefer `xarray` over `vector` when
  concurrent inserts must not be lost — `vector`'s integer indices
  collide under concurrency; see
  [Vector vs XArray](../dsviper/collections.md#vector-vs-xarray-when-to-use-each).
- **References that tolerate breakage** — accept that a `key<X>`
  may outlive its target. This is a *whole-application commitment*,
  not just a DSM choice: the app must load robustly, surface the
  integrity issue, and expose corrective actions to the user. See
  the {ref}`ModelIntegrity <pool-modelintegrity-dsm>` pattern as an
  uncommon worked example.

These choices are made in the `.dsm` before any code is written —
which is why the single-stream / multi-stream decision is
architectural, not runtime.

## What scope decomposition does not solve

Be honest about the limits of the discipline:

- **Strong invariants.** Uniqueness across the whole model (no two
  assets share an SKU, no two users share an email) cannot be enforced
  by partitioning. Two authors writing into disjoint documents can
  still both claim the same global identifier. This requires a
  supervisor — typically a service that mediates allocation. See
  {ref}`local vs strong invariants <local-vs-strong-invariants>` for
  the canonical definition.
- **Cross-author semantic dependencies.** If author B's work depends
  on the *meaning* of what author A produced (and not just its
  presence), they are not really cooperating on disjoint scope; they
  are sequential, and need a coordination protocol.
- **Aggregations and analytics.** Sums, joins, derived views over
  multiple authors' contributions still face the contract at read
  time. The
  [import outcomes](commit_contract.md#import-outcomes) still apply
  to the *derived* state, even if every contributor's individual
  write was clean.

## When a supervisor is required

When the scope cannot be cleanly decomposed — when authors genuinely
need to co-edit the same field, or when strong invariants matter —
the right answer is not a better reduction algorithm. It is an
application-level supervisor: a review UI that surfaces clashes for
human arbitration, a semantic gate that refuses commits, a merge UX
that asks an operator to pick. That is the supervised regime — the
*Collaboration* row in the chapter's {ref}`three-regimes` table.

The supervisor is yours to build. The Commit Database does not
provide it; what it provides — the
[import outcomes](commit_contract.md#import-outcomes) — is the
back-stop at read time, beneath whatever discipline you choose.
[Supervised Reconciliation](commit_collaboration.md) documents one such
supervisor — post-merge, headless, additive over the public API — as a
reference implementation.

## Summary

| Regime                     | How divergence resolves                                | Where it lives                                           |
|----------------------------|--------------------------------------------------------|----------------------------------------------------------|
| **Deterministic reduction**| Structural linearisation — no notion of conflict       | The engine — the strongest guarantee without supervision |
| **Cooperation**            | Disjointness by construction — nothing to pick between | This page — application discipline                       |
| **Collaboration**          | Supervisor arbitrates (human / rule)                   | An application layer you build on top                    |

The dual-layer contract is described in all three regimes; the
discipline you adopt determines whether it stays reference material
or becomes load-bearing. Cooperation keeps it on the shelf.

## See Also

- [Modes of Use](commit_modes.md) —
  the diagnostic that determines which regime your application is in.
- [The Dual-Layer Contract](commit_contract.md) — what the engine
  does and does not guarantee under reduction, and the four import
  outcomes that back-stop the discipline.
- [Attachments — Recommended Pattern](../dsm/attachments.md#recommended-pattern-multiple-attachments) —
  the DSM modelling guidance that operationalises scope decomposition.
