# Cooperative Editing Patterns

The [Dual-Layer Contract](commit_contract.md) explains why the engine
cannot deliver semantic validity on its own: under unsupervised
convergence, reading a merged state is an *import*, and the three
import strategies (ignore, subset, correct) all live outside
the DAG. That is the reactive, post-hoc answer.

This page is the preventive answer. **Organise the work so that
semantic conflicts do not arise** — and the import strategies stay a
defensive fallback rather than the daily mode.

Commit gives you the *mechanical convergence* primitive. To get
[cooperation](commit_database.md#modes-of-use) out of it, you have to
add a discipline. That discipline is scope decomposition.

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
system can deliver. Richer guarantees require a supervisor. The patterns below let you stay
unsupervised by ensuring the engine never has anything semantically
meaningful to arbitrate.

## Principle: scope ownership

If two writers never touch the same path, convergence has nothing to
arbitrate — the result is the union of disjoint mutations, and every
submitted intent survives intact. Semantic validity becomes a
consequence of structural disjointness.

The shape of that disjointness is application-specific. This page does
not prescribe a recipe — what works in one domain may not transfer to
another, and no pattern has been validated at scale as a general
solution.

## What scope decomposition does not solve

Be honest about the limits of the discipline:

- **Global invariants.** Uniqueness across the whole model (no two
  assets share an SKU, no two users share an email) cannot be enforced
  by partitioning. Two authors writing into disjoint documents can
  still both claim the same global identifier. This requires a
  supervisor — typically a service that mediates allocation.
- **Cross-author semantic dependencies.** If author B's work depends
  on the *meaning* of what author A produced (and not just its
  presence), they are not really cooperating on disjoint scope; they
  are sequential, and need a coordination protocol.
- **Aggregations and analytics.** Sums, joins, derived views over
  multiple authors' contributions still face the contract at read
  time. The
  [import strategies](commit_contract.md#import-strategies) still
  apply to the *derived* state, even if every contributor's
  individual write was clean.

## When a supervisor is required

When the scope cannot be cleanly decomposed — when authors genuinely
need to co-edit the same field, or when global invariants matter —
the right answer is not a better convergence algorithm. It is an
application-level supervisor: a review UI that surfaces clashes for
human arbitration, a semantic gate that refuses commits, a merge UX
that asks an operator to pick. That is the supervised regime named in
the three-regime note in
[Commit Database — Modes of Use](commit_database.md#modes-of-use).

The supervisor is yours to build. The Commit Database does not
provide it; what it provides — the
[import strategies](commit_contract.md#import-strategies) — is the
back-stop at read time, beneath whatever discipline you choose.

## Summary

| Regime                     | Conflict handling                       | Where it lives                                      |
|----------------------------|-----------------------------------------|-----------------------------------------------------|
| **Mechanical convergence** | Silent best-effort, no notion           | The engine — the strongest guarantee without supervision |
| **Cooperation**            | Avoided by scope, by construction       | This page — application discipline                  |
| **Collaboration**          | Resolved by a supervisor (human / rule) | An application layer you build on top               |

The dual-layer contract holds in all three regimes; the discipline you
adopt determines how much of it you have to consume at read time.

## See Also

- [The Dual-Layer Contract](commit_contract.md) — why the engine
  cannot deliver semantic validity on its own, and the three import
  strategies that back-stop any cooperation discipline.
- [Commit Database — Modes of Use](commit_database.md#modes-of-use) —
  the three-regime note that names collaboration, cooperation, and
  mechanical convergence.
