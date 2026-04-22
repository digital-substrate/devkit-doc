# Design Patterns

This document catalogs the essential design patterns used in Viper Runtime, focusing on
the patterns that define its architecture.

## Overview

Viper employs a consistent set of design patterns across its 20 domains and ~570 .hpp
files. These patterns ensure type safety, memory safety, and maintainability.

| Category       | Count | Most Common                              |
|----------------|-------|------------------------------------------|
| Creational     | 6     | Token Pattern, Factory Method            |
| Structural     | 9     | Adapter, Composite, Facade               |
| Behavioral     | 11    | Strategy, Template Method, Command       |
| Viper-Specific | 5     | Metadata Everywhere, Content-Addressable |

---

## Token Constructor Pattern

**Intent**: Force all construction through factory methods.

A private `struct Token{}` parameter prevents direct construction while still allowing
`std::make_shared`:

```cpp
class ValueDouble : public Value {
public:
    struct Token {};

    ValueDouble(Token, double value);  // Cannot call directly

    static std::shared_ptr<ValueDouble> make(double value) {
        return std::make_shared<ValueDouble>(Token{}, value);
    }
};
```

**Benefits**:

- Prevents accidental stack allocation
- Guarantees `shared_ptr` ownership
- Enables validation in factory before construction
- Self-documenting API - only `make()` is usable

**Used In**: All 21 domains

---

## Content-Addressable Storage

**Intent**: Identify objects by cryptographic hash of their content.

```cpp
// BlobId is computed from layout + blob data using SHA-1
BlobId blobId{layout, blob};  // Constructor computes hash
blobId.hexString();           // -> "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
blobId.isValid();             // -> true (not Invalid)
```

| Identifier | Hash  | Content           | Size     |
|------------|-------|-------------------|----------|
| BlobId     | SHA-1 | layout + data     | 20 bytes |
| CommitId   | SHA-1 | serialized header | 20 bytes |
| RuntimeId  | MD5   | type structure    | 16 bytes |

**Benefits**:

- Automatic deduplication
- Integrity verification
- Distributed consistency

**Used In**: Blob System, Commit System, Type System

---

## TypeCode Dispatch

**Intent**: Fast polymorphic dispatch without C++ RTTI.

Instead of `dynamic_cast`, Viper uses `TypeCode` enum with switch statements:

```cpp
void serialize(std::shared_ptr<Value const> const & value, StreamWriting & writer) {
    switch (value->typeCode()) {  // Virtual method on Value
        case TypeCode::Int32:
            writer.writeInt32(ValueInt32::cast(value)->value);
            break;
        case TypeCode::Double:
            writer.writeDouble(ValueDouble::cast(value)->value);
            break;
        // ... 33 cases total
    }
}
```

**Benefits**:

- Switch compiles to jump table (O(1))
- Works with `-fno-rtti` compiler flag
- Compiler warns on missing cases
- TypeCode transmitted via RPC

**Used In**: All serialization, encoding, path navigation

---

## Strategy Pattern

**Intent**: Define a family of algorithms, encapsulate each one, and make them
interchangeable.

```cpp
// Interface
class StreamCodecInstancing {
    virtual std::shared_ptr<StreamEncoding> createEncoder() const = 0;
    virtual std::shared_ptr<StreamDecoding> createDecoder(Blob const & blob) const = 0;
};

// Implementations
class StreamBinaryCodec : public StreamCodecInstancing { ... };
class StreamTokenBinaryCodec : public StreamCodecInstancing { ... };
class StreamRawCodec : public StreamCodecInstancing { ... };
```

**Used In**:

- Codecs (`StreamCodecInstancing`)
- Hashing (`Hashing` interface)
- Database (`Databasing` interface)
- Storage (`ValueVectorStoring`)

---

## Interface Segregation (Read/Write)

**Intent**: Separate reading and writing operations into distinct interfaces.

| Read Interface      | Write Interface      | Implementations                    |
|---------------------|----------------------|------------------------------------|
| `AttachmentGetting` | `Databasing`         | Database, DatabaseRemote           |
| `BlobGetting`       | `BlobDatabasing`     | Database                           |
| `StreamReading`     | `StreamWriting`      | BinaryReader, BinaryWriter, Hasher |
| `AttachmentGetting` | `AttachmentMutating` | CommitState, CommitMutableState    |

**Benefits**:

- Read-only views can be shared safely
- Multiple implementations (SQLite, Remote, InMemory)
- Easier testing with mock read interfaces

---

## RAII (Resource Acquisition Is Initialization)

**Intent**: Tie resource lifetime to object lifetime.

```cpp
class SQLite {
public:
    SQLite(Token, const string& path) {
        sqlite3_open(path.c_str(), &_db);
    }
    ~SQLite() {
        sqlite3_close(_db);  // Automatic cleanup
    }
private:
    sqlite3* _db;
};
```

**Benefits**:

- No resource leaks (destructor always called)
- Exception safety (cleanup on stack unwinding)
- Simplified code (no manual cleanup needed)

**Used In**: SQLite, Socket, Semaphore, SharedMemory

---

## Facade Pattern

**Intent**: Provide unified interface to a complex subsystem.

```cpp
// High-level facade
class Database {
public:
    void set(Attachment, Key, Value);
    optional<Value> get(Attachment, Key);
    // ... simple API

private:
    shared_ptr<Databasing> _databasing;  // Delegates to implementation
};
```

| Facade           | Hides                         |
|------------------|-------------------------------|
| `Database`       | SQLite tables, transactions   |
| `CommitDatabase` | 64 commit-related classes     |
| `ServiceRemote`  | RPC connection, serialization |

---

## Command Pattern

**Intent**: Encapsulate requests as objects for serialization and replay.

The program uses 10 opcodes types:

| Opcodes           | Description               |
|-------------------|---------------------------|
| `Document_Set`    | Replace entire document   |
| `Document_Update` | Update at path            |
| `Set_Union`       | Add elements to set       |
| `Set_Subtract`    | Remove elements from set  |
| `Map_Union`       | Add/update map entries    |
| `Map_Subtract`    | Remove map keys           |
| `Map_Update`      | Update existing keys only |
| `XArray_Insert`   | Insert at position        |
| `XArray_Update`   | Update at position        |
| `XArray_Remove`   | Remove at position        |

Each command is:

- Serializable (for persistence)
- Replayable (for state reconstruction)
- Composable (in ValueProgram collections)

---

## Type-Value Duality

**Intent**: For each Type class, provide a corresponding Value class.

| Type          | Value          |
|---------------|----------------|
| TypeDouble    | ValueDouble    |
| TypeVector    | ValueVector    |
| TypeMap       | ValueMap       |
| TypeStructure | ValueStructure |
| TypeKey       | ValueKey       |

This pattern ensures:

- Type describes structure
- Value holds actual data
- Automatic serialization via type metadata

---

## Fluent Interface

**Intent**: Enable method chaining for readable construction.

```cpp
auto path = Path::make()
    ->field("user")
    ->index(0)
    ->field("name");
```

Each method returns `shared_from_this()` for chaining.

**Used In**: Path System

---

## Platform Abstraction

**Intent**: Hide platform differences behind a common interface.

```cpp
#ifdef _WIN32
    SOCKET _socket;
    GUID _uuid;
#else
    int _socket;
    uuid_t _uuid;
#endif
```

**Used In**: IPC (Socket, Semaphore, SharedMemory), Utilities (UUId)

---

## See Also

- [Philosophy](viper_philosophy.md) - Metadata Everywhere principle
- [Type System](viper_type_system.md) - TypeCode dispatch
- [Architecture](viper_architecture.md) - Domain overview
- [Glossary](viper_glossary.md) - Pattern terminology
