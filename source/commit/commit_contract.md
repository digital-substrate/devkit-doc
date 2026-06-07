# The Dual-Layer Contract

This page is load-bearing only for
**[Multi-stream with strong invariants](commit_modes.md#multi-stream-with-strong-invariants)**.
In every other mode listed in
[Modes of Use](commit_modes.md), what follows is
reference material. Reach this page from the diagnostic, not before.

The Commit Database produces **structurally sound but semantically
untrusted output** under reduction. When your invariants are
local, application-side re-validation closes the gap. When they are
strong, re-validation cannot rebuild the intent the reduction
dropped — the contract then describes a gap that must be closed
*upstream*, by re-architecting toward local invariants (see
[Cooperative Discipline](commit_cooperation.md)) or by supervising
reduction with an application layer.

The opposition that decides whether this contract is reference
material or load-bearing — **local vs strong invariants** — is
defined and elaborated in
{ref}`Modes of Use <local-vs-strong-invariants>`.
Re-validating at read time closes the gap for local invariants;
it does **not** close it for strong invariants, where the intent
dropped at reduction is not recoverable downstream.

## A change of discipline

The contract exists because two layers, governed by opposite
disciplines, meet at the reduction boundary.

- **dsviper / Viper C++** applies **fail-fast** at the type and
  structural level: malformed values, undefined paths against a known
  schema, references to absent attachments all raise exceptions
  immediately. Nothing is silently coerced.
- The **Commit Engine**, layered on top, applies **best-effort** at
  the reduction level: when concurrent streams meet, mutations
  whose targets have disappeared after divergence are silently
  dropped so reduction proceeds without human arbitration.

The two are not contradictory — they govern different operations at
different moments. But the discipline changes across the boundary,
and that change is precisely what this contract formalises: the
application takes back, at read time, the strictness the engine
relaxes at reduction time.

### Why the divide exists: complicated vs complex

The boundary is not arbitrary. The engine and the application solve
two qualitatively different problems:

- **Reduction is *complicated*.** Many moving parts — LWW
  arbitration, merge ordering, structural drop rules — but the
  problem is tractable and mechanical: given the same inputs and the
  same merge sequence, the engine always picks the same outcome. It
  is fully solvable in code, once and for all, with no knowledge of
  your domain.
- **Semantic validation is *complex*.** It is not a more elaborate
  flavour of reduction. It is emergent, application-specific, and
  has no closed-form solution: uniqueness, referential integrity,
  cross-field invariants, domain rules all depend on what your data
  *means*. No engine can solve it generically without becoming your
  application.

The engine stops at reduction not because semantic validation is
hard, but because it is *not the engine's problem to solve*. Pushing
it inside would either require the engine to refuse states (breaking
unsupervised reduction) or to encode every application's rules
(breaking generality). The contract keeps the complicated part
mechanical and the complex part where it belongs: at the application
boundary.

## The Contract

| Layer           | Guarantees                                               |
|-----------------|----------------------------------------------------------|
| **Commit**      | Deterministic reduction, DAG consistency, immutability   |
| **Application** | Re-validates engine output before acting on it           |

When concurrent streams are reduced, mutations are applied using a **best-effort**
algorithm:

- Mutations targeting non-existent documents or unresolved paths are **silently
  ignored**.
- Business rule violations are **not** detected by the Commit Database.
- LWW arbitration may keep a value that no single submitted intent would have
  produced.

This is by design. The engine is intentionally agnostic to your domain rules
and never refuses to reduce — it picks a deterministic outcome and moves on.

## Reading the State Is an Import, Not a Load

This is the load-bearing point of the contract.

"Untrusted" usually means *data that crossed a boundary you don't control* —
network input, a deserialized file, an external API. The natural reflex is to
validate at that boundary and then trust the data internally. We call that a
**load**: a one-shot transfer of confidence from an external source into a
trusted in-memory representation.

Best-effort reduction breaks that reflex. **The state returned by
`state(commitId)` is itself a boundary**, even though the data never left the
process. The state is *reconstructed* by replaying the mutations each author
committed, in linearisation order — and a mutation's grain is the verb that
produced it, not the whole value the author had in mind. A `set()` replaces the
**whole document** and supersedes every mutation before it; the
[path-based mutators](commit_database.md#path-based-mutators) (`update` and the
container operations) instead accrete, each on its own path. **The result is
assembled from these mutations, not from the intents behind them.**

For the path-based mutators that carry most concurrent work, that assembly
resolves each shared structure in one of two regimes:

- **Shared path — resolution with loss.** When two heads write the *same*
  path, the last in linearisation order wins and the rest are discarded. No
  value is invented: a value you really submitted wins, verbatim; the others
  are gone, and nothing signals it.
- **Disjoint paths — recombination without loss.** When two heads write
  *different* paths of the same structure, both survive: no field value is
  dropped, and none is fabricated. The recombined structure has no single
  author — with several writers it cannot — but whether that is *owned* or
  *invented* depends on what the paths meant.

A writer **owns** a scope when their whole intent is exactly that scope — all
of it, and nothing outside it. That distinction is the whole of it. If each
writer owned the path they touched, the union is the collective's intent, owned
end to end: trustworthy, though no one person wrote the whole. If
instead `diff` split one author's whole-value intent across those paths, the
union recombines *fragments* no one meant to stand alone — a structure that
answers to no author. The two are indistinguishable field by field: with
nothing lost, every field verbatim, and no invariant broken, per-field
re-validation cannot tell the owned union from the invented one, because each
field, alone, is valid. What ownership certifies is not the fields but the
*combination*.

So name the escalation. *Valid or invalid* is the wrong first question: it
presumes a true state to measure against. *Untrusted* is the working frame —
re-validate on read. And where the paths were fragments, the state is
*invented*: no prior true state exists to recover. Three depths of one gap,
not synonyms.

Structurally the data is sound — types check, paths resolve, the DAG is
consistent. **Semantically, the right question is ownership, not unicity**:
with several writers the state never reflects a *single* intent, so demanding
that is the wrong bar. The state is trustworthy when every surviving value is
one author's whole intent over a scope they alone wrote — and an invention when
any surviving value is a fragment that recombination left standing on its own.

Treat reading `state(commitId)` as an **import**, not a load. An import
acknowledges that the source is structurally well-formed but semantically
foreign: a strategy must be picked for what to do with parts that violate
your domain rules. A load offers no such choice — it assumes the data is
already yours. After best-effort reduction, it is not.

## Three Error Families

Because of this, validation in a `dsviper`-based system happens at three
distinct places, not one:

| Family                           | Origin                                                  | Detected by                         |
|----------------------------------|---------------------------------------------------------|-------------------------------------|
| **Untrusted (external)**         | I/O, deserialization, type mismatch, malformed path     | Engine, fail-fast → `dsviper.Error` |
| **Untrusted (post-reduction)**   | State returned by the Commit Database after reduction   | Application, at read time           |
| **Invalid (semantic)**           | Business-rule violation on otherwise sound data         | Application, at read time           |

The first family is what `dsviper.Error` covers. The other two are entirely
your responsibility — and they share a remediation: **re-validate when you
read the state, not when you build the mutations**.

## What Commit Provides

| Guarantee                     | Description                                                                                                                                                                                                             |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DAG Consistency**           | Commits form a valid directed acyclic graph                                                                                                                                                                             |
| **Immutability**              | Once committed, data cannot be modified                                                                                                                                                                                 |
| **Deterministic Reduction**   | `commitMerge` is a pure function of its ordered inputs — same `(parent, target)` produces the same commit. *Which* order ends up applied across multi-head topologies is an application choice, not an engine property. |
| **Content-Addressable**       | `CommitId = SHA-1(content)`, tamper-evident                                                                                                                                                                             |

```{note}
**Why *reduction* — not *merge*, not *convergence*.** A *merge* in
version-control tools is a reconciliation step that may surface
conflicts and ask a human to arbitrate; the engine does no such thing.
*Convergence*, in the CRDT sense, names an *order-independent* outcome —
the same set of updates yields the same state regardless of the order
they are applied; the engine does not provide that either, because
`commitMerge` is **non-commutative** (`commitMerge(A, B) ≠
commitMerge(B, A)`). What the engine actually does is **reduce**
divergent heads to one by deterministic structural rules: reproducible
given a fixed order, order-dependent, with no semantic arbitration. We
reserve *convergence* for the commutative subset — disjoint paths,
accretive containers (see
[Cooperative Discipline](commit_cooperation.md)) — where reduction
genuinely is order-independent. Everywhere else, it is *reduction*.
```

## How Reduction Picks a Winner

The mechanics — `commitMerge` and the structural rules
that pick a value on each overlapping path — are described in
[Commit Database — How Reduction Picks a Winner](commit_database.md#how-reduction-picks-a-winner).
The summary the contract leans on: the outcome is **deterministic
given a fixed merge sequence**, but its mechanics are *structural*,
not author- or time-meaningful. Two authors editing the same field
have no way to predict which value will survive reduction.

This is what the contract is telling you: do not rely on a specific
arbitration outcome. Re-validate at read time.

## What Commit Does NOT Provide

| Not Provided              | Description                                            |
|---------------------------|--------------------------------------------------------|
| **Intent Preservation**   | Deterministic arbitration (LWW), not your intent       |
| **Semantic Validation**   | No business rule checking                              |
| **Mutation Notification** | No alert when mutations are silently ignored           |
| **Conflict Detection**    | No notion of conflict — just deterministic reduction   |

## Import Outcomes

The four entries below apply to **standard consumers meeting
untrusted state** — code that did not commit to the
defensive-by-design route from day one. They are commonly framed
as "strategies"; under strong invariants they are better described
as **modes of loss**: none re-enters the DAG, none recovers intent.

The trigger for import is the merge itself, not concurrency or
automation. A strictly linear history is a *load*: every mutation
you submitted is exactly the one that contributed to the state. The
moment the history contains a `commitMerge` — unsupervised reducer
or human desktop merge — best-effort drops have been applied
silently, and reading becomes an *import*.

That state answers to no single human intent. Where streams overlap,
reduction picks by structural rule and can preserve a combination no
contributor would have written — **its author is the mechanism, not a
person.** So none of the outcomes below *recovers* a true state; there
is none to recover. Read them as structural consequences, not degrees
of developer fault — the failure is a mechanical reduction applied
where intent had to survive, not the code left coping with the result.

| Outcome              | What the application does   | Resulting state                             |
|----------------------|-----------------------------|---------------------------------------------|
| **Ignore**           | Consume the state as-is     | *untrusted* — stays in the DAG, unvalidated |
| **Extract a subset** | Validate, drop what fails   | *partial* — disconnected from the DAG       |
| **Correct**          | Validate, repair what fails | *phantom* — disconnected from the DAG       |
| **Reject**           | Refuse the state            | *none* — nothing produced                   |

Read this as a hierarchy of failure modes, not a menu. Under strong
invariants:

- **Ignore** — deferral, not a strategy: it treats the import as a
  load. The unvalidated violation surfaces later, in code that assumed
  the invariants held.
- **Extract a subset** — invention by subtraction: to make the
  fragment validate, it deletes the records that carry the violation,
  manufacturing consistency by erasing the evidence of its own
  inconsistency. It carries *less* than the reduced state, not more.
- **Correct** — invention by addition, the mirror of Extract: instead
  of deleting the violating record it overwrites it with a fabricated
  value that has no `CommitId`. Once a write builds on it, the
  fabrication enters the DAG as if authored.
- **Reject** — the only honest answer under strong invariants: it
  concedes mechanical reduction was the wrong primitive, and pushes
  resolution outside the import — human intervention, rollback, or a
  coordination protocol.

**Commit has no notion of conflict** — there is nothing for the
application to push back into. The engine has already produced the
reduced state; whatever the application does with the result lives
outside the DAG.

If you reach for one of these outcomes regularly in code that guards
strong invariants, that is the diagnostic, not the solution. The
next move is upstream: re-design toward
[Multi-stream with local invariants](commit_modes.md#multi-stream-with-local-invariants)
via scope decomposition (see
[Cooperative Discipline](commit_cooperation.md)), or build an
application-level supervisor. Under local invariants these outcomes
remain available as defensive fallbacks — no longer load-bearing.

## Re-entering the graph

Reading a state is half the cycle; writing it back is the other half, and
the verb you write it back with decides what the Commit Database *is* under
concurrency.

**Writing back with `update` / `diff`.** Path-based write-back keeps the
per-path behaviour: concurrent authors who touch different paths have their
edits recombined rather than overwritten. Whether that recombination is a cure
or an invention turns on **ownership** — does each writer own the scope they
touch? When the path *is* the unit of intent, every contribution is a whole
owned intent and the union is trustworthy (the cooperative case). When `diff`
splits one author's whole-value intent into sub-scopes instead, those fragments
recombine into a value no one owns alone — and the same minimality carries it
across the cycle: at input it records a path-scoped operation from a
whole-value edit, attributing a scope the author need not have meant; at
reduction it lets the fragments recombine into a structure no author wrote; and
when a corrected read is written back, it diffs against that reconstructed
state, so a value derived from it enters the DAG as authored. Path-based
write-back is the cure under ownership and the cost without it.

**Writing back with `set`.** A whole-document write replaces the document and
does not recombine. Concurrent writers to the same document are not folded
together — one whole document survives and the others are dropped. The
recombination is gone, and with it the appearance that several authors
collaborated: the Commit Database is then a key-value store with history.

Neither verb is collaboration. `set` gives an honest versioned store where a
contested document keeps one whole version — which one is a
[head-reduction strategy](commit_database.md#how-reduction-picks-a-winner)
choice, not an intent; `update` / `diff` gives recombination — trustworthy when
each scope is owned, an invention when it is a fragment. The architecture
decision is which of the two you mean to build — and to make it on purpose, not
by reaching for whichever verb is nearest.

**Choosing the grain.** Owning a scope is something you *do*, and the lever is
write granularity. `diff` delegates that to structural difference — it splits
wherever values differ, recursively down to the leaf — so it can fragment
fields that form one semantic unit. Only you know which fields are bound: a
translation vector, a `(min, max)` pair, the components of a quaternion. Write
each such unit as a single `update` on the unit's path rather than letting
`diff` pick the grain. The cost is deliberate: two concurrent edits inside one
unit then collide on a shared path — one whole edit lost — instead of
recombining into a value neither author wrote. For bound fields that is the
trade you want: an overt, detectable loss beats a silent invention. `diff` is
safe only where the leaves already are the atoms; otherwise prefer several
targeted `update`s — that is how a path becomes a scope someone owns.

## Implications for `dsviper` Code

The contract shapes how you should write code on top of `dsviper.Commit*`:

- **Treat the post-reduction state as an import boundary.** It is the
  symmetric equivalent of deserialized network input: structurally sound,
  semantically unverified.
- **Do not assume** that every operation you build into a `CommitMutableState`
  will land. After concurrent streams are reduced, some operations may have been
  silently dropped because their targets disappeared.
- **Pick an import outcome explicitly, and name it as such.** Do not
  let it emerge from where you happen to validate. If you find
  yourself reaching for *Correct* or *Ignore* in code that handles
  strong invariants, that is the signal to move the conversation
  upstream — see [Cooperative Discipline](commit_cooperation.md).
- **Validate at the application boundary,** which means
  the Commit Database output. If your domain has invariants (uniqueness,
  referential integrity, cross-field consistency), enforce them when consuming
  the state.

## Summary

> **"I guarantee structural integrity. I hand you back data that is
> structurally sound but semantically untrusted. You re-validate it
> on read."**
>
> — The Dual-Layer Contract

Whether re-validation closes the loop depends on the architecture
upstream of this page:

- **Naturally local invariants** — nothing for the engine to
  silently break. Re-validation is unnecessary; the contract is
  reference material.
- **Defensive-by-design** — the application is built to tolerate
  broken integrity (load robustly, surface, expose correction).
  Re-validation is part of the design. The Graph Editor's
  `ModelIntegrity` pool exemplifies this — an uncommon
  architectural choice.
- **Standard application with strong invariants** — re-validation
  cannot close the loop. The intent dropped at reduction is not
  recoverable, and the application was not built to tolerate the
  drop. The contract describes a gap; closing it requires
  re-architecting upstream, not a better outcome downstream.

## See Also

- [Modes of Use](commit_modes.md) — the diagnostic that determines whether this page applies to you
- [Cooperative Discipline](commit_cooperation.md) — the modelling exit for applications whose invariants are too strong
  for mechanical reduction
- [Commit Database](commit_database.md) — using the commit API from Python
- [Errors](../dsviper/errors.md) — `dsviper.Error` and exception handling
