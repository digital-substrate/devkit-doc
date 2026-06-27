# Values

Values are instances of types. Every value carries its {js:class}`Type` and obeys
the Java-like `equals` / `hash` / `compare` contract. {js:class}`Value` is the base
class, exposing factory methods for creating and converting values; each concrete
class (`ValueString`, `ValueInt64`, ...) is constructible directly.

**When to use**: use values to hold typed data. Primitives are immutable; containers
(`ValueVector`, `ValueMap`, `ValueSet`, `ValueXArray`) are mutable. INT64/UINT64
values encode to native `bigint`; every other integer and float encodes to `number`.

For the conceptual guide see {doc}`../types_values`; for the type system see
{doc}`types`. The Python equivalent is {doc}`../../dsviper/api/values`.

## Quick Start

```js
const { Value, Type, ValueString, ValueInt64, ValueDouble } = require('@digitalsubstrate/dsviper');

// Direct construction for primitives
const name = new ValueString('Alice');
const count = new ValueInt64(42n);          // INT64 ↔ bigint

// Factory with an explicit type (no native arg defaults the value)
const score = Value.create(Type.DOUBLE, 3.14);
const zero = Value.create(Type.INT64);      // 0n

// Infer the value class from a JS scalar
const flag = Value.deduce(true);            // ValueDouble / ValueString / ValueBool ...

// Access the underlying JS value, its text form, and its type
name.encoded();                             // 'Alice'
score.representation();                     // '3.14'
name.type().equals(Type.STRING);            // true

// equals/compare accept native arguments (never use == between values)
count.equals(42n);                          // true
new ValueDouble(1).compare(2) < 0;          // true

// Parse from text — returns undefined on failure (not a throw)
ValueInt64.tryParse('42').encoded();        // 42n
ValueInt64.tryParse('not a number');        // undefined

// cast re-types a Value, throwing a ViperError on mismatch
ValueDouble.cast(score).encoded();          // 3.14

// Per-type singletons
ValueInt64.ZERO.encoded();                  // 0n
ValueDouble.ONE.encoded();                  // 1.0
```

## Choosing the Right Pattern

| Pattern | When to use | Example |
|---------|-------------|---------|
| `new ValueString(...)` | Direct primitive construction | `new ValueInt64(42n)` |
| `Value.create(type[, native])` | Generic factory with an explicit type | `Value.create(Type.DOUBLE, 3.14)` |
| `Value.deduce(scalar)` | Infer the value class from a JS scalar | `Value.deduce(true)` |
| `Value.decode(bytes, type, defs)` | Deserialize from the binary stream codec | `Value.decode(buf, Type.STRING, defs)` |
| `ValueXxx.tryParse(text)` | Parse from text, `undefined` on failure | `ValueInt64.tryParse('42')` |
| `ValueXxx.cast(value)` | Re-type a value, `ViperError` on mismatch | `ValueInt64.cast(v)` |

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`Value` | A utility class to handle value instantiation and representation |
| {js:class}`ValueAny` | A class used to represent a value of any type |
| {js:class}`ValueBlob` | A class used to represent a value of type blob |
| {js:class}`ValueBlobId` | A class used to represent a value of type blob_id |
| {js:class}`ValueBool` | A class used to represent a value of type bool |
| {js:class}`ValueCommitId` | A class used to represent a value of type commit_id |
| {js:class}`ValueDouble` | A class used to represent a value of type double |
| {js:class}`ValueEnumeration` | A class used to represent a value of type struct |
| {js:class}`ValueFloat` | A class used to represent a value of type float |
| {js:class}`ValueInt16` | A class used to represent a value of type int16 |
| {js:class}`ValueInt32` | A class used to represent a value of type int32 |
| {js:class}`ValueInt64` | A class used to represent a value of type int64 |
| {js:class}`ValueInt8` | A class used to represent a value of type int8 |
| {js:class}`ValueKey` | A class used to represent a value of type key<element_type> |
| {js:class}`ValueMap` | A class used to represent a value of type map<key_type, element_type> |
| {js:class}`ValueMat` | A class used to represent a value of type mat<element_type, columns, rows> |
| {js:class}`ValueOpcode` | A utility class to handle opcodes encoder and streamer |
| {js:class}`ValueOpcodeDocumentSet` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOpcodeDocumentUpdate` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOpcodeKey` | A class used to retrieve the mutation opcodes for an instance of a concept for an attachment |
| {js:class}`ValueOpcodeMapSubtract` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOpcodeMapUnion` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOpcodeMapUpdate` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOpcodeSetSubtract` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOpcodeSetUnion` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOpcodeXArrayInsert` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOpcodeXArrayRemove` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOpcodeXArrayUpdate` | A class used to represent the type and the arguments of an opcode |
| {js:class}`ValueOptional` | A class used to represent a value of type optional<element_type> |
| {js:class}`ValueProcessorTrace` | A class used to represent traced opcode |
| {js:class}`ValueProcessorTraceOpcode` | A class used to represent a traced opcode |
| {js:class}`ValueProgram` | A class used to retrieve opcodes |
| {js:class}`ValueSet` | A class used to represent a value of type set<element_type> |
| {js:class}`ValueSetIter` | Iterator for ValueSet elements |
| {js:class}`ValueString` | A class used to represent a value of type string |
| {js:class}`ValueStructure` | A class used to represent a value of type struct |
| {js:class}`ValueTuple` | A class used to represent a value of type tuple<T0, ...> |
| {js:class}`ValueTupleIter` | Iterator for ValueTuple elements |
| {js:class}`ValueUInt16` | A class used to represent a value of type uint16 |
| {js:class}`ValueUInt32` | A class used to represent a value of type uint32 |
| {js:class}`ValueUInt64` | A class used to represent a value of type uint64 |
| {js:class}`ValueUInt8` | A class used to represent a value of type uint8 |
| {js:class}`ValueUUId` | A class used to represent a value of type uuid |
| {js:class}`ValueVariant` | ValueVariant(type_variant, initial_value) |
| {js:class}`ValueVec` | ValueVec(type_vec [, initial_value]) |
| {js:class}`ValueVector` | A class used to represent a value of type vector<element_type> |
| {js:class}`ValueVectorIter` | Iterator for ValueVector elements |
| {js:class}`ValueVoid` | A class used to represent a value of type void |
| {js:class}`ValueXArray` | A class used to represent a value of type xarray<element_type> |

## Reference

```{js:autoclass} Value
:members:
```

```{js:autoclass} ValueAny
:members:
```

```{js:autoclass} ValueBlob
:members:
```

```{js:autoclass} ValueBlobId
:members:
```

```{js:autoclass} ValueBool
:members:
```

```{js:autoclass} ValueCommitId
:members:
```

```{js:autoclass} ValueDouble
:members:
```

```{js:autoclass} ValueEnumeration
:members:
```

```{js:autoclass} ValueFloat
:members:
```

```{js:autoclass} ValueInt16
:members:
```

```{js:autoclass} ValueInt32
:members:
```

```{js:autoclass} ValueInt64
:members:
```

```{js:autoclass} ValueInt8
:members:
```

```{js:autoclass} ValueKey
:members:
```

```{js:autoclass} ValueMap
:members:
```

```{js:autoclass} ValueMat
:members:
```

```{js:autoclass} ValueOpcode
:members:
```

```{js:autoclass} ValueOpcodeDocumentSet
:members:
```

```{js:autoclass} ValueOpcodeDocumentUpdate
:members:
```

```{js:autoclass} ValueOpcodeKey
:members:
```

```{js:autoclass} ValueOpcodeMapSubtract
:members:
```

```{js:autoclass} ValueOpcodeMapUnion
:members:
```

```{js:autoclass} ValueOpcodeMapUpdate
:members:
```

```{js:autoclass} ValueOpcodeSetSubtract
:members:
```

```{js:autoclass} ValueOpcodeSetUnion
:members:
```

```{js:autoclass} ValueOpcodeXArrayInsert
:members:
```

```{js:autoclass} ValueOpcodeXArrayRemove
:members:
```

```{js:autoclass} ValueOpcodeXArrayUpdate
:members:
```

```{js:autoclass} ValueOptional
:members:
```

```{js:autoclass} ValueProcessorTrace
:members:
```

```{js:autoclass} ValueProcessorTraceOpcode
:members:
```

```{js:autoclass} ValueProgram
:members:
```

```{js:autoclass} ValueSet
:members:
```

```{js:autoclass} ValueSetIter
:members:
```

```{js:autoclass} ValueString
:members:
```

```{js:autoclass} ValueStructure
:members:
```

```{js:autoclass} ValueTuple
:members:
```

```{js:autoclass} ValueTupleIter
:members:
```

```{js:autoclass} ValueUInt16
:members:
```

```{js:autoclass} ValueUInt32
:members:
```

```{js:autoclass} ValueUInt64
:members:
```

```{js:autoclass} ValueUInt8
:members:
```

```{js:autoclass} ValueUUId
:members:
```

```{js:autoclass} ValueVariant
:members:
```

```{js:autoclass} ValueVec
:members:
```

```{js:autoclass} ValueVector
:members:
```

```{js:autoclass} ValueVectorIter
:members:
```

```{js:autoclass} ValueVoid
:members:
```

```{js:autoclass} ValueXArray
:members:
```
