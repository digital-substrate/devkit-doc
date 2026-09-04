# Type System

The type system defines every type the Viper runtime understands. `Type` is the
base class: it exposes the primitive types as static accessors (`Type.INT64`,
`Type.STRING`, ...) and serves as the common supertype of the parameterized
container, algebraic, and user-defined types.

**When to use**: reach for types to describe schemas, to validate data, and to
build parameterized containers such as vectors and maps before instantiating
{doc}`values <values>` against them.

## Quick Start

```js
const { Type, TypeVector, TypeMap, TypeOptional } = require('@digitalsubstrate/dsviper');

// Primitive types are static accessors on Type
const tInt = Type.INT64;
const tStr = Type.STRING;
tStr.representation();                        // "string"

// Parameterized container types — construct with `new`
const tVec = new TypeVector(Type.STRING);    // vector<string>
const tMap = new TypeMap(Type.STRING, Type.INT64);
tMap.representation();                        // "map<string, int64>"

// Nested types compose freely
const tNested = new TypeMap(Type.STRING, new TypeVector(Type.FLOAT));

// Nullable type
const tOpt = new TypeOptional(Type.STRING);
tOpt.representation();                        // "optional<string>"
```

A type is the schema half of the runtime; pair it with `Value.create(type, native)`
to mint an instance (see {doc}`values`):

```js
const { Value, Type } = require('@digitalsubstrate/dsviper');

const v = Value.create(Type.STRING, 'hi');   // a ValueString
v.encoded();                                  // "hi"
```

## Choosing the Right Type

| Use Case | Type Class | Example |
|----------|------------|---------|
| Primitive value | `Type.STRING`, `Type.INT64` | static accessors |
| Homogeneous list | {js:class}`TypeVector` | `new TypeVector(Type.INT64)` |
| Key-value mapping | {js:class}`TypeMap` | `new TypeMap(Type.STRING, Type.INT64)` |
| Nullable value | {js:class}`TypeOptional` | `new TypeOptional(Type.STRING)` |
| Concurrent list | {js:class}`TypeXArray` | `new TypeXArray(Type.STRING)` |
| Fixed-size tuple | {js:class}`TypeTuple` | `new TypeTuple([Type.INT64, Type.STRING])` |

The mirror of this page for the Python binding is {doc}`../../dsviper-python/api/types`;
for a narrative walkthrough of types and values together, see
{doc}`../types_values`.

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Base Class

| Class | Description |
|-------|-------------|
| {js:class}`Type` | The primitive types, and the utilities that act on any type |
| {js:class}`TypeName` | Describes the name of a type: its namespace and its identifier |

## Primitive Types

| Class | Description |
|-------|-------------|
| {js:class}`TypeVoid` | The void type |
| {js:class}`TypeBool` | The bool type |
| {js:class}`TypeUInt8` | The uint8 type |
| {js:class}`TypeUInt16` | The uint16 type |
| {js:class}`TypeUInt32` | The uint32 type |
| {js:class}`TypeUInt64` | The uint64 type |
| {js:class}`TypeInt8` | The int8 type |
| {js:class}`TypeInt16` | The int16 type |
| {js:class}`TypeInt32` | The int32 type |
| {js:class}`TypeInt64` | The int64 type |
| {js:class}`TypeFloat` | The float type |
| {js:class}`TypeDouble` | The double type |
| {js:class}`TypeString` | The string type |
| {js:class}`TypeBlob` | The blob type |
| {js:class}`TypeBlobId` | The blob_id type |
| {js:class}`TypeCommitId` | The commit_id type |
| {js:class}`TypeUUId` | The uuid type |

## Container Types

| Class | Description |
|-------|-------------|
| {js:class}`TypeVector` | The vector<element_type> type |
| {js:class}`TypeSet` | The set<element_type> type |
| {js:class}`TypeMap` | The map<key_type, element_type> type |
| {js:class}`TypeXArray` | The xarray<element_type> type |
| {js:class}`TypeOptional` | The optional<element_type> type |

## Algebraic Types

| Class | Description |
|-------|-------------|
| {js:class}`TypeTuple` | The tuple<T0, ...> type |
| {js:class}`TypeVec` | The vec<numeric_type, size> type |
| {js:class}`TypeMat` | The mat<numeric_type, columns, rows> type |
| {js:class}`TypeVariant` | The variant<T0, ...> type |
| {js:class}`TypeAny` | The any type |

## User-Defined Types

| Class | Description |
|-------|-------------|
| {js:class}`TypeStructure` | A struct type |
| {js:class}`TypeStructureDescriptor` | Describes the fields a struct will be created with |
| {js:class}`TypeStructureField` | One field of a struct type |
| {js:class}`TypeEnumeration` | An enum type |
| {js:class}`TypeEnumerationCase` | One case of an enum type |
| {js:class}`TypeEnumerationDescriptor` | Describes the cases an enum will be created with |

## Concept Types

| Class | Description |
|-------|-------------|
| {js:class}`TypeConcept` | A concept type |
| {js:class}`TypeClub` | A club type |
| {js:class}`TypeKey` | The key<element_type> type |
| {js:class}`TypeAnyConcept` | The any_concept type |

## Reference

```{js:autoclass} Type
:members:
```

```{js:autoclass} TypeName
:members:
```

```{js:autoclass} TypeVoid
:members:
```

```{js:autoclass} TypeBool
:members:
```

```{js:autoclass} TypeUInt8
:members:
```

```{js:autoclass} TypeUInt16
:members:
```

```{js:autoclass} TypeUInt32
:members:
```

```{js:autoclass} TypeUInt64
:members:
```

```{js:autoclass} TypeInt8
:members:
```

```{js:autoclass} TypeInt16
:members:
```

```{js:autoclass} TypeInt32
:members:
```

```{js:autoclass} TypeInt64
:members:
```

```{js:autoclass} TypeFloat
:members:
```

```{js:autoclass} TypeDouble
:members:
```

```{js:autoclass} TypeString
:members:
```

```{js:autoclass} TypeBlob
:members:
```

```{js:autoclass} TypeBlobId
:members:
```

```{js:autoclass} TypeCommitId
:members:
```

```{js:autoclass} TypeUUId
:members:
```

```{js:autoclass} TypeVector
:members:
```

```{js:autoclass} TypeSet
:members:
```

```{js:autoclass} TypeMap
:members:
```

```{js:autoclass} TypeXArray
:members:
```
```{js:autoclass} TypeOptional
:members:
```

```{js:autoclass} TypeTuple
:members:
```

```{js:autoclass} TypeVec
:members:
```

```{js:autoclass} TypeMat
:members:
```

```{js:autoclass} TypeVariant
:members:
```

```{js:autoclass} TypeAny
:members:
```

```{js:autoclass} TypeStructure
:members:
```

```{js:autoclass} TypeStructureDescriptor
:members:
```

```{js:autoclass} TypeStructureField
:members:
```

```{js:autoclass} TypeEnumeration
:members:
```

```{js:autoclass} TypeEnumerationCase
:members:
```

```{js:autoclass} TypeEnumerationDescriptor
:members:
```

```{js:autoclass} TypeConcept
:members:
```

```{js:autoclass} TypeClub
:members:
```

```{js:autoclass} TypeKey
:members:
```

```{js:autoclass} TypeAnyConcept
:members:
```
