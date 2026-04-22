# Collections

Viper provides strongly-typed collections that mirror Python's built-in collections while
enforcing type safety.

## Vector

`ValueVector` is compatible with Python's list API:

```pycon
>>> from dsviper import *

# Create vector<string>
>>> v = Value.create(TypeVector(Type.STRING), ["hello", "world"])
>>> v
['hello', 'world']

# Append
>>> v.append("!")
>>> v
['hello', 'world', '!']

# Extend with Python list
>>> v.extend(["from", "python"])

# Index access
>>> v[0]
'hello'
>>> v[-1]
'python'

# Slice
>>> v[1:3]
['world', '!']

# Length
>>> len(v)
5

# Iterate
>>> for item in v:
...     print(item)
```

### Type Safety

```pycon
>>> v.append(42)  # Wrong type
ViperError: expected type 'str', got 'int'
```

## Set

`ValueSet` is compatible with Python's set API:

```pycon
# Create set<int64>
>>> s = Value.create(TypeSet(Type.INT64), {1, 2, 3, 2, 1})
>>> s
{1, 2, 3}

# Add
>>> s.add(4)

# Remove
>>> s.remove(1)

# Membership
>>> 2 in s
True

# Length
>>> len(s)
3

# Set operations
>>> s2 = Value.create(TypeSet(Type.INT64), {3, 4, 5})
>>> s.union(s2)
{2, 3, 4, 5}
>>> s.intersection(s2)
{3, 4}
```

## Map

`ValueMap` is compatible with Python's dict API:

```pycon
# Create map<string, int64>
>>> m = Value.create(TypeMap(Type.STRING, Type.INT64), {"a": 1, "b": 2})
>>> m
{'a': 1, 'b': 2}

# Get/Set
>>> m["c"] = 3
>>> m["a"]
1

# Keys, values, items
>>> list(m.keys())
['a', 'b', 'c']
>>> list(m.values())
[1, 2, 3]
>>> list(m.items())
[('a', 1), ('b', 2), ('c', 3)]

# Delete
>>> del m["a"]

# Length
>>> len(m)
2
```

### Complex Keys

Maps can use complex types as keys:

```pycon
# map<tuple<int64, int64>, string>
>>> t = TypeMap(TypeTuple([Type.INT64, Type.INT64]), Type.STRING)
>>> m = Value.create(t, {(1, 2): "one-two", (3, 4): "three-four"})
>>> m[(1, 2)]
'one-two'
```

## Optional

`ValueOptional` holds a value or nothing:

```pycon
# Create empty optional<string>
>>> opt = Value.create(TypeOptional(Type.STRING))
>>> opt
nil

>>> opt.is_nil()
True

# Wrap a value
>>> opt.wrap("hello")
>>> opt
Optional('hello')

>>> opt.is_nil()
False

# Unwrap
>>> opt.unwrap()
'hello'

# Unwrap empty optional raises error
>>> empty = Value.create(TypeOptional(Type.STRING))
>>> empty.unwrap()
ViperError: Try to unwrap empty optional<string>
```

### Initialize with Value

```pycon
>>> opt = Value.create(TypeOptional(Type.INT64), 42)
>>> opt
Optional(42)
```

## Tuple

`ValueTuple` holds heterogeneous values:

```pycon
# tuple<string, int64, bool>
>>> t = TypeTuple([Type.STRING, Type.INT64, Type.BOOL])
>>> v = Value.create(t, ("hello", 42, True))
>>> v
('hello', 42, True)

# Access by index
>>> v[0]
'hello'
>>> v[1]
42
```

## Variant

`ValueVariant` holds one value from a set of possible types:

```pycon
# string | int64
>>> t = TypeVariant([Type.STRING, Type.INT64])
>>> v = Value.create(t, "a string")
>>> v.type()
string|int64

# Change the value
>>> v.wrap(42)
>>> v.unwrap()
42

# Wrong type
>>> v.wrap(3.14)
ViperError: expected type 'string|int64', got 'float'
```

## XArray

### Vector vs XArray: When to Use Each

| Feature                 | Vector                         | XArray                |
|-------------------------|--------------------------------|-----------------------|
| **Indexing**            | Integer indices (0, 1, 2...)   | UUID positions        |
| **Insert/Remove**       | Indices shift                  | Positions stable      |
| **Multiplayer editing** | Last-write-wins                | Merge-friendly        |
| **Performance**         | Faster for local use           | Slight overhead       |
| **Use case**            | Local arrays, batch processing | Shared editable lists |

**Why XArray?** In multiplayer scenarios, two users might insert at "index 3"
simultaneously. With Vector, one insert wins and the other is lost or corrupted. With
XArray, each element has a UUID position that remains stable across merges.

**Example**: A shared todo list where multiple users add/remove items should use XArray. A
local computation buffer should use Vector.

### XArray Basics

`ValueXArray` preserves order during concurrent mutations using UUID positions instead of
indices:

```pycon
>>> t = TypeXArray(Type.STRING)
>>> x = Value.create(t)

# Append returns the position
>>> pos1 = x.append("first")
>>> pos2 = x.append("second")

# Access by position (UUID)
>>> x[pos1]
'first'

# Insert at position
>>> x.insert(pos1, "inserted")
```

## Any

`TypeAny` accepts any value:

```pycon
>>> v = Value.create(TypeVector(Type.ANY))
>>> v.append("a string")
>>> v.append(42)
>>> v.append([1, 2, 3])

>>> v.description()
"['a string':string:any, 42:int64:any, [1, 2, 3]:vector<int64>:any]:vector<any>"
```

## Nested Collections

Collections can be nested:

```pycon
# vector<map<string, int64>>
>>> t = TypeVector(TypeMap(Type.STRING, Type.INT64))
>>> v = Value.create(t)
>>> v.append({"a": 1})
>>> v.append({"b": 2, "c": 3})
>>> v
[{'a': 1}, {'b': 2, 'c': 3}]
```

## What's Next

- [Structures and Enumerations](structures.md) - User-defined types
- [Database](database.md) - Persisting collections
