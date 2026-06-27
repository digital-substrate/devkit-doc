# Collections

Viper C++ provides strongly-typed collections that mirror the JavaScript built-ins
while enforcing type safety. The Python equivalent is {doc}`../dsviper/collections`;
the collections are identical — only the idiom differs.

Each collection comes as a `TypeX` (the parameterized type) and a `ValueX` (a value
of that type). Build a value either with its constructor, `new ValueX(type[, init])`,
or through the universal factory, `Value.create(type[, init])`. See
{doc}`types_values` for the constructor rules.

```{note}
These are Viper values, so they follow Java-like value semantics. Use `.equals`,
`.hash`, and `.compare` (each accepts a native argument) rather than the JavaScript
operators — `==` between two values is reference equality, never value equality.
`INT64`/`UINT64` elements round-trip through `bigint`, so integer literals carry the
`n` suffix (`42n`).
```

Examples assume the binding is in scope:

```js
const {
    Value, Type,
    ValueVector, TypeVector,
    ValueSet, TypeSet,
    ValueMap, TypeMap,
    ValueTuple, TypeTuple,
    ValueOptional, TypeOptional,
    ValueVariant, TypeVariant,
    ValueXArray, TypeXArray, ValueUUId,
    ValueAny,
} = require('@digitalsubstrate/dsviper');
```

## Vector

`ValueVector` is the ordered, integer-indexed sequence:

```js
const v = Value.create(new TypeVector(Type.STRING), ['hello', 'world']);
[...v];               // ['hello', 'world']
v.size();             // 2
```

Append a single element, or extend with a native array:

```js
v.append('!');
v.extend(['from', 'node']);
[...v];   // ['hello', 'world', '!', 'from', 'node']
```

Index access reads with `.at(i)` and writes with `.set(i, value)`:

```js
const n = new ValueVector(new TypeVector(Type.INT64), [10n, 20n, 30n]);
n.at(0);          // 10n
n.set(0, 99n);
n.at(0);          // 99n
n.size();         // 3
```

Vectors are iterable, so spread them into a native array:

```js
[...new ValueVector(new TypeVector(Type.INT64), [1n, 2n, 3n])];   // [1n, 2n, 3n]
```

`.contains`, `.insert(i, value)`, `.pop([i])`, `.remove(value)`, and `.clear()`
round out the list protocol:

```js
const m = new ValueVector(new TypeVector(Type.INT64), [1n, 2n, 3n]);
m.contains(2n);   // true
m.insert(0, 0n);  // [0n, 1n, 2n, 3n]
m.pop();          // 3n  (removes the last)
m.remove(1n);     // removes the first occurrence
```

### Error cases

An out-of-range index or an absent element throws:

```js
const v = new ValueVector(new TypeVector(Type.INT64), [1n, 2n, 3n]);
v.at(10);      // throws — out of range
v.remove(99n); // throws — absent element
```

## Set

`ValueSet` is a sorted, deduplicated set. Iterating always yields the elements in
sorted order, regardless of insertion order:

```js
const T = new TypeSet(Type.INT64);
const s = new ValueSet(T, [3n, 1n, 4n, 1n, 5n]);
[...s];        // [1n, 3n, 4n, 5n]  (sorted, deduplicated)
s.size();      // 4
```

Add, test membership, and remove:

```js
s.add(2n);
s.contains(2n);   // true
s.remove(1n);     // throws if absent
s.discard(99n);   // silent if absent
```

Set algebra returns a new set and leaves the operands unchanged. Each operation also
accepts a native array (the element type is known, so it is decoded for you):

```js
const a = new ValueSet(T, [1n, 2n, 3n, 4n]);
const b = new ValueSet(T, [3n, 4n, 5n, 6n]);

[...a.union(b)];                 // [1n, 2n, 3n, 4n, 5n, 6n]
[...a.intersection(b)];          // [3n, 4n]
[...a.difference(b)];            // [1n, 2n]
[...a.symmetricDifference(b)];   // [1n, 2n, 5n, 6n]

[...a.union([7n, 8n])];          // native array accepted
```

The in-place variants mutate the receiver: `.update`, `.intersectionUpdate`,
`.differenceUpdate`, `.symmetricDifferenceUpdate`. Predicates `.issubset`,
`.issuperset`, and `.isdisjoint` also accept a set or a native array:

```js
new ValueSet(T, [1n, 2n]).issubset([1n, 2n, 3n]);   // true
new ValueSet(T, [1n, 2n]).isdisjoint([3n, 4n]);     // true
```

## Map

`ValueMap` is a sorted-key map. A native map literal is an array of `[key, value]`
pairs; spreading yields the entries in sorted-key order (like a JavaScript `Map`):

```js
const T = new TypeMap(Type.INT64, Type.STRING);
const m = new ValueMap(T, [[2n, 'Two'], [1n, 'One']]);
[...m];   // [[1n, 'One'], [2n, 'Two']]  (keys sorted)
```

Read with `.at(key)`, write with `.set(key, value)`:

```js
m.set(3n, 'Three');
m.at(1n);         // 'One'
m.contains(3n);   // true
m.size();         // 3
```

`.at(missing)` throws; `.get(key[, default])` is the safe read:

```js
m.get(99n, 'D');   // 'D'  (default for a missing key)
m.get(99n);        // undefined
```

Keys, values, and items each come back as a Viper collection — a `ValueSet` of keys,
a `ValueVector` of values, a `ValueVector` of `[key, value]` tuples — all in key
order:

```js
[...m.keys()];                        // [1n, 2n, 3n]
[...m.values()];                      // ['One', 'Two', 'Three']
[...m.items()].map((t) => [...t]);    // [[1n, 'One'], [2n, 'Two'], [3n, 'Three']]
```

Remove with `.remove(key)` (throws if absent) or `.discard(key)` (silent); merge with
`.update(other)`, accepting a map or native pairs:

```js
m.remove(1n);
m.update([[4n, 'Four']]);   // native pairs accepted
```

### Complex keys

Any value type can be a key — including a composite. Pass a wrapped value as the key:

```js
const mapType = new TypeMap(new TypeMap(Type.STRING, Type.INT64), Type.STRING);
const mm = new ValueMap(mapType);
const k1 = new ValueMap(new TypeMap(Type.STRING, Type.INT64), [['a', 1n]]);
mm.set(k1, 'first');
mm.at(k1);   // 'first'
```

## Optional

`ValueOptional` holds a value or nothing. A bare construction is nil:

```js
const T = new TypeOptional(Type.INT64);
const opt = new ValueOptional(T);
opt.isNil();   // true
```

Wrap a value, read it back with `.unwrap()`, and clear it:

```js
opt.wrap(42n);
opt.isNil();    // false
opt.unwrap();   // 42n
opt.clear();
opt.isNil();    // true
```

Construct with an initial value directly, or use `.get(default)` to avoid the empty
case:

```js
new ValueOptional(T, 42n).unwrap();   // 42n
new ValueOptional(T).get(99n);        // 99n  (default when nil)
```

Unwrapping a nil optional throws:

```js
new ValueOptional(T).unwrap();   // throws — the optional is nil
```

## Tuple

`ValueTuple` holds a fixed, heterogeneous sequence. Construct it from a native array:

```js
const T = new TypeTuple([Type.STRING, Type.INT64, Type.BOOL]);
const t = new ValueTuple(T, ['hello', 42n, true]);
[...t];        // ['hello', 42n, true]
t.size();      // 3
```

Read with `.at(i)`; mutate in place with `.set(i, value)` or build a modified copy
with `.replace(i, value)`:

```js
t.at(0);                  // 'hello'
t.set(1, 99n);
t.at(1);                  // 99n
const w = t.replace(0, 'bye');   // new tuple; t is unchanged
```

A wrong-type element throws:

```js
new ValueTuple(T, [42n, 'hello', true]);   // throws — types swapped
```

## Variant

`ValueVariant` holds one value drawn from a set of member types. The active member is
chosen by what you wrap:

```js
const T = new TypeVariant([Type.BOOL, Type.INT64, Type.STRING]);
const v = new ValueVariant(T, 'a string');
v.unwrap();   // 'a string'
```

`.wrap(value)` swaps the active value — possibly changing the member type. You can
pin the member explicitly with a second `type` argument:

```js
v.wrap(42n);
v.unwrap();           // 42n
v.wrap(true);
v.unwrap();           // true
v.wrap(42n, Type.INT64);   // explicit member type
```

A non-member value is rejected:

```js
v.wrap(3.14);   // throws — double is not a member of bool|int64|string
```

```{note}
Member identity is exact: `true` and `1n` select different members, so a variant
wrapping `true` is not equal to one wrapping `1n`.
```

## XArray

`ValueXArray` is a sequence addressed by stable UUID *positions* rather than integer
indices, so concurrent inserts and removes neither collide nor shift one another. It
preserves insertion order, but its identity is positional: two arrays with the same
values but distinct UUIDs are **not** equal, whereas `.copy()` (which preserves
positions) is equal.

Build it from a native array, then read it back as a plain sequence by iterating or
via `.toVector()`:

```js
const T = new TypeXArray(Type.INT64);
const x = new ValueXArray(T, [1n, 2n, 3n]);
[...x];              // [1n, 2n, 3n]
[...x.toVector()];   // [1n, 2n, 3n]  (a ValueVector)
```

`.append(value)` and `.extend(array)` add at the end and return the END marker (the
zero/invalid UUID that means "the end of the array"), *not* the new position.
`.insert(before, value)` inserts before a position and returns the real new position:

```js
x.append(4n);               // returns ValueXArray.END
ValueXArray.END.isValid();  // false

const x2 = new ValueXArray(T, [1n, 2n]);
const p = x2.insert(ValueXArray.END, 3n);   // append; returns the new position
p.isValid();   // true
```

Recover a position from an integer index with `.position(i)` (or from a value with
`.positionOf(value)`), then use it with `.at`, `.set`, and `.remove`:

```js
const v = new ValueXArray(T, [10n, 20n, 30n]);
const pos1 = v.position(1);
v.at(pos1);          // 20n
v.set(pos1, 99n);
v.at(pos1);          // 99n
v.index(pos1);       // 1

v.remove(v.position(0));
[...v];              // [99n, 30n]
```

```{note}
`ValueXArray` does not bind `.size()` — its length is `[...x].length`. An invalid
position passed to `.at`, `.set`, or `.remove` throws.
```

## Any

`ValueAny` is a type-erased holder for any single value. Construct it empty (nil) or
around a value, which it wraps by deducing the type:

```js
const a = new ValueAny();
a.isNil();   // true

a.wrap(42n);
a.isNil();    // false
a.unwrap();   // 42n
a.type().equals(Type.ANY);   // true
```

It re-wraps freely across types, and holds containers as well as primitives:

```js
const v = new ValueAny(42n);
v.wrap('string');   v.unwrap();   // 'string'
v.wrap(true);       v.unwrap();   // true

const vec = new ValueVector(new TypeVector(Type.INT64), [1n, 2n, 3n]);
v.wrap(vec);
v.unwrap().equals(vec);   // true
[...v.unwrap()];          // [1n, 2n, 3n]
```

`.clear()` returns it to nil; unwrapping a nil `ValueAny` throws:

```js
const a = new ValueAny(42n);
a.clear();
a.isNil();      // true
a.unwrap();     // throws — the holder is nil
```

## Nested collections

Collections compose freely — a value of one collection can be an element, a key, or
the wrapped payload of another:

```js
const T = new TypeVector(new TypeMap(Type.STRING, Type.INT64));
const v = new ValueVector(T);
v.append(new ValueMap(new TypeMap(Type.STRING, Type.INT64), [['a', 1n]]));
v.append(new ValueMap(new TypeMap(Type.STRING, Type.INT64), [['b', 2n], ['c', 3n]]));
v.size();   // 2
[...v.at(0)];   // [['a', 1n]]
```

The same holds for wrappers — an `Optional`, a `Variant`, or a `ValueAny` can hold a
container, and `.unwrap()` returns the wrapped Viper value:

```js
const ot = new TypeOptional(new TypeSet(Type.INT64));
const some = new ValueOptional(ot, new ValueSet(new TypeSet(Type.INT64), [1n, 2n, 3n]));
some.unwrap() instanceof ValueSet;   // true
[...some.unwrap()];                  // [1n, 2n, 3n]
```
</content>
</invoke>
