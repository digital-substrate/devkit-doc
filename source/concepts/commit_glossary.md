# Commit Engine Glossary

This glossary defines terms specific to the Commit Engine. For Viper Runtime terms,
see [Viper Glossary](viper_glossary.md).

---

## Core Concepts

| Term                    | Definition                                                                                                             |
|-------------------------|------------------------------------------------------------------------------------------------------------------------|
| **Dual-Layer Contract** | Commit guarantees structure; application guarantees semantics                                                          |
| **Best-Effort Merge**   | Deterministic merge where unresolved mutations become Deterministic No-Op                                              |
| **Deterministic No-Op** | Mutation completes without effect when path cannot be resolved (industry-standard behavior, same as Google Docs/Figma) |
| **Divergence**          | When concurrent streams modify data incompatibly                                                                       |
| **DAG**                 | Directed Acyclic Graph for commit history and convergence                                                              |

---

## Multiplayer Terminology

| Term                 | Definition                                               |
|----------------------|----------------------------------------------------------|
| **Multiplayer**      | Multiple users editing concurrently with automatic merge |
| **Parallel Editing** | Isolated edits merged at sync time                       |
| **Arbitration**      | Deterministic merge mechanism (LWW for CommitDatabase)   |

> **Industry Context**: By market standards, "collaborative" describes any multi-user
> system with automatic convergence — CommitDatabase qualifies, as do Figma, Google Docs,
> Yjs, and Automerge. This glossary uses precise technical terms for clarity.

---

## Commit Types

| Type        | Description                                                                                                                                                  |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Mutations` | Normal commit containing ValueProgram                                                                                                                        |
| `Disable`   | Evaluates the target commit's opcodes in **ignore** mode (XArray positions are tombstoned, other opcodes become no-ops). Used for Undo                       |
| `Enable`    | Re-evaluates the target commit's opcodes in **execute** mode (restores normal evaluation). Used for Redo                                                     |
| `Merge`     | Combines two concurrent streams by creating a merge commit (no mutations—only references parents). State obtained by linearizing DAG then evaluating opcodes |

---

## ValueOpcode Types

| Opcode            | Semantics                             |
|-------------------|---------------------------------------|
| `Document_Set`    | Replace entire document (dictatorial) |
| `Document_Update` | Update at path if document exists     |
| `Set_Union`       | Add elements to set                   |
| `Set_Subtract`    | Remove elements from set              |
| `Map_Union`       | Add/update map entries                |
| `Map_Subtract`    | Remove map keys                       |
| `Map_Update`      | Update existing keys only             |
| `XArray_Insert`   | Insert at UUID position (CRDT-like)   |
| `XArray_Update`   | Update at position if not tombstoned  |
| `XArray_Remove`   | Clear value at position (tombstone)   |

---

## Classes

| Class                  | Definition                                                          |
|------------------------|---------------------------------------------------------------------|
| `Commit`               | Immutable program fragment: header + program (opcodes)              |
| `CommitId`             | SHA-1 identifier (20 bytes), content-addressable                    |
| `CommitHeader`         | Metadata: commitId, parentCommitId, timestamp, label, type          |
| `ValueOpcode`          | Single mutation opcode with target key/path                         |
| `ValueProgram`         | Collection of ValueOpcode indexed by key and attachment             |
| `CommitState`          | Readonly state computed by DAG evaluation with cache                |
| `CommitMutableState`   | Mutable state accumulating mutations before commit                  |
| `CommitDatabase`       | High-level facade managing commits, blobs, definitions, DAG         |
| `CommitDatabasing`     | Backend storage interface (SQLite, Remote)                          |
| `CommitDatabaseServer` | Network server exposing CommitDatabase via RPC, manages dataVersion |
| `CommitUndoStack`      | Undo/redo via stack of (commitId, disableCommitId)                  |
| `CommitSynchronizer`   | Synchronization between databases (Fetch/Push/Full Sync)            |
| `CommitEvaluator`      | Virtual CPU executing opcodes in protected mode (`catch(...){}`)    |

---

## Interfaces

| Interface            | Definition                                                 |
|----------------------|------------------------------------------------------------|
| `AttachmentGetting`  | Readonly access: `keys()`, `has()`, `get()` via Attachment |
| `AttachmentMutating` | Mutation access: `set()`, `update()`, `diff()`, etc.       |

---

## See Also

- [Commit Overview](commit_overview.md) - Architecture
- [The Dual-Layer Contract](commit_contract.md) - Obligations
- [Commit Patterns](commit_patterns.md) - Application patterns
- [Viper Glossary](viper_glossary.md) - Viper Runtime terms
