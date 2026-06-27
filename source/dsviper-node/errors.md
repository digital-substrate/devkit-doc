# Error Handling

When a Viper C++ operation fails, the Node binding raises a regular JavaScript
`Error`. This chapter explains how to catch, interpret, and recover from those
errors. The Python equivalent is {doc}`../dsviper/errors`; the error model is
identical — only the idiom differs.

## The thrown ViperError

A Viper runtime error is a plain JS `Error`. You catch it like any other:

- its `.name` is `'ViperError'`, and
- its `.message` is the structured string
  `[process@host]:Component:Domain:Code:Message`.

```js
const { ValueInt64, ValueString } = require('@digitalsubstrate/dsviper');

try {
  ValueInt64.cast(new ValueString('hello'));   // wrong source type
} catch (e) {
  console.log(e.name);     // 'ViperError'
  console.log(e.message);  // '[…]:Viper.ValueInt64:TypeErrors:110:expected int64, got string [cast].'
  console.log(e instanceof Error);  // true
}
```

The message format is `[process@host]:Component:Domain:Code:Message`.

```{note}
Not every throw from the binding is a `ViperError`. Binding-level validation
(for example, building a value from an unusable native) surfaces as an ordinary
Node / N-API message, **not** the structured form. Check `e.name === 'ViperError'`
to distinguish a Viper runtime error from a JS-side type problem.
```

## Parsing error details

To read individual fields, parse the message with the `Error` **value** type.
It collides with the global `Error`, so import it under an alias:

```js
const { Error: VError, ValueInt64, ValueString } = require('@digitalsubstrate/dsviper');

try {
  ValueInt64.cast(new ValueString('hello'));
} catch (e) {
  const err = VError.parse(e.message);   // an Error value, or undefined
  if (err) {
    console.log(err.component());    // 'Viper.ValueInt64'
    console.log(err.domain());       // 'TypeErrors'
    console.log(typeof err.code());  // 'number'
    console.log(err.message());      // includes 'expected int64'
    console.log(err.hostname());     // the host where the error originated
    console.log(err.processName());  // the process name
  }
}
```

`VError.parse` returns `undefined` when the string is not a structured error —
empty input, free text, or a message missing the leading `[...]` bracket or
enough `:`-separated fields. Colons inside the trailing message are preserved.

```js
const { Error: VError } = require('@digitalsubstrate/dsviper');

VError.parse('');                              // undefined
VError.parse('not an error at all');           // undefined
VError.parse('a:b:c:1:msg');                   // undefined (no brackets)
VError.parse('[p@h]:C:D:7:msg: with: colons')
  .message();                                  // 'msg: with: colons'
```

The structured string round-trips through the accessors:

```js
const { Error: VError, ValueInt64, ValueString } = require('@digitalsubstrate/dsviper');

let desc;
try {
  ValueInt64.cast(new ValueString('hello'));
} catch (e) {
  desc = e.message;
}
const err = VError.parse(desc);
const rebuilt = `[${err.processName()}@${err.hostname()}]`
  + `:${err.component()}:${err.domain()}:${err.code()}:${err.message()}`;
console.log(rebuilt === desc);  // true
```

A negative `code` is preserved as-is:

```js
const { Error: VError } = require('@digitalsubstrate/dsviper');

const err = VError.parse('[p@h]:C:D:-1:negative code');
console.log(err.code());      // -1
console.log(err.message());   // 'negative code'
```

### Error value methods

| Method                 | Return                | Description                                   |
|------------------------|-----------------------|-----------------------------------------------|
| `Error.parse(str)`     | `Error` or `undefined`| Parse an error string into an Error value     |
| `err.component()`      | `string`              | The subsystem (e.g. `'Viper.ValueInt64'`)     |
| `err.domain()`         | `string`              | The functional domain (e.g. `'TypeErrors'`)   |
| `err.code()`           | `number`              | Numeric error code within the domain          |
| `err.message()`        | `string`              | Human-readable description                     |
| `err.hostname()`       | `string`              | Host where the error originated               |
| `err.processName()`    | `string`              | Process name                                  |
| `err.explained()`      | `string`              | Full formatted error string                   |

`explained()` returns a single string containing every field:

```js
const { Error: VError } = require('@digitalsubstrate/dsviper');

VError.parse('[app@server]:MyComp:MyDomain:99:something broke').explained();
// includes 'server', 'app', 'MyComp', and 'something broke'
```

### Labelling the process

`Error.setProcessName(name)` sets the process field stamped into errors raised
afterwards. This is global state — it affects all subsequent errors, so pick a
stable name at startup:

```js
const { Error: VError } = require('@digitalsubstrate/dsviper');

VError.setProcessName('TestApp');
// errors raised from now on report processName() === 'TestApp'
```

---

## Common error categories

### Type mismatch errors

These occur when a value has the wrong type for the operation — including a
`cast` to an incompatible type:

```js
const { ValueInt64, ValueString } = require('@digitalsubstrate/dsviper');

try {
  ValueInt64.cast(new ValueString('hello'));
} catch (e) {
  console.log(e.message);  // '...expected int64, got string [cast].'
}
```

**Recovery**: check `value.type()` before casting, or validate inputs before
handing them to a typed constructor. See {doc}`types_values`.

### Empty-container access

Popping an empty set or reading past the end of a vector raises a structured
error:

```js
const { ValueSet, TypeSet, ValueVector, TypeVector, Type } = require('@digitalsubstrate/dsviper');

try {
  new ValueSet(new TypeSet(Type.INT64)).pop();   // empty set
} catch (e) {
  // a ViperError; VError.parse(e.message) is non-null
}

try {
  new ValueVector(new TypeVector(Type.INT64)).at(0);  // out of range
} catch (e) {
  // a ViperError
}
```

**Recovery**: check `size()` before `at()` / `pop()`. See {doc}`collections`.

### Empty optional unwrap

Unwrapping a nil optional fails. Always check `isNil()` first:

```js
const { ValueOptional, TypeOptional, Type } = require('@digitalsubstrate/dsviper');

const v = new ValueOptional(new TypeOptional(Type.STRING));  // nil
const content = v.isNil() ? 'default value' : v.unwrap();
```

```{note}
`ValueOptional` is a Viper C++ container, unrelated to JavaScript's `null` /
`undefined`. It wraps a value with nil / non-nil semantics and provides
`isNil()`, `unwrap()`, and `wrap()`. See {doc}`structures`.
```

### Key not found (not an error)

Reading a missing key from a database does **not** throw. `get()` returns a
`ValueOptional` that is nil:

```js
const result = db.get(attachment, key);   // always a ValueOptional
const value = result.isNil() ? null : result.unwrap();
```

Use `has()` to check existence before unwrapping:

```js
if (db.has(attachment, key)) {
  const value = db.get(attachment, key).unwrap();
}
```

See {doc}`database`.

### DSM parse errors

Parsing invalid DSM returns a report instead of throwing, so you can collect
every error at once:

```js
const { DSMBuilder } = require('@digitalsubstrate/dsviper');

const builder = new DSMBuilder();
builder.append('test.dsm', `
namespace Test {00000000-0000-0000-0000-000000000001} {
    struct A { invalid_type1 f1; };
};
`);
const [report, dsmDefs, defs] = builder.parse();

if (report.hasError()) {
  const errors = [...report.errors()];
  console.log(errors[0].message());  // mentions 'invalid_type1'
}
```

See {doc}`dsm`.

---

## Best practices

- Check `e.name === 'ViperError'` to tell a Viper runtime error apart from a
  JS-side or binding-level failure.
- Check `isNil()` before calling `unwrap()` on an optional.
- Check `report.hasError()` after `DSMBuilder.parse()` before using the returned
  definitions.
- `VError.parse()` can return `undefined`; guard the result before calling
  accessors.

---

## Debugging tips

### Enable verbose logging

Use Viper C++'s logging system to trace operations. A logger is constructed with
a numeric threshold; `logger.logging()` returns the logging facade with one
method per level:

```js
const { LoggerConsole } = require('@digitalsubstrate/dsviper');

// Level thresholds are plain numbers (ALL=0, DEBUG=10, INFO=20,
// WARNING=30, ERROR=40, CRITICAL=50).
const logger = new LoggerConsole(20);   // INFO and above
const logging = logger.logging();

logging.info('Starting database operation');
logging.error('Operation failed');
```

The facade exposes `log(level, message)` plus `debug()`, `info()`, `warning()`,
`error()`, and `critical()`; messages below the logger's threshold are filtered
out.

### Remote errors

When working against a remote database or service, the `host` and `process`
fields of the structured message identify where the failure occurred:

```
[db-process@remote-server]:Viper:Database:3:Connection timeout
```

Parse it with `VError.parse()` and read `hostname()` / `processName()` to route
the diagnostic. See {doc}`database`.
