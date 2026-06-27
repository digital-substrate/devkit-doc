# Core utilities

This is the catch-all bucket for the cross-cutting primitives the rest of the
binding builds on: `Definitions` and `NameSpace` register the DSM types of an
application; `Path` addresses and edits a portion of a nested value; `Error`
parses the structured description carried by a thrown Viper error; the
`Hash*` family hashes blobs; and the `Logger*` family emits leveled diagnostics.
Because the bucket is broad, the Quick Start below touches only a representative
few — consult the Reference section below for the rest.

**When to use**: reach for `Path` to navigate or mutate nested
{doc}`values <values>` by location; for `Error` to turn a caught
`ViperError` into queryable fields; and for the logging family when you need
leveled, optionally-captured diagnostics. `Definitions` and `NameSpace` come
into play when you register custom types (see {doc}`../database`).

## Quick Start

```js
const { Path, Error: VError, LoggerReport, ValueInt64, ValueString } =
    require('@digitalsubstrate/dsviper');

// Path — address a portion of a nested value, then read or write it.
// JS has no `/` operator overload, so chain the fluent .field()/.index()/.key().
const path = new Path().field('user').field('settings').key('theme').const();
path.representation();              // human-readable, includes "user" / "settings"
// path.at(value) reads; path.set(value, 'dark') writes; both take a Value.
const decoded = Path.decode(path.encode(), defs.const());  // ValueBlob round-trip

// Error — a thrown Viper runtime error is a JS Error with a structured message.
try {
    ValueInt64.cast(new ValueString('hello'));   // type mismatch -> throws
} catch (e) {
    e.name;                        // "ViperError"
    const err = VError.parse(e.message);          // undefined if it doesn't match
    err.component();               // "Viper.ValueInt64"
    err.domain();                  // "TypeErrors"
    err.code();                    // a number
    err.message();                 // "expected int64, got string [cast]."
    err.explained();               // multi-line, all fields
}

// Logging — a leveled facade. Levels are raw uint8 severities passed to the
// constructor (DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50); a logger
// emits only when its level <= the message level. LoggerReport captures to an
// array; LoggerConsole writes to stdout; LoggerNull discards.
const reporter = new LoggerReport(20);            // INFO and above
const log = reporter.logging();
log.info('started');
log.warning('careful');
reporter.messages();               // ["INF:started", "WNG:careful"]
```

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Key classes

| Class | Purpose | Example |
|-------|---------|---------|
| {js:class}`Path` | Address and edit a portion of a nested value | `new Path().field('x').key('k')` |
| {js:class}`Error` | Parse a thrown `ViperError` into fields | `Error.parse(e.message)` |
| {js:class}`Logging` | Leveled diagnostics interface | `logger.logging().info(msg)` |
| {js:class}`LoggerReport` | Capture messages into an array | `new LoggerReport(20).messages()` |
| {js:class}`HashSHA1` | Hash a `ValueBlob` (also MD5, SHA256, SHA3, CRC32) | `HashSHA1.hash(blob)` |
| {js:class}`NameSpace` | Group registered types under a UUID | `new NameSpace(uuid, 'App')` |
| {js:class}`Definitions` | Register custom DSM types | `new Definitions()` |

The mirror of this page for the Python binding is {doc}`../../dsviper/api/core`.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`Databasing` | An interface used to abstract the implementation of the persistence layer for a CRUD like database |
| {js:class}`DocumentNode` | A class used to represent a node in the tree representation of a value |
| {js:class}`Error` | The structured error raised by Viper: component, domain, code and message |
| {js:class}`Float16` | A class used to handle float16 representation |
| {js:class}`FunctionPrototype` | A class used to represent the prototype of a function |
| {js:class}`HashCRC32` | A class used to hash data with CRC32 |
| {js:class}`HashMD5` | A class used to hash data with MD5 |
| {js:class}`HashSHA1` | A class used to hash data with SHA1 |
| {js:class}`HashSHA256` | A class used to hash data with SHA256 |
| {js:class}`HashSHA3` | A class used to hash a data with SHA3 |
| {js:class}`Hashing` | An interface to abstract a hasher |
| {js:class}`Html` | A class used to generate HTML representation |
| {js:class}`KeyHelper` | A class used to collect keys, attachments and missing attachments for a key |
| {js:class}`KeyNamer` | A class used to get a name for a key from available attachments |
| {js:class}`LoggerConsole` | A class used to display a message on the console |
| {js:class}`LoggerNull` | A class used to discard messages |
| {js:class}`LoggerReport` | A class used to collect messages |
| {js:class}`Logging` | An interface to emit a message |
| {js:class}`NameSpace` | A class used to describe a namespace |
| {js:class}`Path` | A class used to construct the location of a portion of a value |
| {js:class}`PathComponent` | A class used to represent a component of a Path |
| {js:class}`PathConst` | A class used to retrieve a value from a Path |
| {js:class}`PathElementInfo` | A class used to represent the various information for an element of a set |
| {js:class}`PathEntryKeyInfo` | A class used to represent various information for an entry of a map |
| {js:class}`SQLite` | A class used to retrieve the configuration of SQLite3 |
| {js:class}`ServiceRemote` | A class used to connect to a remote service |
| {js:class}`ServiceRemoteAttachmentFunction` | A class used to call a remote attachment function |
| {js:class}`ServiceRemoteAttachmentFunctionPool` | A class used to represent a remote attachment function pool |
| {js:class}`ServiceRemoteAttachmentFunctionPoolFunction` | A class used to represent a remote attachment function |
| {js:class}`ServiceRemoteAttachmentFunctionPoolFunctions` | A class used to represent the remote attachment functions |
| {js:class}`ServiceRemoteFunction` | A class used to call a remote function |
| {js:class}`ServiceRemoteFunctionPool` | A class used to represent a remote function pool |
| {js:class}`ServiceRemoteFunctionPoolFunction` | A class used to represent a remote function |
| {js:class}`ServiceRemoteFunctionPoolFunctions` | A class used to represent the functions of a pool |
| {js:class}`SharedMemory` | A class used to represent a shared memory region |

## Reference

```{js:autoclass} Databasing
:members:
```

```{js:autoclass} DocumentNode
:members:
```

```{js:autoclass} Error
:members:
```

```{js:autoclass} Float16
:members:
```

```{js:autoclass} FunctionPrototype
:members:
```

```{js:autoclass} HashCRC32
:members:
```

```{js:autoclass} HashMD5
:members:
```

```{js:autoclass} HashSHA1
:members:
```

```{js:autoclass} HashSHA256
:members:
```

```{js:autoclass} HashSHA3
:members:
```

```{js:autoclass} Hashing
:members:
```

```{js:autoclass} Html
:members:
```

```{js:autoclass} KeyHelper
:members:
```

```{js:autoclass} KeyNamer
:members:
```

```{js:autoclass} LoggerConsole
:members:
```

```{js:autoclass} LoggerNull
:members:
```

```{js:autoclass} LoggerReport
:members:
```

```{js:autoclass} Logging
:members:
```

```{js:autoclass} NameSpace
:members:
```

```{js:autoclass} Path
:members:
```

```{js:autoclass} PathComponent
:members:
```

```{js:autoclass} PathConst
:members:
```

```{js:autoclass} PathElementInfo
:members:
```

```{js:autoclass} PathEntryKeyInfo
:members:
```

```{js:autoclass} SQLite
:members:
```

```{js:autoclass} ServiceRemote
:members:
```

```{js:autoclass} ServiceRemoteAttachmentFunction
:members:
```

```{js:autoclass} ServiceRemoteAttachmentFunctionPool
:members:
```

```{js:autoclass} ServiceRemoteAttachmentFunctionPoolFunction
:members:
```

```{js:autoclass} ServiceRemoteAttachmentFunctionPoolFunctions
:members:
```

```{js:autoclass} ServiceRemoteFunction
:members:
```

```{js:autoclass} ServiceRemoteFunctionPool
:members:
```

```{js:autoclass} ServiceRemoteFunctionPoolFunction
:members:
```

```{js:autoclass} ServiceRemoteFunctionPoolFunctions
:members:
```

```{js:autoclass} SharedMemory
:members:
```
