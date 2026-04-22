# Viper Philosophy

This document explains the fundamental design principles that govern Viper Runtime.

## What is Viper?

Viper is a **metadata-driven runtime** (v1.2 LTS) that simplifies C++/Python interoperability through a unified type and value system. It is not a language, framework, or library—it is a complete system for managing structured data.

### Viper as a Data Runtime

Like the JVM runs Java bytecode, Viper runs **typed values**:

| Capability          | Implementation                                        |
|---------------------|-------------------------------------------------------|
| Dynamic type system | 33 TypeCodes with runtime metadata                    |
| Strong typing       | Immediate exceptions on type mismatch                 |
| Auto serialization  | Binary/JSON codecs via TypeCode dispatch              |
| Memory management   | `std::shared_ptr` with reference counting             |
| Cross-language      | Same types in C++ and Python                          |

### Viper as a Mini-OS for Data

Viper provides OS-like services for **data** instead of processes:

| OS Concept      | Viper Equivalent                  |
|-----------------|-----------------------------------|
| File System     | Database (SQLite-backed)          |
| Memory          | Blob storage (content-addressed)  |
| Process State   | CommitState (immutable snapshots) |
| Transactions    | begin/commit/rollback             |
| IPC             | RPC (remote procedure calls)      |
| Version Control | Commit DAG (like Git for data)    |

---

## Principle 0: Think Before You Code

> *"Avant donc que d'écrire, apprenez à penser."* — Boileau

Solve the problem completely at the right architectural level. Do not delegate complexity upward unless the upper layer has domain knowledge you lack.

This principle guides all Viper design decisions and ensures problems are solved where they belong.

---

## Metadata Everywhere

Runtime type metadata drives serialization, validation, RPC, Python binding, and persistence. Every Viper Value object knows its type and can describe itself.

| Mechanism            | Purpose                                               |
|----------------------|-------------------------------------------------------|
| **TypeCode**         | Enum (33 codes) enabling fast polymorphic dispatch    |
| **RuntimeId**        | MD5 hash guaranteeing C++/Python compatibility        |
| **Definitions**      | Central registry providing runtime reflection         |
| **representation()** | Self-describing string format for each Type and Value |

### Implications

1. **No manual serialization code** - Codecs use TypeCode dispatch to serialize any Value
2. **No manual type checking** - TypeChecker validates via metadata automatically
3. **RPC protocol self-describing** - Definitions transmitted with calls

---

## Commit Immutability

The Commit system combines mutability during construction with immutability after persistence.

| Phase            | State                | Mutability | Purpose                        |
|------------------|----------------------|------------|--------------------------------|
| **Construction** | `CommitMutableState` | Mutable    | Build/modify data freely       |
| **Persistence**  | `CommitState`        | Immutable  | Historical snapshot in the DAG |

### Benefits

- **Thread safety**: Committed states are immutable—no locks needed for read access
- **Multiplayer editing**: Each client has isolated `CommitMutableState`, converge at commit
- **Undo/redo**: Navigate the commit DAG (history is immutable)
- **Caching**: Committed values can be cached indefinitely

---

## Reference Semantics

Viper uses reference semantics (like Python) rather than value semantics (like C++ STL). Assignment and parameter passing share the underlying data rather than copying.

| C++ STL (Value Semantics)    | Viper (Reference Semantics)             |
|------------------------------|-----------------------------------------|
| `vector<int> a = b;` copies  | `shared_ptr<ValueVector> a = b;` shares |
| Parameter copy by default    | Parameter shared by default             |
| Explicit std::move for moves | Explicit `copy()` for deep copy         |

### Implications

1. **Python-like behavior** - Natural for Python binding
2. **Efficient by default** - No accidental copies
3. **Explicit when needed** - `Value::copy()` for deep copy

---

## Proactive Philosophy

Viper Runtime follows a **proactive** philosophy: invalid operations raise exceptions immediately.

```cpp
// Viper raises immediately on type mismatch
auto vec = ValueVector::make(TypeVector::make(TypeInt32::Instance()));
vec->append(ValueString::make("hello"));  // throws: expected Int32, got String
```

This contrasts with permissive approaches where errors may pass silently. Viper ensures:

- Type errors caught immediately
- Invalid paths rejected at call time
- No silent data corruption

> **Note**: The Commit Engine operates differently—in best-effort mode, mutations
> targeting non-existent documents or unresolved paths are silently ignored (`catch(...){}`).
> See [Commit Overview](commit_overview.md).

---

## The Viper Paradox

Viper is a **dynamic runtime** (like Python) that is **strongly typed** (unlike Python).

| Aspect        | Python                | Viper                                     |
|---------------|-----------------------|-------------------------------------------|
| Type checking | Runtime, permissive   | Runtime, immediate exceptions             |
| Type errors   | May pass silently     | Always throws immediately                 |
| Type metadata | Limited (`type()`)    | Complete (`TypeCode`, `RuntimeId`, etc.)  |
| Serialization | Manual (pickle, json) | Automatic via metadata                    |

**The best of both worlds**: Viper combines the flexibility of dynamic typing with the safety guarantees of static typing.

---

## See Also

- [Viper Architecture](viper_architecture.md) - 7-layer model
- [Type System](viper_type_system.md) - TypeCode and type hierarchy
- [Value System](viper_value_system.md) - Reference semantics in detail
- [Design Patterns](viper_patterns.md) - Pattern implementations
