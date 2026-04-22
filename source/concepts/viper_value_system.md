# Value System

The Value System provides runtime values with reference semantics and a Python-like API.
Every value knows its type and can be serialized, compared, and hashed automatically.

## Reference Semantics

Viper uses reference semantics (like Python) rather than value semantics (like C++ STL):

| C++ STL (Value Semantics)    | Viper (Reference Semantics)             |
|------------------------------|-----------------------------------------|
| `vector<int> a = b;` copies  | `shared_ptr<ValueVector> a = b;` shares |
| Assignment copies data       | Assignment shares reference             |
| Explicit std::move for moves | Explicit `copy()` for deep copy         |

### Sharing by Default

```cpp
auto v1 = ValueVector::make(TypeInt32::Instance());
v1->append(ValueInt32::make(1));

auto v2 = v1;  // v2 shares the same data as v1
v2->append(ValueInt32::make(2));

// Both v1 and v2 now contain [1, 2]
```

### Explicit Copy When Needed

```cpp
auto v1 = ValueVector::make(TypeInt32::Instance());
v1->append(ValueInt32::make(1));

auto v2 = Value::copy(v1);  // v2 is a deep copy
v2->append(ValueInt32::make(2));

// v1 contains [1], v2 contains [1, 2]
```

---

## Value Interface

All values inherit from the `Value` base class:

```cpp
class Value {
public:
    virtual TypeCode typeCode() const = 0;
    virtual std::shared_ptr<Type> type() const = 0;
    virtual std::string representation() const = 0;
    virtual std::size_t hash() const = 0;
    virtual bool equal(std::shared_ptr<Value const> const & other) const = 0;
    virtual Ordered compare(std::shared_ptr<Value const> const & other) const = 0;

    // Static helper for deep copy
    static std::shared_ptr<Value> copy(std::shared_ptr<Value const> const & value);
};
```

### Self-Description

Every value can describe itself:

```cpp
auto v = ValueVector::make(TypeInt32::Instance());
v->append(ValueInt32::make(1));
v->append(ValueInt32::make(2));

v->representation();  // "[1, 2]"
v->type()->representation();  // "vector<int32>"
```

---

## Primitives

Immutable atomic values:

| Class         | Factory          | Constants           |
|---------------|------------------|---------------------|
| ValueBool     | `make(bool)`     | `True()`, `False()` |
| ValueInt8     | `make(int8_t)`   | `Zero()`, `One()`   |
| ValueInt16    | `make(int16_t)`  | `Zero()`, `One()`   |
| ValueInt32    | `make(int32_t)`  | `Zero()`, `One()`   |
| ValueInt64    | `make(int64_t)`  | `Zero()`, `One()`   |
| ValueUInt8    | `make(uint8_t)`  | `Zero()`, `One()`   |
| ValueUInt16   | `make(uint16_t)` | `Zero()`, `One()`   |
| ValueUInt32   | `make(uint32_t)` | `Zero()`, `One()`   |
| ValueUInt64   | `make(uint64_t)` | `Zero()`, `One()`   |
| ValueFloat    | `make(float)`    | `Zero()`, `One()`   |
| ValueDouble   | `make(double)`   | `Zero()`, `One()`   |
| ValueString   | `make(string)`   | `Empty()`           |
| ValueUUId     | `make(uuid)`     | `Invalid()`         |
| ValueBlobId   | `make(blobId)`   | `Invalid()`         |
| ValueCommitId | `make(commitId)` | `Invalid()`         |
| ValueVoid     | `Instance()`     | Singleton           |

### Static Factory Methods

Constants are exposed as class attributes (not method calls):

```python
# Python usage
v = dsviper.ValueDouble.ZERO  # Class attribute
v = dsviper.ValueDouble.ONE  # Class attribute
```

---

## Containers

Mutable collections with Python-like API:

### ValueVector

Dynamic typed array:

```cpp
auto v = ValueVector::make(TypeVector::make(TypeInt32::Instance()));
v->append(ValueInt32::make(1));
v->append(ValueInt32::make(2));
v->insert(1, ValueInt32::make(10));  // [1, 10, 2]
v->pop(0);                           // Remove at index 0, returns value
v->at(0);                            // -> 10
v->size();                           // -> 2
```

Python equivalent:

```python
v = dsviper.ValueVector.make(dsviper.TypeInt32.Instance())
v.append(1)  # Native int accepted, converted via metadata
v[0]  # -> ValueInt32(1)
len(v)  # -> 1
```

### ValueMap

Ordered dictionary:

```cpp
auto m = ValueMap::make(TypeMap::make(TypeString::Instance(), TypeInt32::Instance()));
m->set(ValueString::make("a"), ValueInt32::make(1));
m->get(ValueString::make("a"));  // -> ValueInt32(1) or nullptr
m->at(ValueString::make("a"));   // -> ValueInt32(1), throws if missing
m->keys();                       // -> ValueSet
m->values();                     // -> ValueVector
m->items();                      // -> ValueVector of tuples
```

Python equivalent:

```python
m = dsviper.ValueMap.make(dsviper.TypeString.Instance(), dsviper.TypeInt32.Instance())
m["a"] = 1  # Native types accepted
m["a"]  # -> ValueInt32(1)
list(m.keys())  # -> [ValueString("a")]
```

### ValueSet

Ordered set:

```cpp
auto s = ValueSet::make(TypeSet::make(TypeInt32::Instance()));
s->add(ValueInt32::make(1));
s->add(ValueInt32::make(2));
s->contains(ValueInt32::make(1));  // -> true
s->discard(ValueInt32::make(1));   // Remove without error if missing
s->size();                         // -> 1
```

---

## Compound Types

### ValueStructure

Named fields with types:

```cpp
// 1. Create descriptor
auto descriptor = TypeStructureDescriptor::make("Person");
descriptor->addField("name", TypeString::Instance());
descriptor->addField("age", TypeInt32::Instance());

// 2. Register type via Definitions
auto personType = defs->createStructure(nameSpace, descriptor);

// 3. Create value
auto person = ValueStructure::make(personType);
person->set("name", ValueString::make("Alice"));
person->set("age", ValueInt32::make(30));
person->at("name");  // -> ValueString("Alice")
```

### ValueEnumeration

Enumerated case value:

```cpp
// 1. Create descriptor
auto descriptor = TypeEnumerationDescriptor::make("Color");
descriptor->addCase("Red");
descriptor->addCase("Green");
descriptor->addCase("Blue");

// 2. Register type via Definitions
auto colorType = defs->createEnumeration(nameSpace, descriptor);

// 3. Create value
auto red = ValueEnumeration::make(colorType, "Red");
red->typeEnumerationCase->name;  // -> "Red" (public const member)
```

### ValueOptional

Nullable wrapper:

```cpp
auto optType = TypeOptional::make(TypeDouble::Instance());

auto opt = ValueOptional::make(optType, ValueDouble::make(3.14));
opt->isNil();   // -> false
opt->unwrap();  // -> ValueDouble(3.14)

auto nil = ValueOptional::make(optType);  // No value = nil
nil->isNil();   // -> true
```

### ValueVariant

Union type:

```cpp
auto variant = ValueVariant::make(variantType, ValueInt32::make(42));
variant->unwrap();  // -> ValueInt32(42)
```

---

## Special Values

### ValueKey

Typed reference to a concept instance:

```cpp
auto typeKey = TypeKey::make(cameraType);  // TypeKey wraps TypeConcept
auto key = ValueKey::make(typeKey, UUId::create());
key->instanceId;   // -> UUId (public const member)
key->typeConcept;  // -> TypeConcept (public const member)
```

### ValueXArray

CRDT array with UUID positions for concurrent editing:

```cpp
auto xaType = TypeXArray::make(TypeString::Instance());
auto xa = ValueXArray::make(xaType);

auto pos = xa->append(ValueString::make("hello"));  // Returns new position UUID
xa->set(pos, ValueString::make("world"));           // Update at position
xa->at(pos);                                        // -> ValueString("world")
```

### ValueAny

Dynamic container (type erasure):

```cpp
auto any = ValueAny::make(ValueInt32::make(42));
any->isNil();   // -> false
any->unwrap();  // -> ValueInt32(42)
```

---

## Seamless Python Integration

dsviper accepts Python natives as input since metadata drives conversion:

```python
# Python natives are accepted
v = dsviper.ValueVector.make(dsviper.TypeInt32.Instance())
v.append(42)  # Python int -> ValueInt32
v.extend([1, 2, 3])  # Python list -> multiple ValueInt32

m = dsviper.ValueMap.make(dsviper.TypeString.Instance(), dsviper.TypeDouble.Instance())
m["key"] = 3.14  # Python str/float -> ValueString/ValueDouble
```

However, dsviper is a **strong-typed layer over Python**: type mismatches raise exceptions
immediately.

```python
v = dsviper.ValueVector.make(dsviper.TypeInt32.Instance())
v.append("hello")  # RAISES: expected Int32, got String
```

---

## See Also

- [Type System](viper_type_system.md) - Type-Value duality
- [Philosophy](viper_philosophy.md) - Reference semantics rationale
- [Patterns](viper_patterns.md) - Token Constructor pattern
- [Glossary](viper_glossary.md) - Value terminology
