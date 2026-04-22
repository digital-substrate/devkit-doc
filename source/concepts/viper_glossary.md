# Viper Runtime Glossary

This glossary defines the core terms used in Viper Runtime documentation.

---

## Core Concepts

| Term                           | Definition                                                                                               |
|--------------------------------|----------------------------------------------------------------------------------------------------------|
| **Viper**                      | Metadata-driven C++ runtime providing unified Type/Value system, serialization, database, and RPC        |
| **dsviper**                    | Python wheel exposing Viper to Python. Strong-typed layer that raises exceptions on type mismatch        |
| **P_Viper**                    | Hand-written Python C/API binding (48K LOC) in `src/P_Viper/`                                            |
| **Metadata Everywhere**        | Core principle: runtime metadata drives serialization, validation, RPC, and Python binding               |
| **Reference Semantics**        | Primitives are immutable; containers are mutable via `shared_ptr` (like Python). Use `copy()` for deep copy |
| **Proactive Philosophy**       | Invalid operations raise exceptions immediately, never silently ignored (contrast: Commit's best-effort) |
| **Token Constructor Pattern**  | Private `struct Token{}` forces all construction through `make()` factories                              |

---

## Type System

| Term                   | Definition                                                                                       |
|------------------------|--------------------------------------------------------------------------------------------------|
| **Type**               | Abstract base class defining `typeCode`, `runtimeId`, `representation()`, `equal()`, `compare()` |
| **TypeCode**           | Enum of 33 codes for fast polymorphic dispatch without RTTI                                      |
| **RuntimeId**          | UUID computed by MD5 hash of type structure, guarantees C++/Python compatibility                 |
| **TypePrimitive**      | Atomic types: Bool, Int8-64, UInt8-64, Float, Double, String, BlobId, CommitId, UUId, Void       |
| **TypeStructure**      | Compound type with named fields                                                                  |
| **TypeEnumeration**    | Enumerated type with named cases                                                                 |
| **TypeConcept**        | Abstract entity type with optional parent for inheritance                                        |
| **TypeClub**           | Collection of TypeConcepts for polymorphic grouping                                              |
| **TypeOptional**       | Container for nullable values: `Optional<T>`                                                     |
| **TypeVector**         | Dynamic array: `vector<T>`                                                                       |
| **TypeSet**            | Ordered set: `set<T>`                                                                            |
| **TypeMap**            | Dictionary: `map<K, V>`                                                                          |
| **TypeVariant**        | Union type: `variant<T1, T2, ...>`                                                               |
| **TypeXArray**         | CRDT array with UUID positions for concurrent editing                                            |
| **TypeKey**            | Wrapper type for database keys referencing concept instances                                     |
| **Type-Value Duality** | For each TypeX exists a corresponding ValueX                                                     |

---

## Value System

| Term                   | Definition                                                                                              |
|------------------------|---------------------------------------------------------------------------------------------------------|
| **Value**              | Abstract base for all values. Defines `type()`, `hash()`, `equal()`, `compare()`, `copy()`              |
| **Value\<Primitive\>** | Primitive values (ValueBool, ValueInt32, ValueDouble, etc.) with constants `Zero()`, `One()`, `Empty()` |
| **ValueVector**        | Dynamic container with Python-like API: append, insert, pop, index                                      |
| **ValueMap**           | Ordered dictionary with get, set, keys, values, items                                                   |
| **ValueSet**           | Ordered set with add, remove, union, intersection                                                       |
| **ValueStructure**     | Named structure with typed fields, created via TypeStructureDescriptor                                  |
| **ValueEnumeration**   | Enumeration case value, created via TypeEnumerationDescriptor                                           |
| **ValueOptional**      | Nullable wrapper with `isNil()`, `unwrap()`, `get()`, `wrap()`, `clear()`                               |
| **ValueKey**           | Typed reference to a concept instance (instanceId + typeConcept)                                        |
| **ValueXArray**        | CRDT array with UUID positions for concurrent editing                                                   |

---

## Key System

| Term           | Definition                                                         |
|----------------|--------------------------------------------------------------------|
| **Key**        | Lightweight struct (instanceId, runtimeId) for attachment lookups  |
| **ValueKey**   | Complete key as Value with type metadata                           |
| **instanceId** | Unique UUID identifying a specific instance of a Concept           |

---

## Path System

| Term              | Definition                                                                          |
|-------------------|-------------------------------------------------------------------------------------|
| **Path**          | Sequence of PathComponents for navigation in values: `at()` (read), `set()` (write) |
| **PathComponent** | Single navigation step: Field, Index, Key, Unwrap, Entry, Element, Position         |

---

## Blob System

| Term           | Definition                                                           |
|----------------|----------------------------------------------------------------------|
| **Blob**       | Binary data container (`std::vector<uint8_t>`)                       |
| **BlobId**     | SHA-1 identifier (20 bytes) for content-addressable storage          |
| **BlobLayout** | Type metadata (DataType + component count) for binary interpretation |

---

## Definitions System

| Term            | Definition                                                                                                       |
|-----------------|------------------------------------------------------------------------------------------------------------------|
| **Definitions** | Central registry for user-defined types. Exclusive factory for Structure, Enumeration, Concept, Club, Attachment |
| **Attachment**  | Typed Key-Document association defining a conceptual `map<Key, Document>`                                        |
| **NameSpace**   | Scope where types are defined, identified by UUID                                                                |

---

## Attachment Interfaces

| Term                   | Definition                                                                          |
|------------------------|--------------------------------------------------------------------------------------|
| **AttachmentGetting**  | Abstract read-only interface: `keys()`, `has()`, `get()`                            |
| **AttachmentMutating** | Abstract mutation interface extending AttachmentGetting: `set()`, `update()`, etc.  |
| **Databasing**         | Database-specific interface: AttachmentGetting + `set()`, `delete()`                |

Implementations of AttachmentGetting/AttachmentMutating:
- `Database` (via Databasing)
- `CommitState` (read-only snapshot)
- `CommitMutableState` (isolated evaluation context)
- `AttachmentMutatingRemote` (RPC — bidirectional protocol)

---

## Database System

| Term         | Definition                                             |
|--------------|--------------------------------------------------------|
| **Database** | SQLite-backed storage implementing Databasing          |

---

## Serialization

| Term                      | Definition                                                     |
|---------------------------|----------------------------------------------------------------|
| **StreamReading**         | Typed reading interface for primitives, strings, blobs, arrays |
| **StreamWriting**         | Typed writing interface (same types as Reading)                |
| **StreamCodecInstancing** | Factory for encoders/decoders (Binary, TokenBinary, Raw)       |
| **Codec**                 | Encoder/decoder pair for object-to-binary conversion           |

---

## Hashing

| Term      | Definition                                                |
|-----------|-----------------------------------------------------------|
| **SHA-1** | Cryptographic hash (160-bit) used for BlobId and CommitId |
| **MD5**   | Hash (128-bit) used for RuntimeId generation              |

---

## Network

| Term             | Definition                                                   |
|------------------|--------------------------------------------------------------|
| **RPC**          | Remote Procedure Call protocol for distributed communication |
| **Service**      | Central aggregator of Definitions and FunctionPools          |
| **FunctionPool** | Named container of callable Functions                        |
| **Function**     | Typed callable with prototype validation                     |

---

## Error Handling

| Term             | Definition                                                                                   |
|------------------|----------------------------------------------------------------------------------------------|
| **Viper::Error** | Single exception type with structured format: `[process@host]:Component:Domain:Code:Message` |
| **XxxErrors**    | Namespaces grouping related error codes (TypeErrors, ContainerErrors, DatabaseErrors, etc.)  |

---

## Python Binding

| Term                 | Definition                                                               |
|----------------------|--------------------------------------------------------------------------|
| **Seamless Wrapper** | P_Viper's metadata-driven conversion from Python natives to Viper Values |
| **ViperError**       | Python exception type for Viper errors                                   |

---

## Patterns

| Term                    | Definition                                                                                     |
|-------------------------|------------------------------------------------------------------------------------------------|
| **Content-Addressable** | Identifiers derived from content hash (SHA-1 for Blob/Commit, MD5 for Type)                    |
| **TypeCode Dispatch**   | Fast polymorphism via switch on TypeCode enum instead of RTTI                                  |
| **Dual Reality**        | Kibo-generated code operates in static "Developer Reality" consuming dynamic "Runtime Reality" |
| **RAII**                | Resource Acquisition Is Initialization - automatic cleanup in destructors                      |

---

## See Also

- [Philosophy](viper_philosophy.md) - Core principles
- [Architecture](viper_architecture.md) - 7-layer model
- [Type System](viper_type_system.md) - Type hierarchy
- [Value System](viper_value_system.md) - Value containers
- [Patterns](viper_patterns.md) - Design patterns
- [Commit Glossary](commit_glossary.md) - Commit Engine terminology
