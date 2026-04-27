# The Dual-Layer Contract

This page documents the contract between the Commit engine (exposed in Python
through `dsviper`) and your application code. Read it before relying on commit
behavior to validate your data: the engine guarantees **structural integrity**
but not **semantic integrity**.

## The Contract

| Layer           | Guarantees                                         |
|-----------------|----------------------------------------------------|
| **Commit**      | Deterministic merge, DAG consistency, immutability |
| **Application** | Semantic validation when consuming state           |

When concurrent streams converge, mutations are applied using a **best-effort**
algorithm:

- Mutations targeting non-existent documents or unresolved paths are **silently
  ignored**.
- Business rule violations are **not** detected by the engine.

This is by design. The engine is intentionally agnostic to your domain rules
and never refuses a merge — it picks a deterministic outcome and moves on.
Your application is responsible for re-validating the resulting state.

## What Commit Provides

| Guarantee               | Description                                 |
|-------------------------|---------------------------------------------|
| **DAG Consistency**     | Commits form a valid directed acyclic graph |
| **Immutability**        | Once committed, data cannot be modified     |
| **Deterministic Merge** | Same inputs always produce the same output  |
| **Content-Addressable** | `CommitId = SHA-1(content)`, tamper-evident |

## What Commit Does NOT Provide

| Not Provided              | Description                                      |
|---------------------------|--------------------------------------------------|
| **Intent Preservation**   | Deterministic arbitration (LWW), not your intent |
| **Semantic Validation**   | No business rule checking                        |
| **Mutation Notification** | No alert when mutations are silently ignored     |
| **Conflict Detection**    | No notion of conflict — just deterministic merge |

## Implications for `dsviper` Code

The contract shapes how you should write code on top of `dsviper.Commit*`:

- **Do not assume** that every operation you build into a `CommitMutableState`
  will land. After merging concurrent commits, some operations may have been
  silently dropped because their targets disappeared.
- **Re-read the resulting state** through the typed accessors before acting on
  it. The state after `commit_mutations` is the source of truth, not the
  mutations you submitted.
- **Validate at the application boundary.** If your domain has invariants
  (e.g. unique names, referential integrity), enforce them when consuming the
  state, not by hoping the engine will refuse the merge.
- **Distinguish two error families when calling `dsviper`:**
  - *Fail-fast operations* (type system, structural API) raise
    `dsviper.Error` immediately on misuse.
  - *Best-effort operations* (commit merge, mutation application) never raise
    on a "lost" mutation — silence is the signal.

## Summary

> **"I guarantee structural integrity. You guarantee semantic integrity.
> Together, we guarantee data integrity. Separately, neither of us can."**
>
> — The Dual-Layer Contract

## See Also

- [Commit](commit.md) — using the commit API from Python
- [Errors](errors.md) — `dsviper.Error` and exception handling
