# Values

Values are instances of types. Every value carries its {js:class}`Type` and obeys
the Java-like `equals` / `hash` / `compare` contract. {js:class}`Value` is the base
class, exposing factory methods for creating and converting values; each concrete
class (`ValueString`, `ValueInt64`, ...) is constructible directly.

**When to use**: use values to hold typed data. Primitives are immutable; containers
(`ValueVector`, `ValueMap`, `ValueSet`, `ValueXArray`) are mutable. INT64/UINT64
values encode to native `bigint`; every other integer and float encodes to `number`.

For the conceptual guide see {doc}`../types_values`; for the type system see
{doc}`types`. The Python equivalent is {doc}`../../dsviper-python/api/values`.

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

## Base Class

| Class | Description |
|-------|-------------|
| {js:class}`Value` | Creates values, and converts between them and native JS values |

## Primitive Values

| Class | Description |
|-------|-------------|
| {js:class}`ValueVoid` | A value of type void |
| {js:class}`ValueBool` | A value of type bool |
| {js:class}`ValueUInt8` | A value of type uint8 |
| {js:class}`ValueUInt16` | A value of type uint16 |
| {js:class}`ValueUInt32` | A value of type uint32 |
| {js:class}`ValueUInt64` | A value of type uint64 |
| {js:class}`ValueInt8` | A value of type int8 |
| {js:class}`ValueInt16` | A value of type int16 |
| {js:class}`ValueInt32` | A value of type int32 |
| {js:class}`ValueInt64` | A value of type int64 |
| {js:class}`ValueFloat` | A value of type float |
| {js:class}`ValueDouble` | A value of type double |
| {js:class}`ValueString` | A value of type string |
| {js:class}`ValueBlob` | A value of type blob |
| {js:class}`ValueBlobId` | A value of type blob_id |
| {js:class}`ValueCommitId` | A value of type commit_id |
| {js:class}`ValueUUId` | A value of type uuid |

## Container Values

| Class | Description |
|-------|-------------|
| {js:class}`ValueVector` | A value of type vector<element_type> |
| {js:class}`ValueVectorIter` | Iterator for ValueVector elements |
| {js:class}`ValueSet` | A value of type set<element_type> |
| {js:class}`ValueSetIter` | Iterator for ValueSet elements |
| {js:class}`ValueMap` | A value of type map<key_type, element_type> |
| {js:class}`ValueXArray` | A value of type xarray<element_type> |
| {js:class}`ValueOptional` | A value of type optional<element_type> |

## Algebraic Values

| Class | Description |
|-------|-------------|
| {js:class}`ValueTuple` | A value of type tuple<T0, ...> |
| {js:class}`ValueTupleIter` | Iterator for ValueTuple elements |
| {js:class}`ValueVec` | A value of type vec<numeric_type, size> |
| {js:class}`ValueMat` | A value of type mat<numeric_type, columns, rows> |
| {js:class}`ValueVariant` | A value of type variant<T0, ...> |
| {js:class}`ValueAny` | A value of any type |

## User-Defined Values

| Class | Description |
|-------|-------------|
| {js:class}`ValueStructure` | A value of type struct |
| {js:class}`ValueEnumeration` | A value of type enum |
| {js:class}`ValueKey` | A value of type key<element_type> |

## Value Program

| Class | Description |
|-------|-------------|
| {js:class}`ValueProgram` | The sequence of opcodes a commit carries |
| {js:class}`ValueOpcodeKey` | What an opcode applies to: an attachment, an instance, and that instance's concept |
| {js:class}`ValueOpcode` | The base of the opcode hierarchy |
| {js:class}`ValueOpcodeDocumentSet` | Writes a whole document at a key — the only opcode without a path |
| {js:class}`ValueOpcodeDocumentUpdate` | Writes a value at a path inside a document |
| {js:class}`ValueOpcodeMapUnion` | Adds entries to the map at a path, replacing the keys already there |
| {js:class}`ValueOpcodeMapSubtract` | Removes from the map at a path the entries whose key it carries |
| {js:class}`ValueOpcodeMapUpdate` | Writes entries over the keys the map at a path already holds, inserting none |
| {js:class}`ValueOpcodeSetUnion` | Adds elements to the set at a path |
| {js:class}`ValueOpcodeSetSubtract` | Removes elements from the set at a path |
| {js:class}`ValueOpcodeXArrayInsert` | Inserts a position into the xarray at a path, before another one |
| {js:class}`ValueOpcodeXArrayRemove` | Removes a position from the xarray at a path |
| {js:class}`ValueOpcodeXArrayUpdate` | Writes a value at a position of the xarray at a path |
| {js:class}`ValueProcessorTrace` | The execution of one program: whether it ran, and the opcodes it applied |
| {js:class}`ValueProcessorTraceOpcode` | One step of a traced execution: the opcode, and the exception it raised if it did |

## Reference

```{js:autoclass} Value
:members:
```

```{js:autoclass} ValueVoid
:members:
```

```{js:autoclass} ValueBool
:members:
```

```{js:autoclass} ValueUInt8
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

```{js:autoclass} ValueInt8
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

```{js:autoclass} ValueFloat
:members:
```

```{js:autoclass} ValueDouble
:members:
```

```{js:autoclass} ValueString
:members:
```

```{js:autoclass} ValueBlob
:members:
```

```{js:autoclass} ValueBlobId
:members:
```

```{js:autoclass} ValueCommitId
:members:
```

```{js:autoclass} ValueUUId
:members:
```

```{js:autoclass} ValueVector
:members:
```

```{js:autoclass} ValueVectorIter
:members:
```

```{js:autoclass} ValueSet
:members:
```

```{js:autoclass} ValueSetIter
:members:
```

```{js:autoclass} ValueMap
:members:
```

```{js:autoclass} ValueXArray
:members:
```
```{js:autoclass} ValueOptional
:members:
```

```{js:autoclass} ValueTuple
:members:
```

```{js:autoclass} ValueTupleIter
:members:
```

```{js:autoclass} ValueVec
:members:
```

```{js:autoclass} ValueMat
:members:
```

```{js:autoclass} ValueVariant
:members:
```

```{js:autoclass} ValueAny
:members:
```

```{js:autoclass} ValueStructure
:members:
```

```{js:autoclass} ValueEnumeration
:members:
```

```{js:autoclass} ValueKey
:members:
```

```{js:autoclass} ValueProgram
:members:
```

```{js:autoclass} ValueOpcodeKey
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

```{js:autoclass} ValueOpcodeMapUnion
:members:
```

```{js:autoclass} ValueOpcodeMapSubtract
:members:
```

```{js:autoclass} ValueOpcodeMapUpdate
:members:
```

```{js:autoclass} ValueOpcodeSetUnion
:members:
```

```{js:autoclass} ValueOpcodeSetSubtract
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

```{js:autoclass} ValueProcessorTrace
:members:
```

```{js:autoclass} ValueProcessorTraceOpcode
:members:
```
