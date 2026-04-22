# Industry Context

This document establishes that Viper's conflict handling follows **industry-standard
patterns** used by Google Docs, Figma, Notion, and other collaborative systems.

## The Universal Pattern

All major collaborative editing systems share the same approach: **deterministic
convergence without user intervention**. When concurrent operations conflict, the system
resolves them automatically—never prompting the user.

| System      | Technology | On Deleted Target   | User Notification |
|-------------|------------|---------------------|-------------------|
| Google Docs | OT         | Op becomes NOP      | None              |
| Figma       | CRDT       | Op becomes NOP      | None              |
| Notion      | LWW        | Op becomes NOP      | None              |
| Yjs         | CRDT       | Op becomes NOP      | None              |
| Automerge   | CRDT       | Op becomes NOP      | None              |
| **Viper**   | DAG + LWW  | Deterministic No-Op | None              |

**Key insight**: Viper's Deterministic No-Op is not a design flaw—it is the *
*industry-standard behavior** for handling operations that target deleted or non-existent
elements.

---

## Why Every System Uses Deterministic No-Op

### The OT (Operational Transformation) Precedent

Google Docs pioneered real-time collaboration using OT. When User A deletes a paragraph
while User B edits it, User B's operation becomes a NOP (no-op). No notification is sent.

This is **identical** to Viper's Deterministic No-Op behavior.

### The CRDT Precedent

Figma, Notion, and Linear use CRDTs. When concurrent operations conflict (e.g., update a
deleted node), the delete wins and the update becomes NOP. No notification is sent.

Again, **identical** to Viper's behavior.

---

## Why No System Notifies Users

1. **Latency and UX**: Real-time systems merge in milliseconds. Pausing for confirmation
   would destroy the fluid editing experience.

2. **Frequency**: Micro-conflicts happen constantly. Notifying every Deterministic No-Op
   would create notification fatigue.

3. **Already Resolved**: Unlike Git, the conflict is already resolved. There's nothing for
   the user to do.

4. **Application-Specific**: No generic system can know what constitutes a "meaningful"
   conflict for your domain.

---

## The Dual-Layer Contract is Universal

Every collaborative system implements a version of Viper's Dual-Layer Contract:

| Layer              | Responsibility                                 |
|--------------------|------------------------------------------------|
| **Infrastructure** | Structural integrity, convergence, persistence |
| **Application**    | Semantic validation, business rules            |

This is not a "delegation of responsibility"—it is the **only viable design** for systems
that must handle arbitrary application domains.

---

## What Makes Viper Different

Viper is **transparent** about this architecture:

1. **Documents the behavior explicitly** (Deterministic No-Op, Best-Effort Merge)
2. **Provides the vocabulary** to discuss it (Divergence, Visibility Oscillation)
3. **Offers extension points** for notification if needed

The difference is not in behavior—it is in **transparency and documentation**.

---

## See Also

- [The Dual-Layer Contract](commit_contract.md) - Obligations when using Commit
- [Commit Overview](commit_overview.md) - Architecture
- [Commit Glossary](commit_glossary.md) - Terminology
