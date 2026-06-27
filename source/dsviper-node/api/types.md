# Types

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

The mirror of this page for the Python binding is {doc}`../../dsviper/api/types`;
for a narrative walkthrough of types and values together, see
{doc}`../types_values`.

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`Type` | A utility class to handle type representation |
| {js:class}`TypeAny` | A class used to represent the any type |
| {js:class}`TypeAnyConcept` | A class used to represent the any_concept type |
| {js:class}`TypeBlob` | A class used to represent the blob type |
| {js:class}`TypeBlobId` | A class used to represent the blob_id type |
| {js:class}`TypeBool` | A class used to represent the bool type |
| {js:class}`TypeClub` | A class used to represent a club type |
| {js:class}`TypeCommitId` | A class used to represent the commit_id type |
| {js:class}`TypeConcept` | A class used to represent a concept type |
| {js:class}`TypeDouble` | A class used to represent the double type |
| {js:class}`TypeEnumeration` | A class used to represent an enum type |
| {js:class}`TypeEnumerationCase` | A class used to represent a case for an enum type |
| {js:class}`TypeEnumerationDescriptor` | A class used to describe the cases of an enum |
| {js:class}`TypeFloat` | A class used to represent the float type |
| {js:class}`TypeInt16` | A class used to represent the int16 type |
| {js:class}`TypeInt32` | A class used to represent the int32 type |
| {js:class}`TypeInt64` | A class used to represent the int64 type |
| {js:class}`TypeInt8` | A class used to represent the int8 type |
| {js:class}`TypeKey` | A class used to represent a key<element_type> type where element_type is a concept, club or any_concept |
| {js:class}`TypeMap` | A class used to represent a map<element_type> type |
| {js:class}`TypeMat` | A class used to represent a mat<numeric_type, columns, rows> type |
| {js:class}`TypeName` | A class used to describe the name of a type |
| {js:class}`TypeOptional` | A class used to represent an optional<element_type> type |
| {js:class}`TypeSet` | A class used to represent a set<element_type> type |
| {js:class}`TypeString` | A class used to represent the string type |
| {js:class}`TypeStructure` | A class used to represent a struct type |
| {js:class}`TypeStructureDescriptor` | A class used to describe the fields of a struct |
| {js:class}`TypeStructureField` | A class used to represent a field for a struct |
| {js:class}`TypeTuple` | A class used to represent a tuple<T0, ...> type |
| {js:class}`TypeUInt16` | A class used to represent the uint16 type |
| {js:class}`TypeUInt32` | A class used to represent the uint32 type |
| {js:class}`TypeUInt64` | A class used to represent the uint64 type |
| {js:class}`TypeUInt8` | A class used to represent the uint8 type |
| {js:class}`TypeUUId` | A class used to represent the uuid type |
| {js:class}`TypeVariant` | A class used to represent a variant<T0, ...> type |
| {js:class}`TypeVec` | A class used to represent a vec<element_type, size> type |
| {js:class}`TypeVector` | A class used to represent a vector<element_type> type |
| {js:class}`TypeVoid` | A class used to represent the void type |
| {js:class}`TypeXArray` | A class used to represent a xarray<element_type> type |

## Reference

```{js:autoclass} Type
:members:
```

```{js:autoclass} TypeAny
:members:
```

```{js:autoclass} TypeAnyConcept
:members:
```

```{js:autoclass} TypeBlob
:members:
```

```{js:autoclass} TypeBlobId
:members:
```

```{js:autoclass} TypeBool
:members:
```

```{js:autoclass} TypeClub
:members:
```

```{js:autoclass} TypeCommitId
:members:
```

```{js:autoclass} TypeConcept
:members:
```

```{js:autoclass} TypeDouble
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

```{js:autoclass} TypeFloat
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

```{js:autoclass} TypeInt8
:members:
```

```{js:autoclass} TypeKey
:members:
```

```{js:autoclass} TypeMap
:members:
```

```{js:autoclass} TypeMat
:members:
```

```{js:autoclass} TypeName
:members:
```

```{js:autoclass} TypeOptional
:members:
```

```{js:autoclass} TypeSet
:members:
```

```{js:autoclass} TypeString
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

```{js:autoclass} TypeTuple
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

```{js:autoclass} TypeUInt8
:members:
```

```{js:autoclass} TypeUUId
:members:
```

```{js:autoclass} TypeVariant
:members:
```

```{js:autoclass} TypeVec
:members:
```

```{js:autoclass} TypeVector
:members:
```

```{js:autoclass} TypeVoid
:members:
```

```{js:autoclass} TypeXArray
:members:
```
