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

```{js-summary}
Type
TypeName
```

## Primitive Types

```{js-summary}
TypeVoid
TypeBool
TypeUInt8
TypeUInt16
TypeUInt32
TypeUInt64
TypeInt8
TypeInt16
TypeInt32
TypeInt64
TypeFloat
TypeDouble
TypeString
TypeBlob
TypeBlobId
TypeCommitId
TypeUUId
```

## Container Types

```{js-summary}
TypeVector
TypeSet
TypeMap
TypeXArray
TypeOptional
```

## Algebraic Types

```{js-summary}
TypeTuple
TypeVec
TypeMat
TypeVariant
TypeAny
```

## User-Defined Types

```{js-summary}
TypeStructure
TypeStructureDescriptor
TypeStructureField
TypeEnumeration
TypeEnumerationCase
TypeEnumerationDescriptor
```

## Concept Types

```{js-summary}
TypeConcept
TypeClub
TypeKey
TypeAnyConcept
```

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
