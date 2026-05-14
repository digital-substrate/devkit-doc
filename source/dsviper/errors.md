# Error Handling

Viper uses a single exception type for all errors: `ViperError`. This chapter explains how
to catch, interpret, and recover from errors in your Python code.

## The ViperError Exception

All Viper operations that fail raise a `ViperError` exception:

```python
from dsviper import ViperError, ValueInt8

try:
    v = ValueInt8(200)  # Out of range for int8
except ViperError as e:
    print(str(e))
```

Output:

```
[macbook@myapp]:Viper:Value:1:value is not in the range of 'int8'
```

The message follows the format: `[host@process]:Component:Domain:Code:Message`

### Parsing Error Details

To access individual error fields, use the `Error` class to parse the exception message:

```python
from dsviper import ViperError, Error, ValueInt8

try:
    v = ValueInt8(200)
except ViperError as e:
    error = Error.parse(str(e))
    if error:
        print(error.component())  # "Viper"
        print(error.domain())  # "Value"
        print(error.code())  # 1
        print(error.message())  # "value is not in the range of 'int8'"
        print(error.hostname())  # "macbook"
        print(error.process_name())  # "myapp"
```

### Error Class Methods

| Method                 | Return            | Description                                   |
|------------------------|-------------------|-----------------------------------------------|
| `Error.parse(str)`     | `Error` or `None` | Parse an error string into an Error object    |
| `error.component()`    | `str`             | The subsystem (e.g., "Viper", "Database")     |
| `error.domain()`       | `str`             | The functional domain (e.g., "Value", "Type") |
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

**Recovery**: Check your input types before calling Viper functions.

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

When accessing non-existent keys in databases, Viper does **not** raise an exception.
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

> **Note**: `ValueOptional` is a Viper container type, unrelated to Python's
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

## Best Practices

- Catch `ViperError` specifically rather than bare `Exception`.
- Check `is_nil()` before calling `unwrap()` on an optional.
- Check `report.has_error()` after `DSMBuilder.parse()` before using the
  returned definitions.
- Wrap multi-step transactions in `try/except/rollback`.

---

## Debugging Tips

### Enable Verbose Logging

Use Viper's logging system to trace operations:

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
