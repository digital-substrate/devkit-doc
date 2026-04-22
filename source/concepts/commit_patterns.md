# Commit Patterns

This document describes application patterns for using the Commit Engine effectively.

## CommitStore (Redux-Inspired)

CommitStore is the recommended pattern for state management, inspired by Redux:

```cpp
class CommitStore {
public:
    void dispatch(std::string const & label,
        std::function<void(std::shared_ptr<AttachmentMutating>const&)> const & function) {
        try {
            auto const ms {mutableState()};
            function(ms);
            commitMutations(label, ms);
        } catch(Viper::Error const & e) {
           notifyDispatchError(e);
        }
    }
};
```

### The Dispatch Pattern

1. **Get mutable state**: Isolated working copy
2. **Apply mutations**: Call `set()`, `update()`, etc.
3. **Commit**: Persist mutations as a new Commit
4. **Notify**: Inform observers of new state

### Dispatch Variants

| Method           | Purpose                       |
|------------------|-------------------------------|
| `dispatch`       | General mutation function     |
| `dispatchPool`   | Execute FunctionPool function |
| `dispatchSet`    | Simple document set           |
| `dispatchDiff`   | Differential update           |
| `dispatchUpdate` | Path-based update             |

---

## State Isolation

### CommitState (Readonly)

Immutable snapshot at a specific commitId:

```cpp
auto state = db->state(commitId);  // std::shared_ptr<CommitState>
auto opt = state->get(attachment, key);  // Returns ValueOptional
if (!opt->isNil()) {
    auto doc = opt->unwrap();  // Read-only access
}
// state->set(...)  // ERROR: CommitState has no set() method
```

### CommitMutableState (Mutable)

Mutable working copy for building mutations:

```cpp
auto state = db->state(commitId);
auto mutable_ = CommitMutableState::make(state);  // Wraps CommitState
mutable_->set(attachment, key, document);         // Accumulates mutations
mutable_->update(attachment, key, path, value);
// Later: db->commitMutations("label", mutable_);
```

### Two-Level Read

`CommitMutableState` wraps a `CommitState`:

```
+------------------------------------------------------------+
|                    CommitMutableState                      |
|  +-------------+         +-----------------------------+   |
|  |  mutations  |         |        CommitState          |   |
|  |  (pending)  |         |  (immutable, cached)        |   |
|  +-------------+         +-----------------------------+   |
|         |                            |                     |
|    hasDocumentSet?              _get(ccKey)                |
|         |                            |                     |
|    YES: Skip CommitState    NO: Apply mutations on result  |
+------------------------------------------------------------+
```

---

## XArray: CRDT Pattern

XArray provides CRDT-like behavior for ordered lists with concurrent editing.

### The Problem with Integer Indices

Traditional arrays fail with concurrent insertions:

```
Base state:    [a, b, c]
Client A:      insert X at index 1  ->  [a, X, b, c]
Client B:      insert Y at index 1  ->  [a, Y, b, c]
Merge:         AMBIGUOUS! Which element is at index 1?
```

### The Solution: UUID Positions

XArray uses UUID-based positions instead of indices:

```cpp
std::vector<UUId> _positions;           // Ordered by insertion
std::set<UUId> _disablePositions;       // Tombstones
std::map<UUId, std::shared_ptr<Value>> _elements;
```

### Concurrent Insertions Coexist

```
Base state:    [pos1, pos2, END]
Client A:      insert newPosA BEFORE pos2
Client B:      insert newPosB BEFORE pos2

Merge:         [pos1, newPosA, newPosB, pos2, END]
               Both elements coexist. Deterministic ordering.
```

### Tombstoning

Tombstones are created when a commit containing `XArray_Insert` is **disabled**:

```cpp
void ignore(opcode, result) {  // Called for DISABLED commits
    if (opcode->type == XArray_Insert) {
        xarray->insertPosition(before, pos);  // Insert position
        xarray->disablePosition(pos);          // Then TOMBSTONE it
    }
}
```

This ensures:

- Position ordering preserved for disabled commits
- Updates to tombstoned positions silently ignored
- Disabled work cannot be "resurrected"

---

## Undo/Redo Pattern

Commit Engine provides tree-based undo/redo via Disable/Enable:

```
Timeline:
A -> B -> C -> D (current)

Undo B:
A -> B -> C -> D -> Disable(B)

State at Disable(B):
- B's mutations are skipped during evaluation
- C, D mutations still apply (if paths exist)

Redo B:
A -> B -> C -> D -> Disable(B) -> Enable(B)
```

### CommitUndoStack

```cpp
class CommitUndoStack {
    // Stack of (commitId, disableCommitId) pairs
    void undo();  // Disable the top commit
    void redo();  // Enable the disabled commit
};
```

---

## Synchronization Pattern

`CommitSynchronizer` enables synchronization between databases:

```
1. Fetch: Unknown source commits/blobs -> add to target
2. Push: Unknown target commits/blobs -> add to source
```

### Incremental Transfer

- Commits added via topological sort (parents first)
- Small blobs packed together to reduce RPC traffic
- Definitions merged before commits

---

## Value Reconstruction Optimization

### Two-Phase Algorithm

When reading a document via `CommitState::get()`:

```
evalActions:  [A0] [A1] [A2] [A3] [A4] [A5]
                        ^DocumentSet

Forward Scan ----------------->
              i=0  i=1  i=2 (found!)

Backward Sweep <---------------
              i=0 <- i=1 <- i=2

Result: Apply opcodes from A0, A1, A2 only
```

`Document_Set` establishes a baseline, making later opcodes irrelevant.

### Transparent Memoization

`CommitState` caches reconstructed values:

| Aspect       | Details                                               |
|--------------|-------------------------------------------------------|
| Cache Key    | `(attachmentRuntimeId, instanceId, conceptRuntimeId)` |
| Invalidation | None required - `CommitState` is immutable            |
| Statistics   | `cacheHitRate()` returns hit ratio                    |

---

## Concurrent Operations Matrix

| Type         | Concurrent Operations              | Outcome                |
|--------------|------------------------------------|------------------------|
| **Document** | `Set` vs `Set`                     | Last evaluated wins    |
| **Document** | `Update(path1)` vs `Update(path2)` | Both apply (disjoint)  |
| **Document** | `Update(path)` vs `Update(path)`   | Last evaluated wins    |
| **Set**      | `Union` vs `Union`                 | Union of unions        |
| **Set**      | `Union(x)` vs `Subtract(x)`        | Order-dependent        |
| **Map**      | `Union(k1,v1)` vs `Union(k2,v2)`   | Both apply if k1 != k2 |
| **Map**      | `Union(k,v1)` vs `Union(k,v2)`     | Last evaluated wins    |
| **XArray**   | `Insert` vs `Insert`               | Both coexist (UUID)    |
| **XArray**   | `Remove(pos)` vs `Update(pos)`     | Order-dependent        |

---

## See Also

- [The Dual-Layer Contract](commit_contract.md) - Obligations
- [Commit Overview](commit_overview.md) - Architecture
- [Commit Glossary](commit_glossary.md) - Terminology
