# The Dual-Layer Contract

This page documents the contract between the Commit Database (exposed in Python
through `dsviper`) and your application code **in the regime where merges
happen automatically, without human arbitration** — typically multiple authors
writing concurrently into a shared database. In single-user use (desktop
editors, scripting, read-only history), the Commit Database still behaves the
way this contract describes, but the failure modes below do not bite: there is
no unsupervised convergence to worry about. See
[Modes of Use](commit_database.md#modes-of-use) to locate your scenario.

When the contract does apply, read it before relying on commit behavior to
validate your data: the Commit Database produces **structurally sound but
untrusted output**, and your application is what turns it into trusted state.

## A change of discipline

The contract exists because two layers, governed by opposite
disciplines, meet at the convergence boundary.

- **dsviper / Viper C++** applies **fail-fast** at the type and
  structural level: malformed values, undefined paths against a known
  schema, references to absent attachments all raise exceptions
  immediately. Nothing is silently coerced.
- The **Commit Engine**, layered on top, applies **best-effort** at
  the convergence level: when concurrent streams meet, mutations
  whose targets have disappeared in another branch are silently
  dropped to keep the DAG converging without human arbitration.

The two are not contradictory — they govern different operations at
different moments. But the discipline changes across the boundary,
and that change is precisely what this contract formalises: the
application takes back, at read time, the strictness the engine
relaxes at convergence time.

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

## Why the Engine's Output Is Untrusted Data

This is the load-bearing point of the contract.

"Untrusted" usually means *data that crossed a boundary you don't control* —
network input, a deserialized file, an external API. The natural reflex is to
validate at that boundary and then trust the data internally.

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
any single coherent intent. That makes engine output equivalent to untrusted
data from the application's perspective.

## Three Error Families

Because of this, validation in a `dsviper`-based system happens at three
distinct places, not one:

| Family                           | Origin                                              | Detected by                         |
|----------------------------------|-----------------------------------------------------|-------------------------------------|
| **Untrusted (external)**         | I/O, deserialization, type mismatch, malformed path | Engine, fail-fast → `dsviper.Error` |
| **Untrusted (post-convergence)** | State returned by the Commit Database after convergence      | Application, at read time           |
| **Invalid (semantic)**           | Business-rule violation on otherwise sound data     | Application, at read time           |

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

When concurrent streams converge, the engine has to choose a single
outcome for every overlapping path. The choice is deterministic given
a fixed merge sequence — same inputs, same merges, same result on
every client — but its mechanics are *structural*, not author- or
time-meaningful.

**The merge primitive.** `commitMerge(parent, target)` creates a
merge commit. When the resulting state is reconstructed, `target`'s
mutations are applied *after* `parent`'s — so the target branch
wins all LWW conflicts on overlapping paths. This is the only
arbitration rule the engine itself fixes — and it makes the operation
non-commutative: `commitMerge(A, B) ≠ commitMerge(B, A)`.

**Reducing multiple heads is a strategy, not a guarantee.** The
built-in `reduceHeads` iterates heads in lexicographic `CommitId`
order and calls `commitMerge` once per pair, with the running result
as parent and the next head as target. Applications are free to use a
different order — or to skip `reduceHeads` entirely and issue their
own `commitMerge` sequence. The final state depends on *who calls
commitMerge in what order*, not on a property of the engine.

**None of this preserves intent.** Whichever strategy is used, the
winner of an LWW conflict is a function of how merges were
sequenced — not of authorship, recency, or semantic priority. Two
authors editing the same field have no way to predict which value
will survive convergence, even within a fixed strategy.

This is what the contract is telling you: do not rely on a specific
arbitration outcome. Re-validate at read time.

## What Commit Does NOT Provide

| Not Provided              | Description                                            |
|---------------------------|--------------------------------------------------------|
| **Intent Preservation**   | Deterministic arbitration (LWW), not your intent       |
| **Semantic Validation**   | No business rule checking                              |
| **Mutation Notification** | No alert when mutations are silently ignored           |
| **Conflict Detection**    | No notion of conflict — just deterministic convergence |

## Implications for `dsviper` Code

The contract shapes how you should write code on top of `dsviper.Commit*`:

- **Treat the post-convergence state as a boundary.** It is the symmetric
  equivalent of deserialized network input: structurally sound, semantically
  unverified.
- **Do not assume** that every operation you build into a `CommitMutableState`
  will land. After concurrent streams converge, some operations may have been
  silently dropped because their targets disappeared.
- **Validate at the application boundary,** which means
  the Commit Database output. If your domain has invariants (uniqueness,
  referential integrity, cross-field consistency), enforce them when consuming
  the state.

## Summary

> **"I guarantee structural integrity. I hand you back data that is
> structurally sound but semantically untrusted. You re-validate it on read.
> Together, we guarantee data integrity. Separately, neither of us can."**
>
> — The Dual-Layer Contract

## See Also

- [Commit Database](commit_database.md) — using the commit API from Python
- [Errors](../dsviper/errors.md) — `dsviper.Error` and exception handling
