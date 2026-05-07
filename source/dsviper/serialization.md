# Serialization

Viper provides multiple serialization formats for values and definitions. This
chapter covers JSON and binary encoding.

## JSON Encoding

### Encoding Values

Encode any value to JSON:

```{doctest}
>>> from dsviper import *

>>> v = Value.deduce([1, 2, 3])
>>> Value.json_encode(v)
'[1,2,3]'
```

Complex values — Python tuples become JSON arrays:

```{doctest}
>>> v = Value.deduce({(1, 2): "one", (3, 4): "two"})
>>> Value.json_encode(v)
'[[[1,2],"one"],[[3,4],"two"]]'
```

### Decoding Values

Decode JSON back to a value:

```{doctest}
>>> json_str = '[1,2,3]'
>>> t = TypeVector(Type.INT64)
>>> v = Value.json_decode(json_str, t, Definitions().const())
>>> v
[1, 2, 3]
```

### Pretty Printing

Define a small `Login` structure to demonstrate pretty printing:

```{doctest}
>>> defs = Definitions()
>>> ns = NameSpace(ValueUUId("f529bc42-0618-4f54-a3fb-d55f95c5ad03"), "Tuto")
>>> desc = TypeStructureDescriptor("Login")
>>> desc.add_field("nickname", Type.STRING)
>>> desc.add_field("password", Type.STRING)
>>> t_login = defs.create_structure(ns, desc)
```

Format JSON with indentation:

```{doctest}
>>> v = Value.create(t_login, {"nickname": "alice", "password": "secret"})
>>> print(Value.json_encode(v, indent=2))
{
  "nickname": "alice",
  "password": "secret"
}
```

## DSM Definitions Serialization

### To JSON

Convert `Definitions` to a `DSMDefinitions` snapshot, then encode to JSON:

```{doctest}
>>> defs2 = Definitions()
>>> ns2 = NameSpace(ValueUUId("aaaaaaaa-0000-0000-0000-000000000001"), "Demo")
>>> defs2.create_concept(ns2, "User")
Demo::User

>>> dsm_defs = defs2.const().to_dsm_definitions()
>>> json_str = dsm_defs.json_encode(indent=2)
>>> "Demo" in json_str and "User" in json_str
True
```

The encoded JSON contains the standard DSM categories — namespaces,
concepts, structures, enumerations, attachments, clubs, function pools, and
attachment function pools.

### From JSON

```{doctest}
>>> restored = DSMDefinitions.json_decode(json_str)
>>> type(restored).__name__
'DSMDefinitions'
```

### To DSM Language

Render definitions back to DSM source:

```{doctest}
>>> print(dsm_defs.to_dsm())
namespace Demo {aaaaaaaa-0000-0000-0000-000000000001} {
<BLANKLINE>
concept User;
<BLANKLINE>
}; // ns Demo
<BLANKLINE>
```

## Binary Encoding

Binary encoding is compact and fast, used for persistence and network transfer.

### Encoding Values

`Value.encode(value)` returns a `ValueBlob`; `Value.decode(blob, type, defs)`
restores the value:

```{doctest}
>>> v = Value.deduce([1, 2, 3])
>>> blob = Value.encode(v)
>>> blob
blob(...)

>>> restored = Value.decode(blob, v.type(), Definitions().const())
>>> restored == v
True
```

### Encoding Definitions

`Definitions` are encoded via the const view:

```{doctest}
>>> blob = defs2.const().encode()
>>> blob
blob(...)

>>> restored = Definitions.decode(blob)
>>> type(restored).__name__
'Definitions'
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

Create an encoder, write primitives, finalize:

```{doctest}
>>> encoder = Codec.STREAM_BINARY.create_encoder()
>>> encoder.write_int64(42)
>>> encoder.write_float(3.14)
>>> encoder.write_string("hello")

>>> blob = encoder.end_encoding()
>>> blob
blob(...)
```

### Decoding

Read in the same order. Note that `write_float` / `read_float` round-trip
through 32-bit float, so `3.14` comes back with float32 precision:

```{doctest}
>>> decoder = Codec.STREAM_BINARY.create_decoder(blob)
>>> decoder.read_int64()
42
>>> decoder.read_float()
3.140000104904175
>>> decoder.read_string()
'hello'

>>> decoder.has_more()
False
```

### Type Safety with Tokens

The token codec rejects mismatched reads:

```{doctest}
>>> encoder = Codec.STREAM_TOKEN_BINARY.create_encoder()
>>> encoder.write_int64(42)
>>> blob = encoder.end_encoding()

>>> decoder = Codec.STREAM_TOKEN_BINARY.create_decoder(blob)
>>> decoder.read_bool()
Traceback (most recent call last):
    ...
dsviper.ViperError: ...Expected token bool, got int64...
```

### Computing Sizes

```{doctest}
>>> sizer = Codec.STREAM_BINARY.create_sizer()
>>> sizer.size_of_float()
4
>>> sizer.size_of_int64()
8
```

## Value Description

Get a descriptive string representation:

```{doctest}
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
...     f.write(defs.const().encode())

# Read definitions from binary file
>>> with open("model.dsmb", "rb") as f:
...     defs = Definitions.decode(f.read())
```

## Common Patterns

### Round-Trip Test

Verify encoding/decoding preserves data:

```{doctest}
>>> original = Value.create(t_login, {"nickname": "test"})
>>> json_str = Value.json_encode(original)
>>> decoded = Value.json_decode(json_str, t_login, defs.const())
>>> original == decoded
True
```

### Schema Export

Export schema for external systems:

```pycon
>>> defs = db.definitions()
>>> dsm_defs = defs.to_dsm_definitions()
>>> print(dsm_defs.to_dsm())          # DSM language
>>> print(dsm_defs.json_encode(indent=2))  # JSON schema
```

```{note}
The `Schema Export` snippet above pulls definitions from a live `db` and
therefore requires a working database. See [Database](database.md) for a
full walkthrough.
```

## Summary

| Format | Use Case              | API                            |
|--------|-----------------------|--------------------------------|
| JSON   | Debugging, interop    | `Value.json_encode/decode`     |
| Binary | Persistence, RPC      | `Value.encode/decode`          |
| DSM    | Human-readable schema | `dsm_defs.to_dsm()`            |

## What's Next

- [DSM Processing](dsm.md) - Loading and introspecting DSM files
- [DSM Manual](../dsm/index.rst) - Data modeling language
- [dsviper-tools](../dsviper-tools/index.rst) - Development tools
