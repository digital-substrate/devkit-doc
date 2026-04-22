# Serialization

Viper provides multiple serialization formats for values and definitions. This
chapter covers JSON and binary encoding.

## JSON Encoding

### Encoding Values

Encode any value to JSON:

```pycon
>>> from dsviper import *

# Simple values
>>> v = Value.deduce([1, 2, 3])
>>> Value.json_encode(v)
'[1,2,3]'

# Complex values
>>> v = Value.deduce({(1, 2): "one", (3, 4): "two"})
>>> Value.json_encode(v)
'[[[1,2],"one"],[[3,4],"two"]]'
```

### Decoding Values

Decode JSON back to a value:

```pycon
>>> json_str = '[1,2,3]'
>>> t = TypeVector(Type.INT64)
>>> v = Value.json_decode(json_str, t, Definitions().const())
>>> v
[1, 2, 3]
```

### Pretty Printing

Format JSON with indentation:

```pycon
>>> v = Value.create(t_login, {"nickname": "alice", "password": "secret"})
>>> json_str = Value.json_encode(v, indent=2)
>>> print(json_str)
{
  "nickname": "alice",
  "password": "secret"
}
```

## DSM Definitions Serialization

### To JSON

```pycon
# Create definitions
>>> defs = Definitions()
>>> ns = NameSpace(ValueUUId("f529bc42-..."), "Tuto")
>>> defs.create_concept(ns, "User")

# Convert to DSM definitions
>>> dsm_defs = defs.const().to_dsm_definitions()

# Encode to JSON
>>> json_str = dsm_defs.json_encode(indent=2)
>>> print(json_str)
{
  "namespaces": [...],
  "concepts": [...],
  ...
}
```

### From JSON

```pycon
>>> dsm_defs = DSMDefinitions.json_decode(json_str)
```

### To DSM Language

```pycon
>>> print(dsm_defs.to_dsm())
namespace Tuto {f529bc42-...} {
    concept User;
};
```

## Binary Encoding

Binary encoding is compact and fast, used for persistence and network transfer.

### Encoding Values

```pycon
# Encode to binary (returns bytes)
>>> data = Value.binary_encode(value)

# Decode from binary
>>> value = Value.binary_decode(data, value_type, definitions)
```

### Encoding Definitions

```pycon
# Encode definitions to binary
>>> data = defs.binary_encode()

# Decode definitions from binary
>>> defs = Definitions.binary_decode(data)
```

## Stream Codec

For custom binary formats and RPC, Viper provides low-level stream codecs that
encode/decode primitive types directly.

### Available Codecs

| Codec                       | Description                      |
|-----------------------------|----------------------------------|
| `Codec.STREAM_BINARY`       | Compact binary, no type checking |
| `Codec.STREAM_TOKEN_BINARY` | Adds type tokens for validation  |

The token variant detects desynchronization early by prefixing each value with
its type.

### Encoding

```pycon
>>> from dsviper import *

# Create encoder
>>> encoder = Codec.STREAM_BINARY.create_encoder()

# Write primitives
>>> encoder.write_int64(42)
>>> encoder.write_float(3.14)
>>> encoder.write_string("hello")

# Finalize and get blob
>>> blob = encoder.end_encoding()
>>> blob
blob(21)
```

### Decoding

```pycon
# Create decoder from blob
>>> decoder = Codec.STREAM_BINARY.create_decoder(blob)

# Read in same order
>>> decoder.read_int64()
42
>>> decoder.read_float()
3.14
>>> decoder.read_string()
'hello'

# Check if more data
>>> decoder.has_more()
False
```

### Type Safety with Tokens

```pycon
>>> encoder = Codec.STREAM_TOKEN_BINARY.create_encoder()
>>> encoder.write_int64(42)
>>> blob = encoder.end_encoding()

>>> decoder = Codec.STREAM_TOKEN_BINARY.create_decoder(blob)
>>> decoder.read_bool()  # Wrong type!
ViperError: Expected token 'bool', got 'int64'.
```

### Computing Sizes

```pycon
>>> sizer = Codec.STREAM_BINARY.create_sizer()
>>> sizer.size_of_float()
4
>>> sizer.size_of_int64()
8
```

## Value Description

Get a descriptive string representation:

```pycon
>>> v = Value.deduce([1, 2, 3])
>>> v.description()
'[1, 2, 3]:vector<int64>'

>>> login = Value.create(t_login, {"nickname": "alice"})
>>> login.description()
"{nickname='alice':string, password='':string}:Tuto::Login"
```

## Binary File Format

DSM definitions can be saved in binary format (`.dsmb`):

```pycon
# Write definitions to binary file
>>> with open("model.dsmb", "wb") as f:
...     f.write(defs.binary_encode())

# Read definitions from binary file
>>> with open("model.dsmb", "rb") as f:
...     defs = Definitions.binary_decode(f.read())
```

## Common Patterns

### Round-Trip Test

Verify encoding/decoding preserves data:

```pycon
>>> original = Value.create(t_login, {"nickname": "test"})
>>> json_str = Value.json_encode(original)
>>> decoded = Value.json_decode(json_str, t_login, defs)
>>> original == decoded
True
```

### Schema Export

Export schema for external systems:

```pycon
>>> defs = db.definitions()
>>> dsm_defs = defs.to_dsm_definitions()
>>> print(dsm_defs.to_dsm())  # DSM language
>>> print(dsm_defs.json_encode(2))  # JSON schema
```

## Summary

| Format | Use Case              | API                          |
|--------|-----------------------|------------------------------|
| JSON   | Debugging, interop    | `Value.json_encode/decode`   |
| Binary | Persistence, RPC      | `Value.binary_encode/decode` |
| DSM    | Human-readable schema | `dsm_defs.to_dsm()`          |

## What's Next

- [DSM Processing](dsm.md) - Loading and introspecting DSM files
- [DSM Manual](../dsm/index.rst) - Data modeling language
- [Toolchain](../tools/index.rst) - Development tools
