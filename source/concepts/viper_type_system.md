# Type System

The Type System is the foundation of Viper's metadata-driven architecture. Every value
knows its type, and type metadata enables automatic serialization, validation, and
cross-language interoperability.

## TypeCode: Fast Polymorphic Dispatch

`TypeCode` is an enum of 33 codes that enables fast polymorphic dispatch without C++ RTTI:

```cpp
enum class TypeCode : std::uint8_t {
    Void = 0,
    Bool,
    UInt8, UInt16, UInt32, UInt64,
    Int8, Int16, Int32, Int64,
    Float, Double,
    BlobId, CommitId, UUId,
    String, Blob,
    Vec, Mat,
    Tuple,
    Optional, Vector, Set, Map, XArray,
    Any, Variant,
    Enumeration, Structure,
    Key,
    Concept, Club, AnyConcept,
};
```

### Benefits of TypeCode

| Benefit            | Explanation                          |
|--------------------|--------------------------------------|
| **Fast dispatch**  | switch/case compiles to jump table   |
| **No RTTI**        | Works with `-fno-rtti` compiler flag |
| **Exhaustive**     | Compiler warns on missing cases      |
| **Cross-language** | TypeCode transmitted via RPC         |

---

## Type Hierarchy

### Primitives

Atomic types with no internal structure:

| TypeCode | C++ Type    | Description           |
|----------|-------------|-----------------------|
| Bool     | bool        | Boolean               |
| Int8-64  | int8-64_t   | Signed integers       |
| UInt8-64 | uint8-64_t  | Unsigned integers     |
| Float    | float       | 32-bit floating point |
| Double   | double      | 64-bit floating point |
| String   | std::string | UTF-8 string          |
| Void     | void        | No value              |
| BlobId   | BlobId      | Content hash (SHA-1)  |
| CommitId | CommitId    | Commit hash (SHA-1)   |
| UUId     | UUId        | 128-bit unique ID     |

### Containers

Typed collections of values:

| TypeCode | Description                        | Element Types   |
|----------|------------------------------------|-----------------|
| Optional | Nullable value (`Optional<T>`)     | Any             |
| Vector   | Dynamic array (`vector<T>`)        | Any             |
| Set      | Ordered set (`set<T>`)             | Any             |
| Map      | Dictionary (`map<K,V>`)            | Any             |
| Tuple    | Fixed heterogeneous (`tuple<...>`) | Any combination |
| Vec      | Fixed math vector (`Vec<T,N>`)     | Numeric         |
| Mat      | Fixed math matrix (`Mat<T,M,N>`)   | Numeric         |
| XArray   | CRDT array with UUID positions     | Any             |

### User-Defined Types

Types created via Definitions:

| TypeCode    | Description                    | Factory                          |
|-------------|--------------------------------|----------------------------------|
| Structure   | Named fields with types        | `Definitions::createStructure`   |
| Enumeration | Named cases                    | `Definitions::createEnumeration` |
| Concept     | Abstract entity with hierarchy | `Definitions::createConcept`     |
| Club        | Collection of Concepts         | `Definitions::createClub`        |

### Attachments

Attachments define key-document associations accessed via abstract interfaces
(`AttachmentGetting`, `AttachmentMutating`). Unlike types above, Attachment is not
a TypeCode but a first-class entity in Definitions:

| Component      | Description                                            |
|----------------|--------------------------------------------------------|
| `keyType`      | TypeConcept, TypeClub, or TypeAnyConcept               |
| `documentType` | Type of the document (often Structure)                 |
| `runtimeId`    | UUID for cross-language compatibility                  |
| `typeKey`      | Derived: `TypeKey::make(keyType)` (created internally) |

```cpp
auto attachment = defs->createAttachment(
    nameSpace,
    "CameraAttachment",   // name
    cameraConceptType,    // keyType
    cameraDocumentType,   // documentType
    "Camera storage"      // documentation
);
```

---

## RuntimeId: Cross-Language Compatibility

`RuntimeId` (stored as `runtimeId` in the `Type` class) is a UUID computed by
deterministic hash (MD5) of the type structure. It guarantees that the same type
definition produces the same identifier in C++ and Python.

The `runtimeId` is a public const member of `Type`:

```cpp
auto type = TypeVector::make(TypeDouble::Instance());
type->runtimeId;  // UUID computed from type structure
```

### Why RuntimeId Matters

| Use Case            | Explanation                                |
|---------------------|--------------------------------------------|
| **RPC**             | Verify type compatibility across network   |
| **Database**        | Match stored types with runtime types      |
| **Python binding**  | Ensure C++ and Python see same types       |
| **Code generation** | Detect type changes requiring regeneration |

---

## Type-Value Duality

For each `TypeX` exists a corresponding `ValueX`:

| Type            | Value            | Example                    |
|-----------------|------------------|----------------------------|
| TypeDouble      | ValueDouble      | `3.14`                     |
| TypeString      | ValueString      | `"hello"`                  |
| TypeVector      | ValueVector      | `[1, 2, 3]`                |
| TypeMap         | ValueMap         | `{"a": 1, "b": 2}`         |
| TypeStructure   | ValueStructure   | `{name: "Alice", age: 30}` |
| TypeEnumeration | ValueEnumeration | `Color.Red`                |
| TypeConcept     | ValueKey         | `Key<Camera>(uuid)`        |

### Every Value Knows Its Type

```cpp
auto value = ValueDouble::make(3.14);

value->type();              // -> TypeDouble::Instance()
value->type()->typeCode;    // -> TypeCode::Double (public member)
value->type()->runtimeId;   // -> consistent UUID (public member)
value->representation();    // -> "3.14"
```

---

## Type Interface

All types inherit from the `Type` base class:

```cpp
class Type {
public:
    TypeCode const typeCode;   // Public const member
    UUId const runtimeId;      // Public const member

    explicit Type(TypeCode code, UUId const & runtimeId);

    virtual std::string representation() const = 0;
    virtual std::string description() const = 0;

    template<typename T>
    bool equal(std::shared_ptr<T> const & other);

    template<typename T>
    Ordered compare(std::shared_ptr<T> const & other);
};
```

### Self-Description

Every type can describe itself:

```cpp
auto type = TypeVector::make(TypeDouble::Instance());

type->representation();  // "vector<double>"
type->description();     // "Vector of Double values"
```

---

## TypeChecker: Validation

`TypeChecker` validates type compatibility before operations:

```cpp
// Validate expected type
TypeChecker::check(value, expectedType);  // throws if mismatch

// Safe downcast pattern
auto doubleType = TypeDouble::cast(type);  // nullptr if not Double
```

### Error Messages

Type errors provide clear context:

```
[process@host]:Type:Unexpected:Type mismatch: expected Double, got String
```

---

## Definitions: Type Registry

`Definitions` is the central registry for user-defined types. It is the exclusive factory
for:

- `TypeStructure` - named fields
- `TypeEnumeration` - named cases
- `TypeConcept` - abstract entities
- `TypeClub` - concept collections
- `Attachment` - key-document associations

```cpp
auto defs = Definitions::make();

// Create a structure (via descriptor)
auto structDesc = TypeStructureDescriptor::make("Person");
structDesc->addField("name", TypeString::Instance());
structDesc->addField("age", TypeInt32::Instance());
auto personType = defs->createStructure(nameSpace, structDesc);

// Create a concept
auto cameraType = defs->createConcept(nameSpace, "Camera");

// Create an attachment (key-document association)
auto attachment = defs->createAttachment(
    nameSpace,
    "CameraAttachment",
    cameraType,          // keyType: TypeConcept (not TypeKey)
    cameraDocumentType,  // documentType
    "Camera storage"     // documentation
);
```

---

## See Also

- [Philosophy](viper_philosophy.md) - Metadata Everywhere principle
- [Value System](viper_value_system.md) - Type-Value duality in action
- [Architecture](viper_architecture.md) - Type System in layer model
- [Glossary](viper_glossary.md) - Type terminology
