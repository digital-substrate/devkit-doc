# Error Handling

Most Viper C++ failures raise one exception type, `ViperError`, carrying a structured message.
This chapter explains how to catch, interpret, and recover from errors in your Python code.

`ViperError` is not the only exception you will see. The binding raises the standard Python
exceptions where they are the right answer, and those are not `ViperError` subclasses:

| Call | Raises |
|------|--------|
| `DSMBuilder.assemble("/missing.dsm")` | `OSError` |
| `TypeVector("notatype")` | `RuntimeError` |
| `db.set(None, None, None)` | `TypeError` |

A file that is not there is the most likely failure of `assemble`, so a handler that names
`ViperError` alone will not see it. See {ref}`best-practices` below.

## The ViperError Exception

```python
from dsviper import ViperError, ValueInt8

try:
    v = ValueInt8(200)  # Out of range for int8
except ViperError as e:
    print(str(e))
```

Output:

```
[pid(20423)@mac.home]:P_Viper:P_ViperDecoderErrors:11:value is not in the range of 'int8' while decoding 'P_Viper_ValueInt8.tp_new.int8'.
```

The message follows the format: `[process@host]:Component:Domain:Code:Message` — the process
first, then the host.

### Parsing Error Details

To access individual error fields, use the `Error` class to parse the exception message:

```python
from dsviper import ViperError, Error, ValueInt8

try:
    v = ValueInt8(200)
except ViperError as e:
    error = Error.parse(str(e))
    if error:
        print(error.component())     # 'P_Viper'
        print(error.domain())        # 'P_ViperDecoderErrors'
        print(error.code())          # 11
        print(error.message())       # "value is not in the range of 'int8' while decoding ..."
        print(error.hostname())      # 'mac.home'
        print(error.process_name())  # 'pid(20423)'
```

`component()` is not a fixed subsystem name. It is `P_Viper` for a failure the binding itself
raises while decoding an argument, and the failing runtime class for one the C++ side raises:

| Call | `component()` | `domain()` |
|------|---------------|------------|
| `ValueInt8(200)` | `P_Viper` | `P_ViperDecoderErrors` |
| `ValueOptional(...).unwrap()` on an empty one | `Viper.ValueOptional` | `ContainerErrors` |
| `ValueInt64.cast(ValueString("x"))` | `Viper.ValueInt64` | `TypeErrors` |
| `Database.open("/missing.db")` | `Viper.DatabaseSQLite` | `DatabaseErrors` |

Match on `code()` within a known `domain()`, not on `component()` as a stable label.

### Error Class Methods

| Method                 | Return            | Description                                   |
|------------------------|-------------------|-----------------------------------------------|
| `Error.parse(str)`     | `Error` or `None` | Parse an error string into an Error object    |
| `error.component()`    | `str`             | Where it was raised (e.g. `P_Viper`, `Viper.ValueInt64`) |
| `error.domain()`       | `str`             | The error family (e.g. `TypeErrors`, `DatabaseErrors`) |
| `error.code()`         | `int`             | Numeric error code within the domain          |
| `error.message()`      | `str`             | Human-readable description                    |
| `error.hostname()`     | `str`             | Host where error originated                   |
| `error.process_name()` | `str`             | Process name                                  |
| `error.explained()`    | `str`             | Full formatted error string                   |

---

## Common Error Categories

### Type Mismatch Errors

These occur when you provide a value of the wrong type:

```python
from dsviper import Value, Type, TypeVector, ViperError

t_vec = TypeVector(Type.INT64)

try:
    # Trying to create a vector with strings instead of integers
    v = Value.create(t_vec, ["a", "b", "c"])
except ViperError as e:
    print(str(e))  # "...expected type 'long', got 'str'..."
```

**Recovery**: Check your input types before calling Viper C++ functions.

### Range Validation Errors

These occur when numeric values exceed their type's range:

```python
from dsviper import ValueInt8, ViperError

# Int8 range: -128 to 127
try:
    v = ValueInt8(200)
except ViperError as e:
    print(str(e))  # "...value is not in the range of 'int8'..."
```

Integer type ranges:

| Type     | Range             |
|----------|-------------------|
| `Int8`   | -128 to 127       |
| `Int16`  | -32,768 to 32,767 |
| `Int32`  | -2³¹ to 2³¹-1     |
| `Int64`  | -2⁶³ to 2⁶³-1     |
| `UInt8`  | 0 to 255          |
| `UInt16` | 0 to 65,535       |
| `UInt32` | 0 to 2³²-1        |
| `UInt64` | 0 to 2⁶⁴-1        |

**Recovery**: Validate numeric inputs before creating values, or use larger types.

### Optional Unwrap Errors

These occur when you try to unwrap an empty (nil) optional:

```python
from dsviper import Value, Type, TypeOptional, ValueOptional

t_opt = TypeOptional(Type.STRING)
v_empty = ValueOptional(t_opt)  # Creates nil optional

try:
    content = v_empty.unwrap()
except Exception as e:
    print("Cannot unwrap nil optional")
```

**Recovery**: Always check `is_nil()` before calling `unwrap()`:

```python
if not v_empty.is_nil():
    content = v_empty.unwrap()
else:
    content = "default value"
```

### Cast Errors

These occur when you cast a value to an incompatible type:

```python
from dsviper import ValueString, ValueInt64, ViperError

v_str = ValueString("hello")

try:
    v_int = ValueInt64.cast(v_str)
except ViperError as e:
    print(str(e))  # "...expected int64, got string [cast]..."
```

**Recovery**: Use `type()` to check the value's type before casting:

```python
from dsviper import Type

if v_str.type() == Type.INT64:
    v_int = ValueInt64.cast(v_str)
```

### Key Not Found (Not an Error)

When accessing non-existent keys in databases, Viper C++ does **not** raise an exception.
Instead, `get()` returns a `ValueOptional` that is nil:

```python
# db.get() returns ValueOptional, not the value directly
result = db.get(attachment, unknown_key)

# Check if key exists
if result.is_nil():
    print("Key not found")
else:
    value = result.unwrap()
```

> **Note**: `ValueOptional` is a Viper C++ container type, unrelated to Python's
> `typing.Optional`. It wraps a value with nil/non-nil semantics and provides
> `is_nil()`, `unwrap()`, and `wrap()` methods.

**Alternatives**: Use `has()` to check key existence before get:

```python
if db.has(attachment, key):
    value = db.get(attachment, key).unwrap()
```

### DSM Parse Errors

These occur when parsing invalid DSM files:

```python
from dsviper import DSMBuilder

builder = DSMBuilder.assemble("invalid.dsm")
report, dsm_defs, defs = builder.parse()

if report.has_error():
    for error in report.errors():
        print(f"Line {error.line()}: {error.message()}")
```

**Note**: DSM parsing returns a report object instead of raising exceptions, allowing you
to collect multiple errors at once.

---

(best-practices)=
## Best Practices

- Catch `ViperError` for a Viper failure, but do not assume it is the only one a call can
  raise. `DSMBuilder.assemble` raises `OSError` on a missing file, and the binding raises
  `TypeError` and `RuntimeError` on arguments it rejects before the C++ side sees them.
- Check `is_nil()` before calling `unwrap()` on an optional.
- Check `report.has_error()` after `DSMBuilder.parse()` before using the
  returned definitions.
- Wrap multi-step transactions in `try/except/rollback`.

---

## Debugging Tips

### Enable Verbose Logging

Use Viper C++'s logging system to trace operations:

```python
from dsviper import LoggerConsole, Logging

# Create a console logger with debug level
logger = LoggerConsole(Logging.LEVEL_DEBUG)
logging = logger.logging()

# Log operations
logging.info("Starting database operation")
logging.error("Operation failed")
```

Available log levels: `LEVEL_ALL`, `LEVEL_DEBUG`, `LEVEL_INFO`, `LEVEL_WARNING`,
`LEVEL_ERROR`, `LEVEL_CRITICAL`.

### Remote Errors

When using `DatabaseRemote` or `ServiceRemote`, errors include the remote host
information, helping you identify where the error occurred:

```
[remote-server@db-process]:Viper:Database:3:Connection timeout
```
