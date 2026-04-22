# Types and Values

The Viper type system provides strong typing with runtime validation. This chapter covers
all available types and how to create values.

## The Universal Constructor

Create any value using `Value.create(type, [initial_value])`:

```pycon
>>> from dsviper import *

>>> Value.create(TypeFloat())
0.0

>>> Value.create(Type.STRING, "hello")
'hello'

>>> Value.create(TypeVector(Type.INT64), [1, 2, 3])
[1, 2, 3]
```

If `initial_value` is omitted, the value is initialized to the type's "zero".

## Choosing the Right Constructor

Viper offers multiple ways to create values. Use this guide to pick the right one:

| Pattern              | When to Use               | Example                                         |
|----------------------|---------------------------|-------------------------------------------------|
| `Type.STRING`        | Primitive type constant   | `Value.create(Type.STRING, "hello")`            |
| `TypeVector(...)`    | Parameterized container   | `Value.create(TypeVector(Type.INT64), [1,2,3])` |
| `ValueString("...")` | Direct value (known type) | `ValueString("hello")`                          |
| `Value.create(t, v)` | Universal factory         | `Value.create(t_struct, {"field": 1})`          |
| `Value.deduce(v)`    | Let Viper infer type      | `Value.deduce([1, 2, 3])`                       |
| `ValueUUId.create()` | Factory with generation   | `ValueUUId.create()`                            |

**Quick rules:**

- Use **Type.X** for primitives: `Type.STRING`, `Type.INT64`, `Type.BOOL`
- Use **TypeX(...)** for containers: `TypeVector(...)`, `TypeMap(...)`,
  `TypeOptional(...)`
- Use **ValueX(...)** when type is known and you want direct construction
- Use **Value.create(t, v)** when working with dynamic types or DSM definitions
- Use **Value.deduce(v)** for quick prototyping (type inferred from Python value)

## Type Constants

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

## Primitive Types

### Boolean

```pycon
>>> Value.create(Type.BOOL)
False

>>> Value.create(Type.BOOL, True)
True

# Type checking
>>> Value.create(Type.BOOL, 4)
ViperError: expected type 'bool', got 'int'
```

### Integers

Signed and unsigned integers with range validation:

```pycon
>>> Value.create(Type.INT8)
0

>>> Value.create(Type.INT8, 42)
42

>>> Value.create(Type.INT8, 256)  # Out of range
ViperError: value is not in the range of 'int8'
```

Available types: `INT8`, `INT16`, `INT32`, `INT64`, `UINT8`, `UINT16`, `UINT32`, `UINT64`

### Floats

```pycon
>>> Value.create(Type.FLOAT)
0.0

>>> Value.create(Type.FLOAT, 42)
42.0

>>> Value.create(Type.FLOAT, 1e300)  # Out of range
ViperError: value is not in the range of 'float'
```

### String

UTF-8 encoded strings:

```pycon
>>> Value.create(Type.STRING)
''

>>> Value.create(Type.STRING, "hello world")
'hello world'
```

### UUID

Create UUIDs with `ValueUUId.create()`:

```pycon
# Generate new UUID
>>> uuid = ValueUUId.create()
>>> uuid
'c98ddeec-0496-494c-b1e9-b470ff204be3'

# Parse UUID string
>>> uuid = ValueUUId.create("c98ddeec-0496-494c-b1e9-b470ff204be3")

# Invalid UUID
>>> ValueUUId.create("invalid")
ViperError: The literal 'invalid' is a malformed UUId.
```

## Mathematical Types

### Vec

Fixed-size numeric arrays:

```pycon
# vec<float, 3>
>>> t = TypeVec(Type.FLOAT, 3)
>>> Value.create(t)
(0.0, 0.0, 0.0)

>>> Value.create(t, (1, 2, 3))
(1.0, 2.0, 3.0)
```

### Mat

Matrices with columns and rows:

```pycon
# mat<float, 2, 3>
>>> t = TypeMat(Type.FLOAT, 2, 3)
>>> Value.create(t)
[(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

>>> Value.create(t, ((1, 2, 3), (4, 5, 6)))
[(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]
```

## Type Deduction

Let Python infer the Viper type with `Value.deduce()`:

```pycon
# List of integers → vector<int64>
>>> v = Value.deduce([1, 2, 3])
>>> v.type()
vector<int64>

# Complex nested structure
>>> v = Value.deduce([1, 2, (3, "string"), {1.0, 2.0}])
>>> v.type()
vector<int64 | set<double> | tuple<int64, string>>
```

## Type Information

Every value knows its type:

```pycon
>>> v = Value.create(TypeVector(Type.STRING), ["a", "b"])
>>> v.type()
vector<string>

>>> v.description()
"['a', 'b']:vector<string>"
```

## Type Checking

Viper validates types at runtime:

```pycon
>>> v = Value.create(TypeVector(Type.STRING))
>>> v.append("valid")
>>> v.append(123)  # Wrong type
ViperError: expected type 'str', got 'int'
```

## The Seamless Bridge

Python natives are automatically converted:

```pycon
# Python list accepted as input
>>> v = Value.create(TypeVector(Type.STRING))
>>> v.extend(["from", "python", "list"])
>>> v
['from', 'python', 'list']

# Python dict accepted for map
>>> m = Value.create(TypeMap(Type.STRING, Type.INT64), {"a": 1, "b": 2})
>>> m
{'a': 1, 'b': 2}
```

The bridge uses type metadata to validate and convert Python objects.

## What's Next

- [Collections](collections.md) - Vectors, Maps, Sets, and more
- [Structures and Enumerations](structures.md) - User-defined types
