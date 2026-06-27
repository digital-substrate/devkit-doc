# Serialization

The runtime offers several ways to turn a `Value` into bytes (or text) and
back: JSON, a compact binary stream codec, and a native JS bridge
(`dumps`/`loads`). DSM definitions have their own JSON and binary codecs. This
is the Node twin of the Python {doc}`../dsviper/serialization` page.

Every form is type-driven on the way back: a decode needs both the target
`Type` and a definitions snapshot. Build a frozen, empty snapshot with:

```js
const { Definitions } = require('@digitalsubstrate/dsviper');

const defs = new Definitions().const();   // a DefinitionsConst — the schema universe
```

Round-trips preserve **value**, not identity. `Value` handles have Java-like
semantics: compare with `.equals(...)`, never `==` (which is reference
equality between handles). So a clean round-trip reads:

```js
v.equals(Value.decode(Value.encode(v), type, defs));   // true
```

## JSON

### Encoding values

`Value.jsonEncode(value)` returns a JSON string.

### Decoding values

`Value.jsonDecode(string, type, defs)` reconstructs the value. The type tells
the decoder how to read the document, so a JSON round-trip reads:

```js
const { Value, Type, TypeVector, ValueVector, Definitions } = require('@digitalsubstrate/dsviper');

const defs = new Definitions().const();
const t = new TypeVector(Type.INT64);
const v = new ValueVector(t, [1n, 2n, 3n]);

v.equals(Value.jsonDecode(Value.jsonEncode(v), t, defs));   // true
```

## Binary stream codec

The binary codec is compact and fast — the format used for persistence and
network transfer. `Value.encode(value)` returns a `ValueBlob`;
`Value.decode(blob, type, defs)` restores the value.

```js
const { Value, Type, TypeVector, ValueVector, Definitions } = require('@digitalsubstrate/dsviper');

const defs = new Definitions().const();
const t = new TypeVector(Type.INT64);
const v = new ValueVector(t, [1n, 2n, 3n]);

const blob = Value.encode(v);              // a ValueBlob
const restored = Value.decode(blob, t, defs);
restored.equals(v);                        // true
```

The codec covers the whole value catalogue — scalars, containers, wrappers —
including IEEE-754 edge cases. A `NaN` double survives intact (Viper gives
`NaN` singleton semantics, so it compares equal to itself):

```js
const { ValueDouble } = require('@digitalsubstrate/dsviper');

const nan = new ValueDouble(NaN);
nan.equals(Value.decode(Value.encode(nan), Type.DOUBLE, defs));   // true
```

## Native bridge (dumps / loads)

`Value.dumps(value)` projects a value to a native JS shape; `Value.loads(native,
type, defs)` reads it back. Use this to hand a value to JS-native code (logging,
a `JSON.stringify` boundary, an IPC payload) and reconstruct it later.

```js
const native = Value.dumps(v);             // a native JS representation
const back = Value.loads(native, t, defs);
back.equals(v);                            // true
```

## Stream encoder / decoder

For custom wire formats and RPC, the runtime exposes a low-level codec that
writes and reads primitives one at a time. Resolve a codec by name with
`Codec.check(name)`, or use the bound instances directly:

| Codec                       | Description                       |
|-----------------------------|-----------------------------------|
| `Codec.STREAM_BINARY`       | Length-prefixed binary stream     |
| `Codec.STREAM_TOKEN_BINARY` | Adds a type token per value        |
| `Codec.STREAM_RAW`          | Fixed-width raw stream            |

The token variant prefixes every value with its type, catching a
read/write desynchronization early.

### Encoding

Create an encoder, write in order, finalize with `endEncoding()` (yields a
`ValueBlob`):

```js
const { Codec } = require('@digitalsubstrate/dsviper');

const encoder = Codec.STREAM_BINARY.createEncoder();
encoder.writeBool(true);
encoder.writeUint32(42);
encoder.writeString('hello');
encoder.writeDouble(3.14);

const blob = encoder.endEncoding();
encoder.isEnded();                         // true
blob.size() > 0;                           // true
```

### Decoding

Read back in the **same order**. The decoder tracks its position; `offset()`
advances, `hasMore()` reports remaining data, and `rewind()` returns to the
start:

```js
const decoder = Codec.STREAM_BINARY.createDecoder(blob);
decoder.readBool();                        // true
decoder.readUint32();                       // 42
decoder.readString();                       // 'hello'
decoder.readDouble();                       // 3.14 (double precision)
decoder.hasMore();                          // false
```

```{note}
64-bit integers cross the boundary as JS `bigint`: write `42n` with
`writeInt64` / `writeUint64`, read it back with `readInt64` / `readUint64`.
The `writeFloat` / `readFloat` pair round-trips through 32-bit precision, so a
value like `3.14159` returns slightly rounded; `writeDouble` / `readDouble`
keep full double precision.
```

Arrays of primitives travel as native JS arrays. Pass the element count to both
the write and the read:

```js
const e = Codec.STREAM_BINARY.createEncoder();
e.writeUint32s([1000, 2000, 3000], 3);
const data = e.endEncoding();

const d = Codec.STREAM_BINARY.createDecoder(data);
d.readUint32s(3);                          // [1000, 2000, 3000]
```

### Type safety with tokens

`Codec.STREAM_TOKEN_BINARY` validates each read against the token written. A
mismatched read raises — the error is a JS `Error` whose `.name` is
`'ViperError'`:

```js
const e = Codec.STREAM_TOKEN_BINARY.createEncoder();
e.writeDouble(3.14);
const tokenBlob = e.endEncoding();

const d = Codec.STREAM_TOKEN_BINARY.createDecoder(tokenBlob);
try {
  d.readBool();                            // wrong type for the next token
} catch (err) {
  err.name;                                // 'ViperError'
}
```

### Computing sizes

A sizer reports the encoded width of each primitive without writing anything:

```js
const sizer = Codec.STREAM_BINARY.createSizer();
sizer.sizeOfInt64();                       // 8
sizer.sizeOfFloat();                       // 4
```

## DSM definitions

A parsed `DSMDefinitions` snapshot serializes through its own codecs. JSON
(`.dsm.json`) is the canonical on-disk form consumed by Kibo and the toolchain;
binary is the compact alternative. Both round-trips are stable.

```js
const { DSMBuilder, DSMDefinitions } = require('@digitalsubstrate/dsviper');

const [report, dsm] = DSMBuilder.assemble('model.dsm').parse();
if (report.hasError()) throw new Error('parse failed');

// JSON
const json = dsm.jsonEncode();
const fromJson = DSMDefinitions.jsonDecode(json);
DSMDefinitions.jsonDecode(json).jsonEncode() === json;   // true (stable)

// Binary
const blob = dsm.encode();                 // a ValueBlob
const fromBinary = DSMDefinitions.decode(blob);
```

The JSON encoding carries every DSM category — namespaces, concepts,
structures, enumerations, attachments, clubs, function pools, and attachment
function pools — so the decoded snapshot matches the source category by
category. The two codecs also agree: a binary round-trip re-encoded as JSON is
byte-identical to encoding the source straight to JSON.

### Rendering back to DSM source

`toDsm(...)` renders a snapshot back to DSM language. The booleans are
positional — `toDsm(showDocumentation, showRuntimeId, html)`:

```js
const source = dsm.toDsm();                // plain DSM text
const withRuntimeIds = dsm.toDsm(true, true, false);
```

See {doc}`dsm` for working with definitions from DSM, and
{doc}`database` for sealing them into a database.

## Value description

`description()` gives a human-readable rendering of a value with its type — handy
for logging and debugging, not a serialization format:

```js
const v = new ValueSet(new TypeSet(Type.INT64), [1n, 2n, 3n]);
const d = v.description();                  // a string carrying the values and the type
d.includes('set<int64>');                   // true
```

## Common patterns

### Round-trip test

A quick way to confirm encode/decode preserves a value across any codec — using
the {doc}`types_values` `Fuzzer` to generate a random value of a given type:

```js
const { Value, Type, Definitions, Fuzzer } = require('@digitalsubstrate/dsviper');

const defs = new Definitions().const();
const fuzzer = new Fuzzer(defs);
const v = fuzzer.fuzz(Type.DOUBLE);

// All three codecs round-trip the same value.
v.equals(Value.decode(Value.encode(v), Type.DOUBLE, defs));            // binary
v.equals(Value.jsonDecode(Value.jsonEncode(v), Type.DOUBLE, defs));    // JSON
v.equals(Value.loads(Value.dumps(v), Type.DOUBLE, defs));              // native
```

### Schema export

Render a database's definitions for an external system — as DSM source or as a
JSON schema:

```js
const dsm = DSMDefinitions.jsonDecode(json);   // or from a live database's definitions
console.log(dsm.toDsm());                       // DSM language
console.log(dsm.jsonEncode());                  // JSON schema
```

```{note}
Pulling definitions from a live database requires a working database. See
{doc}`database` for the full walkthrough.
```
