# Core Utilities

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
| {js:class}`Path` | Constructs the location of a portion of a value |
| {js:class}`Error` | The structured error raised by Viper: component, domain, code and message |
| {js:class}`Logging` | An interface to emit a message |
| {js:class}`LoggerReport` | Collects messages instead of emitting them |
| {js:class}`HashSHA1` | Hashes data with SHA1 |
| {js:class}`NameSpace` | A UUID and a name, under which types are registered |
| {js:class}`Definitions` | Registers concepts, clubs, enums, structs and attachments |

The mirror of this page for the Python binding is {doc}`../../dsviper-python/api/core`.

## Namespace

```{js-summary}
NameSpace
```

## Paths

```{js-summary}
Path
PathConst
PathComponent
PathElementInfo
PathEntryKeyInfo
```

## Function Pools

```{js-summary}
FunctionPrototype
```

## Hashing

```{js-summary}
Hashing
HashCRC32
HashMD5
HashSHA1
HashSHA256
HashSHA3
```

## Logging

```{js-summary}
Logging
LoggerConsole
LoggerReport
LoggerNull
```

## Utilities

```{js-summary}
Error
Cancelation
SharedMemory
Socket
Float16
KeyHelper
KeyNamer
```

## Reference

```{js:autoclass} NameSpace
:members:
```

```{js:autoclass} Path
:members:
```

```{js:autoclass} PathConst
:members:
```

```{js:autoclass} PathComponent
:members:
```

```{js:autoclass} PathElementInfo
:members:
```

```{js:autoclass} PathEntryKeyInfo
:members:
```

```{js:autoclass} FunctionPrototype
:members:
```

```{js:autoclass} Hashing
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

```{js:autoclass} Logging
:members:
```

```{js:autoclass} LoggerConsole
:members:
```

```{js:autoclass} LoggerReport
:members:
```

```{js:autoclass} LoggerNull
:members:
```

```{js:autoclass} Error
:members:
```

```{js:autoclass} Cancelation
:members:
```

```{js:autoclass} SharedMemory
:members:
```

```{js:autoclass} Socket
:members:
```
```{js:autoclass} Float16
:members:
```

```{js:autoclass} KeyHelper
:members:
```

```{js:autoclass} KeyNamer
:members:
```
