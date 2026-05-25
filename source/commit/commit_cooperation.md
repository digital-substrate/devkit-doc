# Cooperative Discipline

If you have chosen
[multi-stream usage](commit_modes.md), this page is
the modelling discipline that keeps you on the safe side of the
diagnostic — in
[Multi-stream with local invariants](commit_modes.md#multi-stream-with-local-invariants),
where the [Dual-Layer Contract](commit_contract.md) stays reference
material.

Commit gives you mechanical convergence as a primitive. To get
*cooperation* — the regime where disjoint writes converge without
arbitration, every submitted intent surviving — shape the DSM model
so the engine never has anything semantically meaningful to
pick between. That shaping is **scope decomposition**: model the data
such that concurrent writers operate on structurally disjoint
targets.

This is the recommended path for multi-stream usage, not the
back-stop when the contract bites. The
[import outcomes](commit_contract.md#import-outcomes) are what
remains *if* the discipline fails on a specific path.

## Not a Commit quirk

The limit is structural, not a peculiarity of this engine. Any system
that converges automatically without supervision — no human at the
merge, no semantic rule allowed to refuse — faces the same dual-layer
contract.

- CRDTs converge with semantic validity *only* where semantic equals
  structural: counters, grow-only sets, two-phase sets.
- Rich-document CRDTs (Automerge, Yjs) guarantee that characters or
  nodes do not duplicate or vanish, but cannot guarantee the resulting
  document means what either author intended.
- Operational Transformation (Google-Docs-style) needs a central
  server that arbitrates operation order. Remove the server and OT
  collapses back to mechanical convergence.
- Line-based text auto-merge succeeds silently on textually disjoint
  edits even when they are semantically incompatible — the "successful
  merge, broken build" pattern.

Mechanical convergence is the strongest guarantee any unsupervised
system can deliver. Richer guarantees require a supervisor. The
discipline below lets you stay unsupervised by ensuring the engine
never has anything semantically meaningful to pick between.

## Principle: scope ownership

If two writers operate on disjoint attachments — or on disjoint paths
within a shared attachment — convergence has nothing to pick between.
The result is the union of disjoint mutations, and every submitted
intent survives intact. Semantic validity becomes a consequence of
structural disjointness.

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
  granules**: grow-only `set` union, `xarray` insert (no insert is
  lost), and writes to non-overlapping keys / paths / positions.
  Concurrent writes to the *same* element collapse to last-writer-wins,
  silently dropping one value. Prefer `xarray` over `vector` when
  positions must survive convergence; see
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
the right answer is not a better convergence algorithm. It is an
application-level supervisor: a review UI that surfaces clashes for
human arbitration, a semantic gate that refuses commits, a merge UX
that asks an operator to pick. That is the supervised regime — the
*Collaboration* row in the chapter's {ref}`three-regimes` table.

The supervisor is yours to build. The Commit Database does not
provide it; what it provides — the
[import outcomes](commit_contract.md#import-outcomes) — is the
back-stop at read time, beneath whatever discipline you choose.

## Summary

| Regime                     | How divergence resolves                                | Where it lives                                           |
|----------------------------|--------------------------------------------------------|----------------------------------------------------------|
| **Mechanical convergence** | Structural linearisation — no notion of conflict       | The engine — the strongest guarantee without supervision |
| **Cooperation**            | Disjointness by construction — nothing to pick between | This page — application discipline                       |
| **Collaboration**          | Supervisor arbitrates (human / rule)                   | An application layer you build on top                    |

The dual-layer contract is described in all three regimes; the
discipline you adopt determines whether it stays reference material
or becomes load-bearing. Cooperation keeps it on the shelf.

## See Also

- [Modes of Use](commit_modes.md) —
  the diagnostic that determines which regime your application is in.
- [The Dual-Layer Contract](commit_contract.md) — what the engine
  does and does not guarantee under convergence, and the four import
  outcomes that back-stop the discipline.
- [Attachments — Recommended Pattern](../dsm/attachments.md#recommended-pattern-multiple-attachments) —
  the DSM modelling guidance that operationalises scope decomposition.
