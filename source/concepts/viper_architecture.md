# Viper Architecture

This document provides a high-level view of the Viper Runtime architecture.

## The 7-Layer Model

Viper Runtime is organized into 20 functional domains across 7 layers:

| Layer              | Domains | Files | Responsibility                                      |
|--------------------|---------|-------|-----------------------------------------------------|
| **Infrastructure** | 01-02   | ~26   | IPC/Utilities - Low-level services                  |
| **Foundation**     | 03-07   | ~148  | Type/Value/Key/Path/Error - Core abstractions       |
| **Data**           | 08-11   | ~168  | Blob/Definitions/DSM/Attachment - Data organization |
| **Storage**        | 12-13   | ~25   | Database/SQLite - Persistence                       |
| **Serialization**  | 14-16   | ~54   | Stream/Hashing/Encoding - Binary/JSON codecs        |
| **Network**        | 17-19   | ~143  | RPC/Service/Function - Distribution                 |
| **Representation** | 20      | ~6    | Document/HTML - Visualization                       |

**Total**: 20 domains, ~570 .hpp files

---

## Layer Diagram

```
+---------------------------------------------------------------+
|                     Representation (20)                       |  <- Top (UI)
|                     Document / HTML                           |
+---------------------------------------------------------------+
|                        Network (17-19)                        |
|                  RPC / Service / Function                     |
+---------------------------------------------------------------+
|                     Serialization (14-16)                     |
|              Stream/Codec / Hashing / Encoding                |
+---------------------------------------------------------------+
|                        Storage (12-13)                        |
|                     Database / SQLite                         |
+---------------------------------------------------------------+
|                         Data (08-11)                          |
|           Blob / Definitions / DSM / Attachment               |
+---------------------------------------------------------------+
|                      Foundation (03-07)                       |
|             Type / Value / Key / Path / Error                 |
+---------------------------------------------------------------+
|                    Infrastructure (01-02)                     |  <- Base
|                      IPC / Utilities                          |
+---------------------------------------------------------------+
```

---

## Domain Catalog

### Infrastructure Layer (01-02)

| #  | Domain    | Files | Purpose                     | Key Classes                           |
|----|-----------|-------|-----------------------------|---------------------------------------|
| 01 | IPC       | 3     | Inter-process communication | `Socket`, `Semaphore`, `SharedMemory` |
| 02 | Utilities | 23    | Cross-cutting services      | `UUId`, `StringHelper`, `Logger`      |

### Foundation Layer (03-07)

| #  | Domain         | Files | Purpose                  | Key Classes                            |
|----|----------------|-------|--------------------------|----------------------------------------|
| 03 | Type System    | 53    | Unified type hierarchy   | `Type`, `TypeCode`, `TypeStructure`    |
| 04 | Value System   | 44    | Runtime values           | `Value`, `ValueVector`, `ValueMap`     |
| 05 | Key System     | 5     | Concept instance IDs     | `Key`, `ValueKey`, `TypeKey`           |
| 06 | Path System    | 8     | Navigation in structures | `Path`, `PathComponent`                |
| 07 | Error Handling | 38    | Unified exception system | `Viper::Error`, `XxxErrors` namespaces |

### Data Layer (08-11)

| #  | Domain             | Files | Purpose                     | Key Classes                           |
|----|--------------------|-------|-----------------------------|---------------------------------------|
| 08 | Blob System        | 21    | Content-addressable storage | `Blob`, `BlobId`, `BlobLayout`        |
| 09 | Definitions System | 11    | Centralized type registry   | `Definitions`, `DefinitionsCollector` |
| 10 | DSM System         | 124   | Data modeling language      | `DSMDefinitions`, `DSMBuilder`        |
| 11 | Attachment System  | 12    | Key-Document associations   | `Attachment`, `AttachmentGetting`     |

### Storage Layer (12-13)

| #  | Domain             | Files | Purpose                    | Key Classes                 |
|----|--------------------|-------|----------------------------|-----------------------------|
| 12 | Database System    | 12    | Unified persistence facade | `Database`, `Databasing`    |
| 13 | SQLite Integration | 13    | SQLite3 C API abstraction  | `SQLite`, `SQLiteStatement` |

### Serialization Layer (14-16)

| #  | Domain              | Files | Purpose                      | Key Classes                      |
|----|---------------------|-------|------------------------------|----------------------------------|
| 14 | Stream/Codec System | 37    | Binary serialization         | `StreamReading`, `StreamWriting` |
| 15 | Hashing System      | 7     | Content-addressable IDs      | `Hashing`, `HashSHA1`, `HashMD5` |
| 16 | Encoding Utilities  | 14    | JSON/BSON/Base64 conversions | `JsonValueEncoder`, `Base64`     |

### Network Layer (17-19)

| #  | Domain          | Files | Purpose                     | Key Classes                     |
|----|-----------------|-------|-----------------------------|---------------------------------|
| 17 | RPC System      | 120   | Remote procedure call       | `RPCConnection`, `RPCProtocol`  |
| 18 | Service System  | 16    | Function pool exposition    | `Service`, `ServiceRemote`      |
| 19 | Function System | 7     | Typed callable abstractions | `Function`, `FunctionPrototype` |

### Representation Layer (20)

| #  | Domain                | Files | Purpose                     | Key Classes                       |
|----|-----------------------|-------|-----------------------------|-----------------------------------|
| 20 | Representation System | 6     | Document/HTML visualization | `DocumentNode`, `DocumentBuilder` |

---

## Core Data Flows

### Type -> Value -> Storage Flow

```
                   TypeCode
                      |
                      v
    +-------------------------------------+
    |           Type System               |
    |  TypeStructure, TypeEnumeration     |
    +-------------------------------------+
                  | type()
                  v
    +-------------------------------------+
    |          Value System               |
    |  ValueStructure, ValueVector        |
    +-------------------------------------+
                  | serialize
                  v
    +-------------------------------------+
    |       Stream/Codec System           |
    |   StreamEncoding -> Blob            |
    +-------------------------------------+
                  | persist
                  v
    +-------------------------------------+
    |       Database (SQLite)             |
    +-------------------------------------+
```

### RPC Communication Flow

```
    +-----------------+         +-----------------+
    |     Client      |         |     Server      |
    +--------+--------+         +--------+--------+
             |                           |
             |  RPCPacketCallFunction    |
             |-------------------------->|
             |                           |
             |                    +------+------+
             |                    |  Service    |
             |                    | FunctionPool|
             |                    +------+------+
             |                           |
             |  RPCPacketReturnValue     |
             |<--------------------------|
             |                           |
```

---

## Domain Dependencies

```
Infrastructure Layer:
  01 IPC              -> (none - low-level)
  02 Utilities        -> (none - low-level)

Foundation Layer:
  03 Type System      -> (none - root domain)
  04 Value System     -> 03
  05 Key System       -> 03, 04
  06 Path System      -> 04
  07 Error Handling   -> (none - cross-cutting)

Data Layer:
  08 Blob System      -> 04
  09 Definitions      -> 03
  10 DSM System       -> 09
  11 Attachment       -> 03, 05

Storage Layer:
  12 Database System  -> 09, 11
  13 SQLite           -> 12

Serialization Layer:
  14 Stream/Codec     -> 04, 08
  15 Hashing          -> 08
  16 Encoding         -> 04, 14

Network Layer:
  17 RPC System       -> 04, 14, 01
  18 Service System   -> 09, 12, 17, 19
  19 Function System  -> 03, 04, 09
```

---

## Runtime Invariants

### Type System Foundation

- **Types** have `TypeCode` for fast dispatch and `RuntimeId` for identity
- **Values** always reference their `Type` via `type()`
- **Definitions** is the exclusive factory for user-defined types

### Content-Addressable Storage

Identifiers are derived from content:

- `BlobId` = SHA-1(layout + data)
- `RuntimeId` = MD5(type structure) -> UUId

### Metadata-Driven Operations

No manual coding for:

- Serialization (TypeCode dispatch in codecs)
- RPC (Definitions synchronization)
- Python binding (automatic type conversion)
- Database schema (Attachment-driven)

---

## See Also

- [Philosophy](viper_philosophy.md) - Design principles
- [Type System](viper_type_system.md) - TypeCode and hierarchy
- [Value System](viper_value_system.md) - Value containers
- [Design Patterns](viper_patterns.md) - Pattern catalog
