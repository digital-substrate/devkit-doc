# Structures and Enumerations

Structures (named-field records) and enumerations are user-defined types that
must be registered with `Definitions` before use. This chapter covers creating
and working with both from Node. The Python equivalent is
{doc}`../dsviper/structures`; the type system is identical — only the idiom
differs. The one real difference is field access: Node has no attribute protocol
(see the warning below), so reads and writes go through explicit methods.

Examples assume the binding is in scope:

```js
const {
  Value, Type, Definitions, NameSpace, ValueUUId,
  TypeStructureDescriptor, ValueStructure,
  TypeVector, ValueVector,
} = require('@digitalsubstrate/dsviper');
```

## Defining a structure

Structures are defined within a `Definitions` context. Build a descriptor, add
fields, then materialise the type with `createStructure`:

```js
const defs = new Definitions();
const ns = new NameSpace(ValueUUId.create(), 'Tuto');

const d = new TypeStructureDescriptor('Point');
d.addField('x', Type.INT32);
d.addField('y', Type.INT32);
const tPoint = defs.createStructure(ns, d);

tPoint.fields().map((f) => f.name());   // ['x', 'y']
```

`addField` also accepts a default `Value` instead of a bare type. The default is
applied to every instance that does not override the field:

```js
const dCfg = new TypeStructureDescriptor('Config');
dCfg.addField('name', Value.create(Type.STRING, 'Default'));
dCfg.addField('count', Value.create(Type.INT32, 42));
const tConfig = defs.createStructure(ns, dCfg);

new ValueStructure(tConfig).at('name');   // 'Default'
new ValueStructure(tConfig).at('count');  // 42
```

A descriptor with no fields, or a duplicate field name, throws — the descriptor
is validated eagerly:

```js
defs.createStructure(ns, new TypeStructureDescriptor('Empty')); // throws ViperError

const dup = new TypeStructureDescriptor('Dup');
dup.addField('field1', Type.STRING);
dup.addField('field1', Type.INT32);   // throws ViperError
```

## Constructing instances

The ergonomic form is to construct directly from a plain object. Nested objects
are accepted for nested structure fields:

```js
const p = new ValueStructure(tPoint, { x: 3, y: 4 });
p.at('x');   // 3
p.at('y');   // 4
```

Omit the object to get the type's defaults (zero, or per-field defaults declared
on the descriptor):

```js
new ValueStructure(tConfig).at('count');  // 42
```

Passing another `ValueStructure` of the same type makes a deep copy:

```js
const q = new ValueStructure(tPoint, p);
q.set('x', 99);
p.at('x');   // 3  (independent copy)
```

When a structure is the document of an attachment, `Attachment.createStructure`
is the equivalent factory — see [Using structures with databases](#using-structures-with-databases).

## Field access

```{warning}
Node has **no attribute protocol**. `struct.x` is `undefined` — silently, with
no error — because `x` is a Viper field, not a JavaScript property. This is the
one quiet footgun on this page. Always read and write fields through `at` / `set`
(or the bulk and deep-access methods below). Every one of those is fail-fast: an
unknown field, a wrong-type value, or an empty key-path throws.
```

### One field at a time

`set(field, value)` writes; `at(field)` reads back the JavaScript native:

```js
const s = new ValueStructure(tPoint);
s.set('x', 10);
s.at('x');   // 10

s.x;         // undefined  <-- NOT a field read; there is no attribute protocol
```

By default `at` returns the native (a JS `number` for `INT32`/`FLOAT`/`DOUBLE`
fields, a `bigint` for `INT64`, a `string` for `STRING`, ...). Pass `false` as a
second argument to get the wrapped `Value` handle instead:

```js
const { ValueString } = require('@digitalsubstrate/dsviper');

const cfg = new ValueStructure(tConfig, { name: 'x', count: 1 });
cfg.at('name', false) instanceof ValueString;   // true
```

Both `at` and `set` are type-checked and fail-fast:

```js
s.set('nope', 1);          // throws ViperError — unknown field
s.at('nope');              // throws ViperError — unknown field
s.set('x', 'not an int');  // throws ViperError — wrong type
```

### Several fields at once

`assign(object)` writes several fields in one call. It is partial (only the keys
you pass are touched), type-checked per field, and returns the structure so it
chains:

```js
const s2 = new ValueStructure(tPoint);
s2.assign({ x: 3, y: 4 });
s2.at('x');   // 3

s2.assign({ y: 9 });   // partial update
s2.at('y');            // 9

s2.assign({ nope: 1 }); // throws ViperError — unknown field
```

`toObject()` is the reverse: it returns the fields as a plain object (natives by
default, wrapped handles with `toObject(false)`), which destructures cleanly:

```js
const { x, y } = new ValueStructure(tPoint, { x: 3, y: 4 }).toObject();
// x === 3, y === 4
```

### INT64 fields are bigint

`INT32`, `FLOAT`, and `DOUBLE` fields round-trip as JavaScript numbers; `INT64`
fields are `bigint`. Mind the `n` suffix:

```js
const dSample = new TypeStructureDescriptor('Sample');
dSample.addField('count', Type.INT64);
dSample.addField('ratio', Type.DOUBLE);
const tSample = defs.createStructure(ns, dSample);

const s = new ValueStructure(tSample, { count: 9876543210n, ratio: 3.14159 });
typeof s.at('count');   // 'bigint'
typeof s.at('ratio');   // 'number'
```

## Nested structures and deep access

A structure can hold other structures. Construct them inline with nested objects:

```js
const dAddr = new TypeStructureDescriptor('Address');
dAddr.addField('city', Type.STRING);
dAddr.addField('zip', Type.INT32);
const tAddr = defs.createStructure(ns, dAddr);

const dUser = new TypeStructureDescriptor('User');
dUser.addField('name', Type.STRING);
dUser.addField('address', tAddr);
const tUser = defs.createStructure(ns, dUser);

const u = new ValueStructure(tUser, {
  name: 'Bob',
  address: { city: '', zip: 0 },
});
u.at('address') instanceof ValueStructure;   // true
```

To reach into a nested field, chaining `at` works (`u.at('address').at('city')`),
but `setIn` / `getIn` express a deep read or write directly with a key-path:

```js
u.setIn(['address', 'city'], 'Paris');
u.getIn(['address', 'city']);   // 'Paris'
```

A key-path step is resolved polymorphically by what sits at that level — a field
name for a structure, an index for a vector, a key for a map:

```js
const dUser2 = new TypeStructureDescriptor('User2');
dUser2.addField('tags', new TypeVector(Type.STRING));
const tUser2 = defs.createStructure(ns, dUser2);

const u2 = new ValueStructure(tUser2, {
  tags: new ValueVector(new TypeVector(Type.STRING), ['a', 'b']),
});
u2.setIn(['tags', 1], 'z');   // vector index step
u2.getIn(['tags', 1]);        // 'z'
```

`setIn` returns the structure, so calls chain. `getIn(path, false)` returns the
wrapped handle instead of the native. Both are fail-fast — an unknown field, a
wrong-type leaf, or an empty key-path throws:

```js
u.setIn(['address', 'nope'], 'x');   // throws — unknown field
u.setIn(['address', 'city'], 42);    // throws — wrong-type leaf
u.getIn([]);                         // throws — empty key-path
```

Deep access is offered only on the nestable containers (structures, vectors,
maps); it is not defined on flat bytes (`ValueBlob`) or a by-membership
`ValueSet`.

## Enumerations

Enumerations are types with a fixed set of named cases. Build them through a
`TypeEnumerationDescriptor`, mirroring the structure flow:

```js
const { TypeEnumerationDescriptor, ValueEnumeration } = require('@digitalsubstrate/dsviper');

const eStatus = new TypeEnumerationDescriptor('Status');
eStatus.addCase('pending', 'Waiting to start');
eStatus.addCase('active', 'In progress');
eStatus.addCase('completed', 'Finished');
const tStatus = defs.createEnumeration(ns, eStatus);
```

Create a value by case name (most common) or by 0-based index:

```js
new ValueEnumeration(tStatus, 'active').name();   // 'active'
new ValueEnumeration(tStatus, 0).name();          // 'pending'
```

Read its properties:

```js
const status = new ValueEnumeration(tStatus, 'active');
status.name();             // 'active'
status.index();            // 1
status.typeEnumeration().equals(tStatus);   // true
```

The default value of an enumeration type is its first case:

```js
Value.create(tStatus).name();   // 'pending'
```

```{note}
Compare enumeration values with `.equals` / `.compare` (both accept a native
case name), never with `==` — between two `Value`s `==` is reference equality,
not value equality. See {doc}`types_values` for the value-semantics rules.
```

## Errors

A thrown Viper error is a JavaScript `Error` whose `name` is `'ViperError'`:

```js
try {
  new ValueStructure(tPoint).at('nope');
} catch (e) {
  e.name;   // 'ViperError'
}
```

See {doc}`errors` for the full error model.

## Using structures with databases

Structures are usually stored as the documents of an attachment. Define the
attachment against a concept type, then mint documents with
`Attachment.createStructure`:

```js
const tNode = defs.createConcept(ns, 'Node');
const att = defs.createAttachment(ns, 'Node_Data', tNode, tPoint);
const doc = att.createStructure({ x: 1, y: 2 });
```

Locating and mutating a field of a stored document inside a transaction goes
through a `Path` rather than `at` / `setIn` — see {doc}`database` (Path) for the
mutation and commit API.
