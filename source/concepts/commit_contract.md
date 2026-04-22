# The Dual-Layer Contract

This document describes the contract between the Commit Engine and applications.

## The Contract

The Commit Engine guarantees **structural integrity** but NOT **semantic integrity**.

| Layer           | Guarantees                                         |
|-----------------|----------------------------------------------------|
| **Commit**      | Deterministic merge, DAG consistency, immutability |
| **Application** | Semantic validation when consuming state           |

When concurrent streams converge, mutations are applied using a "best effort" algorithm:

- Mutations targeting non-existent documents or unresolved paths are **silently ignored**
- Business rule violations are NOT detected by the engine

---

## What Commit Provides

| Guarantee               | Description                                 |
|-------------------------|---------------------------------------------|
| **DAG Consistency**     | Commits form a valid directed acyclic graph |
| **Immutability**        | Once committed, data cannot be modified     |
| **Deterministic Merge** | Same inputs always produce the same output  |
| **Content-Addressable** | CommitId = SHA-1(content), tamper-evident   |

---

## What Commit Does NOT Provide

| Not Provided              | Description                                      |
|---------------------------|--------------------------------------------------|
| **Intent Preservation**   | Deterministic arbitration (LWW)                  |
| **Semantic Validation**   | No business rule checking                        |
| **Mutation Notification** | No alert when mutations are silently ignored     |
| **Conflict Detection**    | No notion of conflict — just deterministic merge |

---

## Summary

> **"I guarantee structural integrity. You guarantee semantic integrity.
> Together, we guarantee data integrity. Separately, neither of us can."**
>
> — The Dual-Layer Contract

---

## See Also

- [Commit Overview](commit_overview.md) - Architecture and positioning
- [Commit Patterns](commit_patterns.md) - Application patterns
- [Commit Glossary](commit_glossary.md) - Terminology
