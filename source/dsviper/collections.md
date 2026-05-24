# Collections

Viper C++ provides strongly-typed collections that mirror Python's built-in collections while
enforcing type safety.

## Vector

`ValueVector` is compatible with Python's list API:

```{doctest}
>>> from dsviper import *

>>> v = Value.create(TypeVector(Type.STRING), ["hello", "world"])
>>> v
['hello', 'world']
```

Append a single element:

```{doctest}
>>> v.append("!")
>>> v
['hello', 'world', '!']
```

Extend with a Python list:

```{doctest}
>>> v.extend(["from", "python"])
>>> v
['hello', 'world', '!', 'from', 'python']
```

Index access (positive and negative):

```{doctest}
>>> v[0]
'hello'
>>> v[-1]
'python'
```

Length:

```{doctest}
>>> len(v)
5
```

Iterate:

```{doctest}
>>> for item in v:
...     print(item)
hello
world
!
from
python
```

```{note}
`ValueVector` does not currently support slice access (`v[1:3]`). Iterate
explicitly or use `list(v)` to materialize a slice in Python.
```

### Type Safety

```{doctest}
>>> v.append(42)
Traceback (most recent call last):
    ...
dsviper.ViperError: ...expected type 'str', got 'int'...
```

## Set

`ValueSet` is compatible with Python's set API:

```{doctest}
>>> s = Value.create(TypeSet(Type.INT64), {1, 2, 3, 2, 1})
>>> s
{1, 2, 3}
```

Add and remove:

```{doctest}
>>> s.add(4)
>>> s.remove(1)
>>> s
{2, 3, 4}
```

Membership and length:

```{doctest}
>>> 2 in s
True
>>> len(s)
3
```

Set operations:

```{doctest}
>>> s2 = Value.create(TypeSet(Type.INT64), {3, 4, 5})
>>> s.union(s2)
{2, 3, 4, 5}
>>> s.intersection(s2)
{3, 4}
```

## Map

`ValueMap` is compatible with Python's dict API:

```{doctest}
>>> m = Value.create(TypeMap(Type.STRING, Type.INT64), {"a": 1, "b": 2})
>>> m
{'a': 1, 'b': 2}
```

Get and set:

```{doctest}
>>> m["c"] = 3
>>> m["a"]
1
```

Keys, values, items:

```{doctest}
>>> list(m.keys())
['a', 'b', 'c']
>>> list(m.values())
[1, 2, 3]
>>> list(m.items())
[('a', 1), ('b', 2), ('c', 3)]
```

Delete and length:

```{doctest}
>>> del m["a"]
>>> len(m)
2
```

### Complex Keys

Maps can use complex types as keys:

```{doctest}
>>> t = TypeMap(TypeTuple([Type.INT64, Type.INT64]), Type.STRING)
>>> m = Value.create(t, {(1, 2): "one-two", (3, 4): "three-four"})
>>> m[(1, 2)]
'one-two'
```

## Optional

`ValueOptional` holds a value or nothing:

```{doctest}
>>> opt = Value.create(TypeOptional(Type.STRING))
>>> opt
nil

>>> opt.is_nil()
True
```

Wrap a value:

```{doctest}
>>> opt.wrap("hello")
>>> opt
Optional('hello')

>>> opt.is_nil()
False
```

Unwrap:

```{doctest}
>>> opt.unwrap()
'hello'
```

Unwrapping an empty optional raises an error:

```{doctest}
>>> empty = Value.create(TypeOptional(Type.STRING))
>>> empty.unwrap()
Traceback (most recent call last):
    ...
dsviper.ViperError: ...Try to unwrap empty optional<string>...
```

### Initialize with Value

```{doctest}
>>> opt = Value.create(TypeOptional(Type.INT64), 42)
>>> opt
Optional(42)
```

## Tuple

`ValueTuple` holds heterogeneous values. Note that booleans render with Viper C++'s
own repr (`true`/`false`), not Python's `True`/`False`:

```{doctest}
>>> t = TypeTuple([Type.STRING, Type.INT64, Type.BOOL])
>>> v = Value.create(t, ("hello", 42, True))
>>> v
('hello', 42, true)
```

Access by index:

```{doctest}
>>> v[0]
'hello'
>>> v[1]
42
```

## Variant

`ValueVariant` holds one value from a set of possible types:

```{doctest}
>>> t = TypeVariant([Type.STRING, Type.INT64])
>>> v = Value.create(t, "a string")
>>> v.type()
string|int64
```

Change the value:

```{doctest}
>>> v.wrap(42)
>>> v.unwrap()
42
```

Wrong type is rejected:

```{doctest}
>>> v.wrap(3.14)
Traceback (most recent call last):
    ...
dsviper.ViperError: ...expected type 'string|int64', got 'float'...
```

## XArray

### Vector vs XArray: When to Use Each

| Feature                | Vector                         | XArray                    |
|------------------------|--------------------------------|---------------------------|
| **Indexing**           | Integer indices (0, 1, 2...)   | UUID positions            |
| **Insert/Remove**      | Indices shift                  | Positions stable          |
| **Concurrent editing** | Last-write-wins                | Converges without loss    |
| **Performance**        | Faster for local use           | Slight overhead           |
| **Use case**           | Local arrays, batch processing | Concurrently edited lists |

**Why XArray?** Under concurrent editing, two authors might insert at "index 3"
simultaneously. With Vector, one insert wins and the other is lost or corrupted. With
XArray, each element has a UUID position that remains stable across convergence.

**Example**: A shared todo list where multiple users add/remove items should use XArray. A
local computation buffer should use Vector.

### XArray Basics

`ValueXArray` preserves order during concurrent mutations using UUID positions instead of
integer indices.

Create and append. Note that `append()` returns `x.END` — the zero-UUID
sentinel that means "the end of the array" — not the position of the
just-appended element:

```{doctest}
>>> t = TypeXArray(Type.STRING)
>>> x = Value.create(t)

>>> x.END
00000000-0000-0000-0000-000000000000

>>> x.append("first")
00000000-0000-0000-0000-000000000000
>>> x.append("second")
00000000-0000-0000-0000-000000000000
>>> x
['first', 'second']
```

Recover the actual UUID position of an element with `position(index)` or
`position_of(value)`, then access it with `at(pos)` (or `x[pos]`):

```{doctest}
>>> pos0 = x.position(0)
>>> x.at(pos0)
'first'
>>> x[pos0]
'first'

>>> p = x.position_of("second")
>>> x.at(p)
'second'
```

`insert(pos, value)` inserts **before** the given position and returns the
UUID position of the new element. Inserting at `x.END` is therefore
equivalent to appending; inserting at `pos0` prepends:

```{doctest}
>>> p_third = x.insert(x.END, "third")
>>> x.at(p_third)
'third'

>>> p_zero = x.insert(pos0, "zero")
>>> x.at(p_zero)
'zero'

>>> x
['zero', 'first', 'second', 'third']
```

Iterate over values, or over `(position, value)` pairs:

```{doctest}
>>> for item in x:
...     print(item)
zero
first
second
third
```

## Any

`TypeAny` accepts any value:

```{doctest}
>>> v = Value.create(TypeVector(Type.ANY))
>>> v.append("a string")
>>> v.append(42)
>>> v.append([1, 2, 3])

>>> v.description()
"['a string':string:any, 42:int64:any, [1, 2, 3]:vector<int64>:any]:vector<any>"
```

## Nested Collections

Collections can be nested:

```{doctest}
>>> t = TypeVector(TypeMap(Type.STRING, Type.INT64))
>>> v = Value.create(t)
>>> v.append({"a": 1})
>>> v.append({"b": 2, "c": 3})
>>> v
[{'a': 1}, {'b': 2, 'c': 3}]
```

