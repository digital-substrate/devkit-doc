# The Dual-Layer Contract

This page is load-bearing only for
**[Multi-stream with strong invariants](commit_modes.md#multi-stream-with-strong-invariants)**.
In every other mode listed in
[Modes of Use](commit_modes.md), what follows is
reference material. Reach this page from the diagnostic, not before.

The Commit Database produces **structurally sound but semantically
untrusted output** under convergence. When your invariants are
local, application-side re-validation closes the gap. When they are
strong, re-validation cannot rebuild the intent the convergence
dropped — the contract then describes a gap that must be closed
*upstream*, by re-architecting toward local invariants (see
[Cooperative Discipline](commit_cooperation.md)) or by supervising
convergence with an application layer.

The opposition that decides whether this contract is reference
material or load-bearing — **local vs strong invariants** — is
defined and elaborated in
{ref}`Modes of Use <local-vs-strong-invariants>`.
Re-validating at read time closes the gap for local invariants;
it does **not** close it for strong invariants, where the intent
dropped at convergence is not recoverable downstream.

## A change of discipline

The contract exists because two layers, governed by opposite
disciplines, meet at the convergence boundary.

- **dsviper / Viper C++** applies **fail-fast** at the type and
  structural level: malformed values, undefined paths against a known
  schema, references to absent attachments all raise exceptions
  immediately. Nothing is silently coerced.
- The **Commit Engine**, layered on top, applies **best-effort** at
  the convergence level: when concurrent streams meet, mutations
  whose targets have disappeared after divergence are silently
  dropped to keep the DAG converging without human arbitration.

The two are not contradictory — they govern different operations at
different moments. But the discipline changes across the boundary,
and that change is precisely what this contract formalises: the
application takes back, at read time, the strictness the engine
relaxes at convergence time.

### Why the divide exists: complicated vs complex

The boundary is not arbitrary. The engine and the application solve
two qualitatively different problems:

- **Convergence is *complicated*.** Many moving parts — LWW
  arbitration, merge ordering, structural drop rules — but the
  problem is tractable and mechanical: given the same inputs and the
  same merge sequence, the engine always picks the same outcome. It
  is fully solvable in code, once and for all, with no knowledge of
  your domain.
- **Semantic validation is *complex*.** It is not a more elaborate
  flavour of convergence. It is emergent, application-specific, and
  has no closed-form solution: uniqueness, referential integrity,
  cross-field invariants, domain rules all depend on what your data
  *means*. No engine can solve it generically without becoming your
  application.

The engine stops at convergence not because semantic validation is
hard, but because it is *not the engine's problem to solve*. Pushing
it inside would either require the engine to refuse states (breaking
unsupervised convergence) or to encode every application's rules
(breaking generality). The contract keeps the complicated part
mechanical and the complex part where it belongs: at the application
boundary.

## The Contract

| Layer           | Guarantees                                               |
|-----------------|----------------------------------------------------------|
| **Commit**      | Deterministic convergence, DAG consistency, immutability |
| **Application** | Re-validates engine output before acting on it           |

When concurrent streams converge, mutations are applied using a **best-effort**
algorithm:

- Mutations targeting non-existent documents or unresolved paths are **silently
  ignored**.
- Business rule violations are **not** detected by the Commit Database.
- LWW arbitration may keep a value that no single submitted intent would have
  produced.

This is by design. The engine is intentionally agnostic to your domain rules
and never refuses to converge — it picks a deterministic outcome and moves on.

## Reading the State Is an Import, Not a Load

This is the load-bearing point of the contract.

"Untrusted" usually means *data that crossed a boundary you don't control* —
network input, a deserialized file, an external API. The natural reflex is to
validate at that boundary and then trust the data internally. We call that a
**load**: a one-shot transfer of confidence from an external source into a
trusted in-memory representation.

Best-effort convergence breaks that reflex. **The state returned by
`state(commitId)` is itself a boundary**, even though the data never left the
process:

- Mutations you submitted may have been silently dropped.
- Two disjoint updates, each individually consistent, may have produced a
  combined state that violates a cross-field invariant.
- LWW may have preserved a value that no submitted commit would have written
  on its own.

Structurally the data is sound — types check, paths resolve, the DAG is
consistent. **Semantically, you have no guarantee** that the result reflects
any single coherent intent.

Treat reading `state(commitId)` as an **import**, not a load. An import
acknowledges that the source is structurally well-formed but semantically
foreign: a strategy must be picked for what to do with parts that violate
your domain rules. A load offers no such choice — it assumes the data is
already yours. After best-effort convergence, it is not.

## Three Error Families

Because of this, validation in a `dsviper`-based system happens at three
distinct places, not one:

| Family                           | Origin                                                  | Detected by                         |
|----------------------------------|---------------------------------------------------------|-------------------------------------|
| **Untrusted (external)**         | I/O, deserialization, type mismatch, malformed path     | Engine, fail-fast → `dsviper.Error` |
| **Untrusted (post-convergence)** | State returned by the Commit Database after convergence | Application, at read time           |
| **Invalid (semantic)**           | Business-rule violation on otherwise sound data         | Application, at read time           |

The first family is what `dsviper.Error` covers. The other two are entirely
your responsibility — and they share a remediation: **re-validate when you
read the state, not when you build the mutations**.

## What Commit Provides

| Guarantee                     | Description                                 |
|-------------------------------|---------------------------------------------|
| **DAG Consistency**           | Commits form a valid directed acyclic graph |
| **Immutability**              | Once committed, data cannot be modified     |
| **Deterministic Convergence** | Same inputs always produce the same output  |
| **Content-Addressable**       | `CommitId = SHA-1(content)`, tamper-evident |

```{note}
**Why *convergence*, not *merge*** — a *merge* in version-control
tools is a reconciliation step that may surface conflicts and ask a
human to arbitrate. The engine does no such thing: when concurrent
streams meet, it linearises them by deterministic structural rules,
never refuses, and never reports a conflict. We call this
*convergence* to keep the two operations distinct: reproducible, but
no semantic arbitration has happened.
```

## How Convergence Picks a Winner

The mechanics — `commitMerge`, `reduceHeads`, the structural rules
that pick a value on each overlapping path — are described in
[Commit Database — How Convergence Picks a Winner](commit_database.md#how-convergence-picks-a-winner).
The summary the contract leans on: the outcome is **deterministic
given a fixed merge sequence**, but its mechanics are *structural*,
not author- or time-meaningful. Two authors editing the same field
have no way to predict which value will survive convergence.

This is what the contract is telling you: do not rely on a specific
arbitration outcome. Re-validate at read time.

## What Commit Does NOT Provide

| Not Provided              | Description                                            |
|---------------------------|--------------------------------------------------------|
| **Intent Preservation**   | Deterministic arbitration (LWW), not your intent       |
| **Semantic Validation**   | No business rule checking                              |
| **Mutation Notification** | No alert when mutations are silently ignored           |
| **Conflict Detection**    | No notion of conflict — just deterministic convergence |

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

| Outcome              | What the application does   | Consequence                                                                       |
|----------------------|-----------------------------|-----------------------------------------------------------------------------------|
| **Ignore**           | Consume the state as-is     | A *latent* state — violations deferred to code that assumed the invariants held   |
| **Extract a subset** | Validate, drop what fails   | A *partial* state — **disconnected from the DAG**                                 |
| **Correct**          | Validate, repair what fails | A *phantom* state — **disconnected from the DAG**                                 |
| **Reject**           | Refuse the state            | No state — resolution moves outside the import                                    |

Read this as a hierarchy of failure modes, not a menu. Under strong
invariants:

- **Ignore** — deferral, not a strategy. It treats the read as a
  load, bypassing the import boundary the contract describes. The
  violation propagates into downstream code written assuming
  invariants held.
- **Extract a subset** — shows a state that is *not* the DAG state.
  Tolerable for read-only audit; once edits resume from it, new
  commits reference a fiction.
- **Correct** — invention dressed as recovery. The application makes
  up a value nobody committed; if a subsequent write builds on it,
  the fiction enters the DAG as if authored.
- **Reject** — the only honest answer when invariants are strong,
  and equivalent to saying mechanical convergence was the wrong
  primitive. Resolution moves outside the import: human intervention,
  rollback, or a coordination protocol.

**Commit has no notion of conflict** — there is nothing for the
application to push back into. The engine has already converged;
whatever the application does with the result lives outside the DAG.

If you reach for one of these outcomes regularly in code that guards
strong invariants, that is the diagnostic, not the solution. The
next move is upstream: re-design toward
[Multi-stream with local invariants](commit_modes.md#multi-stream-with-local-invariants)
via scope decomposition (see
[Cooperative Discipline](commit_cooperation.md)), or build an
application-level supervisor. Under local invariants these outcomes
remain available as defensive fallbacks — no longer load-bearing.

## Implications for `dsviper` Code

The contract shapes how you should write code on top of `dsviper.Commit*`:

- **Treat the post-convergence state as an import boundary.** It is the
  symmetric equivalent of deserialized network input: structurally sound,
  semantically unverified.
- **Do not assume** that every operation you build into a `CommitMutableState`
  will land. After concurrent streams converge, some operations may have been
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
  cannot close the loop. The intent dropped at convergence is not
  recoverable, and the application was not built to tolerate the
  drop. The contract describes a gap; closing it requires
  re-architecting upstream, not a better outcome downstream.

## See Also

- [Modes of Use](commit_modes.md) — the diagnostic that determines whether this page applies to you
- [Cooperative Discipline](commit_cooperation.md) — the modelling exit for applications whose invariants are too strong for mechanical convergence
- [Commit Database](commit_database.md) — using the commit API from Python
- [Errors](../dsviper/errors.md) — `dsviper.Error` and exception handling
