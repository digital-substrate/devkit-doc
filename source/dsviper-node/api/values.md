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

```{js-summary}
Value
```

## Primitive Values

```{js-summary}
ValueVoid
ValueBool
ValueUInt8
ValueUInt16
ValueUInt32
ValueUInt64
ValueInt8
ValueInt16
ValueInt32
ValueInt64
ValueFloat
ValueDouble
ValueString
ValueBlob
ValueBlobId
ValueCommitId
ValueUUId
```

## Container Values

```{js-summary}
ValueVector
ValueVectorIter
ValueSet
ValueSetIter
ValueMap
ValueXArray
ValueOptional
```

## Algebraic Values

```{js-summary}
ValueTuple
ValueTupleIter
ValueVec
ValueMat
ValueVariant
ValueAny
```

## User-Defined Values

```{js-summary}
ValueStructure
ValueEnumeration
ValueKey
```

## Value Program

```{js-summary}
ValueProgram
ValueOpcodeKey
ValueOpcode
ValueOpcodeDocumentSet
ValueOpcodeDocumentUpdate
ValueOpcodeMapUnion
ValueOpcodeMapSubtract
ValueOpcodeMapUpdate
ValueOpcodeSetUnion
ValueOpcodeSetSubtract
ValueOpcodeXArrayInsert
ValueOpcodeXArrayRemove
ValueOpcodeXArrayUpdate
ValueProcessorTrace
ValueProcessorTraceOpcode
```

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
