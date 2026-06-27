# Serialization

Encoding and decoding values: the high-level `Value` codecs, the named stream
codecs behind them, byte-size prediction via sizers, and the raw/binary/token
streams those codecs are built on.

Most code never touches a stream directly. To turn a {js:class}`Value` into a
blob and back you call `Value.encode` / `Value.decode` (binary),
`Value.jsonEncode` / `Value.jsonDecode` (JSON, for web and REST), or
`Value.dumps` / `Value.loads` (the native format). Decoding always needs the
`Type` and a const {js:class}`Definitions` so the decoder knows the shape it is
reading. The classes on this page are the machinery underneath: pick a named
codec with {js:class}`Codec` when you need a specific wire format, drive an
encoder/decoder/sizer through {js:class}`StreamCodecInstancing`, and reach for
the {js:class}`StreamReaderFile` / {js:class}`StreamWriterFile` family for
low-level file, blob, and shared-memory I/O.

**When to use**: reach for the `Value.*` codecs for ordinary
serialization. Drop to {js:class}`Codec` and the stream classes when you are
implementing a custom protocol, predicting an encoded size ahead of time, or
streaming straight to a file or shared-memory region.

## Quick Start

A value survives a binary round-trip when the decoded copy `.equals` the
original — never compare values with `==`:

```js
const { Value, ValueString, Type, Definitions } = require('@digitalsubstrate/dsviper');

// Const definitions tell the decoder the shape it is reading back.
const defs = new Definitions().const();

const value = new ValueString('hello');

// Binary: encode to a blob, decode it back with its type + definitions.
const blob = Value.encode(value);
const decoded = Value.decode(blob, Type.STRING, defs);
console.log(value.equals(decoded)); // true

// JSON: same round-trip, for web and REST integration.
const json = Value.jsonEncode(value);
console.log(value.equals(Value.jsonDecode(json, Type.STRING, defs))); // true

// Native dumps/loads: the same shape again.
console.log(value.equals(Value.loads(Value.dumps(value), Type.STRING, defs))); // true
```

Vectors and other containers round-trip the same way — build the vector from its
type and an array of elements, then pass that type to `decode`:

```js
const { Value, ValueVector, TypeVector, Type, Definitions } = require('@digitalsubstrate/dsviper');

const defs = new Definitions().const();
const t = new TypeVector(Type.INT64);
const vec = new ValueVector(t, [1n, 2n, 3n]); // 64-bit elements are bigint

const decoded = Value.decode(Value.encode(vec), t, defs);
console.log(vec.equals(decoded)); // true
```

To work below `Value`, resolve a named codec and drive its encoder, decoder, and
sizer. The sizer predicts the exact encoded byte length without producing a
blob:

```js
const { Codec } = require('@digitalsubstrate/dsviper');

const codec = Codec.STREAM_BINARY;          // or Codec.check('StreamTokenBinary')

const encoder = codec.createEncoder();
encoder.writeBool(true);
encoder.writeUint32(42);
encoder.writeDouble(3.14);
const data = encoder.endEncoding();         // a ValueBlob

const decoder = codec.createDecoder(data);
console.log(decoder.readBool());            // true
console.log(decoder.readUint32());          // 42

// A sizer predicts the byte length the same writes would produce.
const sizer = codec.createSizer();
console.log(sizer.sizeOfBool() + sizer.sizeOfUint32() + sizer.sizeOfDouble());
console.log(data.size());                   // matches the prediction
```

An unknown codec name, or a token mismatch while decoding, throws a JS `Error`
whose `name` is `'ViperError'`:

```js
const { Codec } = require('@digitalsubstrate/dsviper');

try {
  Codec.check('an unknown codec');
} catch (err) {
  console.log(err.name); // 'ViperError'
}
```

## Choosing the right approach

| Use case | API | Note |
|----------|-----|------|
| Binary serialization | `Value.encode` / `Value.decode` | Default codec; decode needs type + const definitions |
| JSON for web / REST | `Value.jsonEncode` / `Value.jsonDecode` | Web integration |
| Native format | `Value.dumps` / `Value.loads` | Round-trips like the others |
| Specific wire format | {js:class}`Codec` | `STREAM_BINARY`, `STREAM_RAW`, `StreamTokenBinary`, ... |
| Encoder / decoder / sizer | {js:class}`StreamCodecInstancing` | `createEncoder` / `createDecoder` / `createSizer` |
| Predict encoded size | `createSizer().sizeOf*()` | Byte length without building a blob |
| File / blob / shared-memory I/O | {js:class}`StreamReaderFile` / {js:class}`StreamWriterFile` | Low-level streaming |

See also the {doc}`serialization guide <../serialization>`, the
{doc}`blobs reference <blobs>` for `ValueBlob`, and the equivalent
{doc}`Python serialization reference <../../dsviper/api/serialization>`.

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`Codec` | A class used to instantiate a codec |
| {js:class}`Fuzzer` | A class used to generate a random value |
| {js:class}`StreamBinaryReader` | A class used to read data through the StreamRawReading interface (handle endianness) |
| {js:class}`StreamBinaryWriter` | A class used to write data through the StreamRawWriting interface (handle endianness) |
| {js:class}`StreamCodecInstancing` | An interface used to create encoder, decoder and sizer |
| {js:class}`StreamDecoding` | An interface used to read data from a blob |
| {js:class}`StreamEncoding` | An interface used to write data to a blob |
| {js:class}`StreamRawReader` | An class used to read data through the StreamRawReading interface |
| {js:class}`StreamRawReading` | An interface used to read data |
| {js:class}`StreamRawWriter` | A class used to write data through the StreamRawWriting interface |
| {js:class}`StreamRawWriting` | An interface to write data |
| {js:class}`StreamReaderBlob` | A class used to read data from a blob |
| {js:class}`StreamReaderFile` | A class used to read data from a file |
| {js:class}`StreamReaderSharedMemory` | A class used to read data from a shared memory region |
| {js:class}`StreamReading` | An interface used to read data |
| {js:class}`StreamSizing` | An interface used to get the size of data |
| {js:class}`StreamTokenBinaryReader` | A class used to read through the StreamRawReading interface (handle endianness) |
| {js:class}`StreamTokenBinaryWriter` | A class used to write through the StreamRawWriting interface (handle endianness) |
| {js:class}`StreamWriterBlob` | A class used to write data to a blob |
| {js:class}`StreamWriterFile` | A class used to write data to a file |
| {js:class}`StreamWriterSharedMemory` | A class used to write data to a shared memory region |
| {js:class}`StreamWriting` | An interface used to read data |

## Reference

```{js:autoclass} Codec
:members:
```

```{js:autoclass} Fuzzer
:members:
```

```{js:autoclass} StreamBinaryReader
:members:
```

```{js:autoclass} StreamBinaryWriter
:members:
```

```{js:autoclass} StreamCodecInstancing
:members:
```

```{js:autoclass} StreamDecoding
:members:
```

```{js:autoclass} StreamEncoding
:members:
```

```{js:autoclass} StreamRawReader
:members:
```

```{js:autoclass} StreamRawReading
:members:
```

```{js:autoclass} StreamRawWriter
:members:
```

```{js:autoclass} StreamRawWriting
:members:
```

```{js:autoclass} StreamReaderBlob
:members:
```

```{js:autoclass} StreamReaderFile
:members:
```

```{js:autoclass} StreamReaderSharedMemory
:members:
```

```{js:autoclass} StreamReading
:members:
```

```{js:autoclass} StreamSizing
:members:
```

```{js:autoclass} StreamTokenBinaryReader
:members:
```

```{js:autoclass} StreamTokenBinaryWriter
:members:
```

```{js:autoclass} StreamWriterBlob
:members:
```

```{js:autoclass} StreamWriterFile
:members:
```

```{js:autoclass} StreamWriterSharedMemory
:members:
```

```{js:autoclass} StreamWriting
:members:
```
