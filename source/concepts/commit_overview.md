# Commit Engine Overview

The Commit Engine provides DAG versioning with immutable history, enabling transactional
persistence, undo/redo, and distributed synchronization.

## Positioning

| Aspect     | Viper Runtime         | Commit Engine              |
|------------|-----------------------|----------------------------|
| Status     | Core product          | Specialized                |
| Files      | ~570 .hpp             | 64 .hpp                    |
| Philosophy | Proactive             | Best-effort                |
| Exceptions | Raised immediately    | Recovered (protected mode) |
| Validation | Immediate rejection   | Deterministic No-Op        |
| Scope      | Structural + Semantic | Structural only            |

The Viper Runtime is **complete and standalone**. The Commit Engine adds versioning
capabilities and delegates semantic validation to the application layer.

---

## Architecture

```
+----------------------------------------------------------+
|                      Commit Engine                       |
|                  (built on Viper Runtime)                |
|                                                          |
|  * DAG versioning with immutable history                 |
|  * Best-effort evaluation                                |
|  * Content-addressable commits (SHA-1)                   |
|  * 64 .hpp files                                         |
+----------------------------------------------------------+
                        | built on
+==========================================================+
|                   Viper Runtime                          |
|          Type/Value/Codec/Database/RPC...                |
|                 (20 domains, proactive)                  |
+==========================================================+
```

---

## Key Classes

| Class                | Responsibility                                       |
|----------------------|------------------------------------------------------|
| `Commit`             | Immutable structure: header + program                |
| `CommitId`           | SHA-1 identifier (20 bytes), content-addressable     |
| `CommitHeader`       | Metadata: commitId, parentCommitId, timestamp, label |
| `ValueProgram`       | Indexed collection of ValueOpcode by key             |
| `CommitState`        | Readonly state at a specific commitId                |
| `CommitMutableState` | Mutable state for building mutations                 |
| `CommitDatabase`     | High-level facade managing commits, blobs, DAG       |
| `CommitDatabasing`   | Backend interface (SQLite, Remote)                   |
| `CommitStore`        | State management with undo/redo (Redux-inspired)     |
| `CommitSynchronizer` | Synchronization between databases                    |

---

## Commit Types

| CommitType  | Description                                                                                            |
|-------------|--------------------------------------------------------------------------------------------------------|
| `Mutations` | Normal commit containing ValueProgram                                                                  |
| `Disable`   | Evaluates target commit's opcodes in **ignore** mode (XArray tombstoning, other opcodes become no-ops) |
| `Enable`    | Re-evaluates target commit's opcodes in **execute** mode (restores normal evaluation)                  |
| `Merge`     | Combines concurrent streams by creating merge commit (state via DAG linearization + evaluation)        |

---

## Content-Addressable Commits

Each commit is identified by the SHA-1 hash of its serialized header:

```
CommitId = SHA-1(header blob)
```

This ensures:

- Identical content produces identical IDs
- History cannot be tampered with
- Distributed systems can verify integrity

---

## Philosophy: Best-Effort

The Commit Engine operates in **best-effort** mode, contrasting with Viper's proactive
philosophy:

```cpp
void execute(opcode, result) {
    try {
        // Execute the opcode
    } catch (...) {}  // Exceptions recovered (protected mode)
}
```

**The system always completes. Mutations targeting non-existent elements become
Deterministic No-Ops (same as Google Docs, Figma).**

The `catch(...){}` is a necessary consequence of DAG linearization (similar to OT
evaluation of operations on deleted elements): opcodes may target documents that don't
exist (Document_Set disabled) or unresolved paths. See
[The Dual-Layer Contract](commit_contract.md) for implications.

---

## Interactions with Viper Runtime

| Domain                     | Relation | Via                               |
|----------------------------|----------|-----------------------------------|
| **Value System (04)**      | Uses     | `Value`, `ValueKey`, `ValueSet`   |
| **Path System (06)**       | Uses     | `Path` - navigation in structures |
| **Blob System (08)**       | Uses     | `Blob`, `BlobId` - serialization  |
| **Attachment System (11)** | Uses     | `Attachment` - key scope          |
| **Hashing System (15)**    | Uses     | SHA-1 for CommitId                |
| **Stream/Codec (14)**      | Uses     | `StreamCodecInstancing`           |
| **RPC System (17)**        | Uses     | `CommitDatabaseRemote`            |

---

## Typical Flow

```
1. Mutation:  CommitMutableState::set/update -> accumulates ValueProgram
2. Commit:    CommitDatabase::commitMutations() -> serialize -> compute CommitId -> store
3. Reading:   CommitDatabase::state(commitId) -> DAG traversal -> CommitState (cached)
4. Undo:      disableCommit() -> new Disable commit -> CommitUndoStack::undo()
5. Sync:      CommitSynchronizer::sync() -> compare -> incremental transfer
```

---

## See Also

- [The Dual-Layer Contract](commit_contract.md) - Obligations when using Commit
- [Commit Patterns](commit_patterns.md) - CommitStore and CRDT patterns
- [Commit Glossary](commit_glossary.md) - Terminology
- [Viper Philosophy](viper_philosophy.md) - Proactive vs Best-effort
