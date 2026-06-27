# Types and Values

The Viper C++ type system provides strong typing with runtime validation. This
chapter covers how to create values from Node and how the type system surfaces
through the binding. The Python equivalent is {doc}`../dsviper/types_values`; the
type system is identical — only the idiom differs.

Examples assume the binding is in scope:

```js
const { Value, Type, ValueBool, ValueInt8, ValueInt32, ValueDouble,
        ValueString, ValueUUId, TypeVector } = require('@digitalsubstrate/dsviper');
```

## The universal constructor

Create any value with `Value.create(type, [initialValue])`:

```js
Value.create(Type.DOUBLE).encoded();              // 0.0
Value.create(Type.STRING, 'hello').encoded();     // 'hello'
Value.create(new TypeVector(Type.INT64), [1, 2, 3]).size();   // 3
```

If `initialValue` is omitted, the value is initialized to the type's "zero".
`encoded()` returns the underlying JavaScript native; `representation()` returns
the canonical string form.

## Choosing the right constructor

| Pattern                | When to use                  | Example |
|------------------------|------------------------------|---------|
| `Type.STRING`          | Primitive type constant      | `Value.create(Type.STRING, 'hello')` |
| `new TypeVector(...)`  | Parameterized container      | `Value.create(new TypeVector(Type.INT64), [1, 2, 3])` |
| `new ValueString(...)` | Direct value (known type)    | `new ValueString('hello')` |
| `Value.create(t, v)`   | Universal factory            | `Value.create(tStruct, { field: 1 })` |
| `Value.deduce(v)`      | Let Viper C++ infer the type | `Value.deduce(3.14)` |
| `ValueUUId.create()`   | Factory with generation      | `ValueUUId.create()` |

**Quick rules:**

- Use **`Type.X`** for primitives: `Type.STRING`, `Type.INT64`, `Type.BOOL`.
- Use **`new TypeX(...)`** for containers: `TypeVector`, `TypeMap`, `TypeOptional`.
- Use **`new ValueX(...)`** when the type is known and you want direct construction.
- Use **`Value.create(t, v)`** when working with dynamic types or DSM definitions.
- Use **`Value.deduce(v)`** for quick prototyping (type inferred from the native).

## Type constants

Common types are available as constants on `Type`:

| Constant                      | Type              |
|-------------------------------|-------------------|
| `Type.BOOL`                   | Boolean           |
| `Type.INT8` to `Type.INT64`   | Signed integers   |
| `Type.UINT8` to `Type.UINT64` | Unsigned integers |
| `Type.FLOAT`                  | 32-bit float      |
| `Type.DOUBLE`                 | 64-bit double     |
| `Type.STRING`                 | UTF-8 string      |
| `Type.UUID`                   | UUID              |
| `Type.ANY`                    | Any type          |

A type knows its own name and rendering:

```js
Type.DOUBLE.typeName().name();   // 'double'
Type.DOUBLE.description();       // 'double'
```

## Primitive types

### Boolean

Viper values render with their own representation — booleans are `true`/`false`:

```js
new ValueBool(false).representation();  // 'false'
new ValueBool(true).representation();   // 'true'
```

Type checking is enforced — a wrong native throws:

```js
try {
    new ValueBool(5);   // an integer is not a bool
} catch (e) {
    // a ViperError is thrown
}
```

### Integers

Signed and unsigned integers with range validation. `INT64`/`UINT64` round-trip
through `bigint`:

```js
Value.create(Type.INT8, 42).encoded();    // 42
Value.create(Type.INT64, 42n).encoded();  // 42n  (bigint)

try {
    new ValueInt8(128);   // out of range (INT8 max is 127)
} catch (e) {
    // a ViperError is thrown
}
```

Available types: `INT8`, `INT16`, `INT32`, `INT64`, `UINT8`, `UINT16`,
`UINT32`, `UINT64`.

### Floats

```js
new ValueDouble(3.14159).representation();   // '3.14159'
ValueDouble.ZERO.encoded();                  // 0.0
ValueDouble.tryParse('1.23e-4').encoded();   // 0.000123
ValueDouble.tryParse('not a number');        // undefined
```

`ValueDouble` follows IEEE 754 with Viper's total order: `NaN` equals `NaN`
(and hashes equally), and sorts before every other value.

### String

```js
Value.create(Type.STRING).encoded();              // ''
new ValueString('hello world').encoded();         // 'hello world'
```

### UUID

`ValueUUId.create()` generates a fresh UUID; pass a string to parse a known one:

```js
const u = ValueUUId.create();
u.representation();   // e.g. 'c98ddeec-0496-494c-b1e9-b470ff204be3'

ValueUUId.create('c98ddeec-0496-494c-b1e9-b470ff204be3');   // parsed

try {
    new ValueUUId('not-a-uuid');
} catch (e) {
    // a ViperError is thrown
}
```

## Type deduction

Let Viper infer the type from a native with `Value.deduce()`:

```js
const v = Value.deduce(3.14);
v instanceof ValueDouble;   // true
v.type().equals(Type.DOUBLE);   // true
```

## Type information

Every value knows its type:

```js
const v = new ValueDouble(1.618);
v.typeCode();         // 'double'
v.type().equals(Type.DOUBLE);   // true
v.description();      // contains both the value and 'double'
```

## Type checking and the seamless bridge

The bridge uses type metadata to validate and convert natives — there is
nothing to register. A value of the expected type is accepted; a cross-type
`cast` throws a `ViperError`:

```js
ValueDouble.cast(new ValueDouble(3.14));   // ok

try {
    ValueDouble.cast(new ValueInt32(42));   // wrong type
} catch (e) {
    e.name;   // 'ViperError'
}
```

## Value semantics

`equals`, `hash`, and `compare` are the value contract (see
{doc}`index` for the full Python ↔ Node mapping). They accept a native argument
directly:

```js
new ValueDouble(2).equals(2);          // true
new ValueDouble(1).compare(2) < 0;     // true
new ValueDouble(2).equals('foo');      // false  (incompatible → false, not a throw)
```

Remember that JavaScript `==` between two values is reference equality, not
value equality — reach for `.equals`.
