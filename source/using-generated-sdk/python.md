# Python

You defined a data model in DSM and ran Kibo over it with the
{doc}`kibo-template-viper <../kibo-template-viper/index>` pack. What you got back — and
what you work against every day — is a typed Python package over the
[`dsviper`](https://pypi.org/project/dsviper/) wheel. This page is that daily surface, end
to end: what the package holds, how its objects behave, how documents are stored, how to
cross to the runtime, and what is raised when something does not fit.

Producing the package is {doc}`kibo-project <../kibo/kibo-project>`'s job, packaging it as a
wheel is described in {doc}`../kibo-template-viper/wheels`, and the raw runtime the package
delegates to is the {doc}`dsviper for Python <../dsviper-python/index>` chapter.

The examples are doctests, run against the package generated from two small DSM
namespaces. `Tuto` is the model the runtime pages use:

```text
namespace Tuto {f529bc42-0618-4f54-a3fb-d55f95c5ad03} {

concept User;

struct Login    { string nickname; string password; };
struct Identity { string firstname; string lastname; };
enum Status     { pending, active, completed };
struct Account  { Status state; };

attachment<User, Login> login;
attachment<User, Identity> identity;
attachment<User, Account> account;
// … and two more, avatar and portrait

};
```

`Studio` adds what Tuto lacks — a concept that is another, a club, a structure holding a
structure and containers, a declared default:

```text
namespace Studio {3a5c2f8e-6b1d-4c7a-9e2f-8d4b6a1c3e5f} {

concept Member;
concept Admin is a Member;
concept Device;

club Principal;
membership Principal Member;
membership Principal Device;

struct Name { string first; string last; };
struct Profile {
    Name name;
    vector<string> tags;
    set<string> roles;
    map<string, string> settings;
    optional<string> motto;
    uint8 level = 1;
};
struct Credentials { string login; };

attachment<Member, Profile> profile;
attachment<Principal, Credentials> credentials;

};
```

The infrastructure name (Kibo's `-n`) is `model`, so the package is `model`, with one module
per namespace: `model.tuto` and `model.studio`. Neither declares a function pool; the pool
examples use the `service` model of the generator's laboratory,
[devkit-codegen-test](https://github.com/digital-substrate/devkit-codegen-test), and are
not doctests, since a remote pool needs a running service.

## The package

```text
model/
├── __init__.py        ← definitions(), AnyConceptKey, AnyValue, Key, AttachmentProxy, the units
├── containers.py      ← one class per container shape the model uses
├── tuto/              ← one module per DSM namespace: Tuto is tuto
│   ├── data.py        ← structures, enumerations, keys, and their runtime ids (LOGIN, USER, …)
│   └── attachments.py ← one class per concept, one accessor per attachment
├── <pool>/            ← one subpackage per function pool (the Pool feature)
├── _codegen/          ← the runtime every generated package carries
└── resources.py       ← the model's definitions, embedded
```

Every file starts with a header naming the generator, the templates and the runtime range
(`dsviper >=1.2.29 <1.3.0`), and says *Do not edit by hand*: the package is a build
artifact, regenerated on every model change. A defect in it is fixed in the DSM model or
in the templates, never in the output.

The entry point gives the units, the containers and the model's definitions:

```{doctest}
>>> import dsviper
>>> import model
>>> from model import tuto, containers

>>> tuto.Login
<class 'model.tuto.data.Login'>
>>> containers.Set_of_Tuto_UserKey
<class 'model.containers.Set_of_Tuto_UserKey'>
>>> model.definitions()
<dsviper.DefinitionsConst object at ...>
```

`model.definitions()` is the model as the runtime knows it, decoded once from the embedded
blob: a database is extended with it, and decoding a value needs it. The package documents
itself — `help(model)` says where to start — and so does `_codegen`, whose docstrings are
the reference for the bridge, the containers and the stores.

### First steps

A document lives in a database that carries the model. Open one, extend it with
`model.definitions()`, write a document inside a transaction, and read it back:

```{doctest}
>>> db = dsviper.Database.create_in_memory()     # Database.create(path) on disk, Database.open(path) to reopen
>>> _ = db.extend_definitions(model.definitions())
>>> alice = tuto.UserKey.create()
>>> db.begin_transaction()
>>> tuto.attachments.User.login.set(db, alice, tuto.Login(nickname="alice"))
True
>>> db.commit()
>>> tuto.attachments.User.login.get(db, alice).unwrap().nickname
'alice'
```

[Attachments and stores](#attachments-and-stores) covers the rest: reading, deleting,
updating one field, and the `CommitDatabase` that keeps every commit.

### Where each name comes from

A namespace is a module, so two namespaces of one model may declare the same name. Static
names follow Kibo's snake_case rule, and a project spells a name its own way with `[names]`
in its `kibo.toml` (see {doc}`../kibo/kibo-project`):

| You write | It came from | DSM |
|---|---|---|
| `model.tuto` | a namespace | `namespace Tuto { … }` |
| `tuto.Login`, `.nickname` | a structure and its field | `struct Login { string nickname; … }` |
| `tuto.Status.ACTIVE` | an enumeration case | `enum Status { …, active, … }` |
| `tuto.UserKey` | a concept | `concept User;` |
| `tuto.attachments.User.login` | an attachment, grouped by its concept | `attachment<User, Login> login;` |
| `studio.attachments.Principal.credentials` | an attachment on a club, grouped by the club | `attachment<Principal, Credentials> credentials;` |
| `<unit>.attachments.AnyConcept.<attachment>` | an attachment on any concept | `attachment<any_concept, any> propertiesAnyConceptAny;` in the laboratory's `Demo` gives `demo.attachments.AnyConcept.properties_any_concept_any` |
| `<unit>.attachments.<Namespace>_<Concept>.<attachment>` | an attachment on a concept of another namespace | `attachment<Core::Thing, Parts::Colour> mark;` in the laboratory's `Woven` gives `woven.attachments.Core_Thing.mark` |
| `containers.Set_of_Tuto_UserKey` | a container shape | `set<key<User>>` |
| `tuto.LOGIN` | the runtime id of a type | `struct Login` |

A function, a field, an attachment or a module of several words is put in snake case: split
into words at its capitals, lowercased, the words joined by an underscore; an underscore the
author wrote is kept, and a run of capitals stays one word (`userIDs` gives `user_ids`).
With the laboratory's `features` model
(`concept ConceptC is a ConceptB;`, `attachment<ConceptA, set<int8>> propertiesSeInt8;`, a
field `key<ConceptA> f_A;`):

| DSM | Python | TypeScript |
|---|---|---|
| narrowing to `ConceptC` | `to_concept_c_key()` | `toConceptCKey()` |
| a club key from a `ConceptC` key | `from_concept_c_key()` | `fromConceptCKey()` |
| attachment `propertiesSeInt8` | `properties_se_int8` | `propertiesSeInt8` |
| field `f_A` | `f_a` | `f_A` |
| function `hasPlayer` | `has_player` | `hasPlayer` |

Classes keep the DSM spelling (`ConceptCKey`, `StructureS`), and an enumeration case is
uppercased (`Status.ACTIVE`). The complete rule is the
[`snake` format](../kibo/template_model.md#string-formats) of the Template Model.

A type of another namespace needs nothing new: import that namespace's module and use its
class. In the laboratory's `crossing` model, the `Woven` structure `Composites` has a field
`vector<Parts::Colour> f_vector`:

```python
from crossing import core, parts, woven

composites = woven.Composites()
composites.f_vector.append(parts.Colour(r=1.0))   # f_vector is containers.Vector_of_Parts_Colour
composites.f_tuple.set(0, core.Colour(r=1))       # tuple<Core::Colour, Parts::Colour>
```

A function pool is a subpackage imported by its path, `import model.<pool>`: the entry
module belongs to the `Base` feature and cannot import what only the `Pool` feature renders
(see [Pools](#pools)).

## Structures

A structure is constructed by naming its fields, in snake_case, as keywords. A field
is a property:

```{doctest}
>>> login = tuto.Login(nickname="alice", password="s3cret")
>>> login.nickname
'alice'
>>> login.password = "hunter2"
>>> login
Tuto::Login(nickname=alice, password=hunter2)
```

It can also be built from a source, given positionally: a dict keyed by the DSM field
names, as the runtime takes it, or a Viper value of its type (see [Ownership](#ownership)):

```{doctest}
>>> tuto.Login({"nickname": "bob"})
Tuto::Login(nickname=bob, password=)
```

A generated object is not a source: given one, of its own type or another, a constructor
raises `TypeError`. A copy is asked for with `copy()`:

```{doctest}
>>> tuto.Login(tuto.Login(nickname="bob"))
Traceback (most recent call last):
    ...
TypeError: Tuto::Login(nickname=bob, password=) is a generated value, not a source: copy() it, or pass a dict or a Viper value
>>> tuto.Login(nickname="bob").copy()
Tuto::Login(nickname=bob, password=)
```

Equality, hashing and order are the runtime's, delegated to the value; `copy()` returns an
independent copy:

```{doctest}
>>> login == tuto.Login(nickname="alice", password="hunter2")
True
>>> hash(login) == hash(login.copy())
True
>>> tuto.Login(nickname="a") < tuto.Login(nickname="b")
True
>>> other = login.copy()
>>> other.nickname = "carol"
>>> login.nickname
'alice'
```

### Defaults

A new structure holds the model's defaults: the default a field declares, or else the
default of its type (`""`, `0`, the first case of an enumeration, an empty container, the
invalid key). The declared default is the runtime's, on the structure's type:

```{doctest}
>>> tuto.Login()
Tuto::Login(nickname=, password=)
>>> tuto.Account().state
<Status.PENDING: 'pending'>
>>> tuto.Login.type().fields()[0].default_value() is None    # Tuto declares no default
True
```

Studio's `Profile` declares `uint8 level = 1;`:

```{doctest}
>>> from model import studio
>>> studio.Profile().level
1
>>> [field.name() for field in studio.Profile.type().fields()][5]
'level'
>>> studio.Profile.type().fields()[5].default_value()
1
```

`default_value()` is `None` also when the declared default equals the type's own default —
`EnumerationE f_E = .a;` in the laboratory's `features` model, `.a` being its first case, or
`uint8 n = 0;`, `string s = "";` — since
nothing then differs from the type. The new structure holds that value all the same.

## Enumerations

An enumeration is an `enum.Enum` whose values are the DSM case names:

```{doctest}
>>> tuto.Status.ACTIVE
<Status.ACTIVE: 'active'>
>>> tuto.Status.ACTIVE.value
'active'
>>> tuto.Status.from_str("completed")    # spelled as the DSM spells it
<Status.COMPLETED: 'completed'>
>>> tuto.Status["COMPLETED"]             # the member's own name, Python's
<Status.COMPLETED: 'completed'>
>>> tuto.Status(1)                       # by position
<Status.ACTIVE: 'active'>
>>> tuto.Status.ACTIVE.index()
1
>>> tuto.Status.PENDING < tuto.Status.ACTIVE < tuto.Status.COMPLETED   # in declaration order
True
```

A case is a host value, not a box: it converts to the runtime's enumeration value with
`unwrap_value()`, and back with `wrap_value()`:

```{doctest}
>>> tuto.Status.ACTIVE.unwrap_value()
.active
>>> tuto.Status.wrap_value(tuto.Status.ACTIVE.unwrap_value())
<Status.ACTIVE: 'active'>
```

## Ownership

**A generated object is a box around one Viper value**, with the API of the class it
faces. It holds nothing else, and every write reaches the runtime. The package follows
the runtime's reference semantics and adds no value semantics of its own:

- a field read hands back what the value holds — changing a nested structure or container
  read from a field changes the object it was read from;
- a field write keeps the object it is given — changing that object afterwards shows in
  the field;
- a constructor given a Viper value boxes it, without copying, and refuses a generated
  object with `TypeError`;
- set elements and map keys are copies;
- a document crossing a database is copied, on `set` as on `get`;
- any other copy is explicit: `copy()`, or `Cls(value.copy())`.

A constructor given a Viper value shares it; a copy is asked for:

```{doctest}
>>> value = login.unwrap_value()
>>> boxed = tuto.Login(value)
>>> boxed.nickname = "dave"
>>> login.nickname                      # the same value
'dave'
>>> copied = tuto.Login(value.copy())
>>> copied.nickname = "erin"
>>> login.nickname
'dave'
```

A document crossing a database is copied (the stores are described in
[Attachments and stores](#attachments-and-stores)):

```{doctest}
>>> store = dsviper.Database.create_in_memory()
>>> _ = store.extend_definitions(model.definitions())
>>> alice = tuto.UserKey.create()
>>> store.begin_transaction()
>>> tuto.attachments.User.login.set(store, alice, login)
True
>>> store.commit()
>>> login.nickname = "changed after set"
>>> tuto.attachments.User.login.get(store, alice).unwrap().nickname
'dave'
```

Studio's `Profile` holds a `Name`. A field read is live, and a field write keeps the object
it is given:

```{doctest}
>>> profile = studio.Profile()
>>> profile.name.first = "Ada"              # changes profile
>>> profile.name.first
'Ada'
>>> name = studio.Name(first="Grace")
>>> profile.name = name                     # profile keeps name
>>> name.last = "Hopper"
>>> profile.name
Studio::Name(first=Grace, last=Hopper)
```

## Containers

A container is a live view over the Viper container it wraps. The package declares one
class per container shape the model uses — in a structure field, an attachment or a pool —
in `containers`, named `<Kind>_of_<element>`: Tuto's attachments use
`containers.Set_of_Tuto_UserKey` for their keys and `containers.Optional_of_Tuto_Login` for
a read document.

The element is spelled the way the DSM spells it: a primitive by its name (`uint8`,
`string`), `Any` for an `any`, `AnyConceptKey` for a `key<any_concept>`, a type of a
namespace as `<Namespace>_<Type>` whatever the namespace (`Tuto_UserKey`, `Parts_Colour`),
and a container by its own class name. A map is `Map_of_<K>_to_<V>`, a variant joins its
alternatives with `_or_`, a tuple with `_and_`:

| DSM | Class |
|---|---|
| `optional<map<int8, string>>` | `Optional_of_Map_of_int8_to_string` |
| `set<key<any_concept>>` | `Set_of_AnyConceptKey` |
| `vector<Parts::Colour>` | `Vector_of_Parts_Colour` |
| `map<key<ModelA::Material>, key<ModelB::Material>>` | `Map_of_ModelA_MaterialKey_to_ModelB_MaterialKey` |
| `variant<string, uint8, StructureS>` in `Demo` | `Variant_of_string_or_uint8_or_Demo_StructureS` |

```{doctest}
>>> bob = tuto.UserKey.create()
>>> users = containers.Set_of_Tuto_UserKey([alice, bob])
>>> len(users), alice in users
(2, True)
>>> users.discard(bob)
>>> users == containers.Set_of_Tuto_UserKey([alice])
True

>>> maybe = containers.Optional_of_Tuto_Login()
>>> bool(maybe), maybe.is_nil()
(False, True)
>>> maybe.wrap(tuto.Login(nickname="frank"))
>>> maybe.unwrap().nickname
'frank'
>>> maybe.clear()
>>> maybe.get(tuto.Login(nickname="fallback")).nickname
'fallback'
```

Each kind declares what it does, so a type checker refuses a method the kind does not have:

| DSM | Class | What it does |
|---|---|---|
| `vector<T>` | `Vector_of_T` | a `list`-like sequence: `append`, `insert`, `extend`, `pop`, `remove`, `count`, `index`, `front`, `back`, `v[i] = e`, `del v[i]`, `+`, `+=` |
| `set<T>` | `Set_of_T` | sorted: `add`, `remove`, `discard`, `pop`, `min`, `max`, the set operations, their `_update` forms and operators |
| `map<K, V>` | `Map_of_K_to_V` | a `dict`-like mapping: `m[k]`, `get`, `items`, `popitem`, `min`, `max`, … |
| `optional<T>` | `Optional_of_T` | `is_nil`, `unwrap`, `wrap`, `get(default)`, `clear`; its truth is presence |
| `variant<A, B>` | `Variant_of_A_or_B` | per alternative: `is_A()`, `get_A()`, `set_A()`; `unwrap()` the element it holds, `wrap(e)` or `wrap(e, type)` |
| `tuple<A, B>` | `Tuple_of_A_and_B` | fixed length: `t[i]`, `set(i, e)`, and `get_0()`, `get_1()`, … typed by member |
| `xarray<T>` | `XArray_of_T` | positions that survive concurrent edits: `append`, `insert`, `remove`, `x[i]` or `x[position]`, `at`, `set`, `positions`, `position`, `index`, `has_position`, `position_of`, `items`, `extend`, `insert_position`, `disable_position`, `create_position()` and `END`, `to_vector` |
| `vec<T, n>` | `Vec<n>_of_T` | fixed length: `v[i]`, `set(i, e)` |
| `mat<T, c, r>` | `Mat<c>x<r>_of_T` | column-major: `m[c, r]`, `m[c]` a column, `at`, `set`, `column`, `columns`, `rows`; `len` its columns, `size()` its elements; iterating yields its columns |

Every view also has `unwrap_value()`, `copy()`, `==`, `hash()` and `<`. The vector, the set,
the tuple and the vec are sequences: `len`, `in`, iteration, `empty()`, `to_list()` and
`to_tuple()`. The xarray has `len`, `in`, iteration and `empty()`, and `to_vector()` in place
of `to_list()`; the mat has `to_tuple()`, a tuple of its columns; the map has `keys()`,
`values()` and `items()`.

A container field reads as its declared class — `Profile`'s fields are
`containers.Vector_of_string`, `Set_of_string`, `Map_of_string_to_string` and
`Optional_of_string` — and is changed in place:

```{doctest}
>>> profile = studio.Profile()
>>> profile.tags.extend(["math", "logic"])  # vector<string>
>>> profile.tags[0], len(profile.tags)
('math', 2)
>>> profile.roles.add("editor")             # set<string>
>>> "editor" in profile.roles
True
>>> profile.settings["theme"] = "dark"      # map<string, string>
>>> profile.settings["theme"]
'dark'
>>> profile.motto = "Ask"                   # optional<string>: its element, or None
>>> profile.motto.unwrap()
'Ask'
>>> profile.motto = None
>>> bool(profile.motto)
False
```

A container field also takes the host's own collection when nothing in it is generated: the
runtime decodes it at the line that writes it. A host collection of generated values is
refused with `TypeError`; build its declared class instead (`containers.Set_of_Tuto_UserKey(keys)`),
which checks every element where it is built:

```{doctest}
>>> profile.roles = {"admin", "editor"}
>>> profile.roles
{'admin', 'editor'}
>>> profile.tags = [studio.Name()]
Traceback (most recent call last):
    ...
TypeError: a native container of generated values: ...
```

A variant, a tuple, a vec and a mat behave as the table says. A variant tells, reads and
writes each alternative by its own method, named after the alternative as a container class
names its element: `is_string()`, `get_string()`, `set_string()` for a `string`, and
`is_Demo_StructureS()`, `get_Demo_StructureS()`, `set_Demo_StructureS()` for a structure
`StructureS` of `Demo` (a key is `…_Demo_ConceptAKey`). `unwrap()` reads whichever
alternative it holds, and `wrap(e)` writes the alternative the runtime finds for `e`, or the
one `wrap(e, type)` names. A `mat<uint8, 2, 3>` holding `{{1, 2, 3}, {4, 5, 6}}` gives
`m[1, 2] == 6`, `m[1] == (4, 5, 6)`, `len(m) == 2`, `m.size() == 6`, and
`list(m) == [(1, 2, 3), (4, 5, 6)]`: iterating a mat yields its columns.

An xarray is a sequence addressed by positions — `dsviper.ValueUUId`s that stay valid
whatever is inserted or removed around them, so that concurrent edits merge. `append(e)`
returns the new position; `insert(before, e)` inserts before a position (`END` appends) and
returns the new one. `x[i]` reads the i-th element, `x[position]` or `at(position)` reads by
position, and `position(i)` gives the position of the i-th element. `positions()` lists
every position the array holds, in order, including the removed ones, and ends with `END`;
`index(position) -> int | None` is the place of a position in that list, so it is not the
element's index once something was removed. `remove(position)` (or `del x[position]`)
removes the element and keeps the position, which reads `None` and can be `set` again;
`disable_position(position)` removes it for good, and a later `set` there stores nothing.
`insert_position(before, position)` inserts a position that holds no element yet, to be
`set` later. On the laboratory's `features` model:

```python
from features import containers

trail = containers.XArray_of_uint8()
first = trail.append(10)                    # the new position
second = trail.append(20)
third = trail.append(30)
len(trail), len(trail.positions())          # (3, 4): positions() ends with END
trail[second], trail[1]                     # (20, 20): by position, or by index
trail.remove(second)
list(trail), trail.has_position(second), trail[second]   # ([10, 30], True, None)
trail.index(third), trail.position(1) == third            # (2, True)
for position, element in trail.items():     # (position, element) pairs, removed ones left out
    print(position == first, element)       # True 10, then False 30
trail.insert(third, 25)                     # before third; returns its position
trail.to_vector()                           # [10, 25, 30]
```

What removes an element, per kind:

| Kind | Removing |
|---|---|
| vector | `del v[i]`, `remove(e)` (the first equal element; `dsviper.ViperError` when absent), `pop()` / `pop(i)`, `clear()` |
| set | `discard(e)` (nothing when absent), `remove(e)` (`KeyError` when absent), `pop()`, `clear()` |
| map | `del m[k]` or `remove(k)` (`KeyError` when absent), `discard(k)`, `pop(k)`, `clear()` |
| optional | `clear()`, or assign `None` to the field |
| xarray | `remove(position)` or `del x[position]`; `disable_position(position)` |
| variant, tuple, vec, mat | none: a fixed shape is changed by writing an element |

A shape the model does not use has no class. Build it with the runtime, from Viper values:

```{doctest}
>>> dsviper.Value.create(dsviper.TypeVector(tuto.UserKey.type()),
...                      [alice.unwrap_value(), alice.unwrap_value()])
[..., ...]
```

## Keys

A concept or a club gives a key class. A key is an identity, not data — the concept of its
instance and an instance id:

```{doctest}
>>> alice = tuto.UserKey.create()            # a fresh instance
>>> alice.description()
'...:Tuto::UserKey'
>>> alice.is_valid()
True
>>> type(alice.instance_id())                # the instance id
<class 'dsviper.ValueUUId'>
>>> tuto.UserKey(alice.instance_id()) == alice   # the key of that instance
True
>>> tuto.UserKey()                           # the invalid key
00000000-0000-0000-0000-000000000000:Tuto::UserKey
>>> tuto.UserKey().is_valid()
False
```

One instance has many views: its own key, its parent's, a club's, the any-concept key. They
are equal and hash alike whatever the view, so a native `set` or `dict` holds the instance
once. Every conversion is named and goes through the runtime, which keeps the instance:

```{doctest}
>>> anyone = alice.to_any_concept_key()
>>> anyone.description()
'...:AnyConceptKey(Tuto::UserKey)'
>>> anyone == alice, hash(anyone) == hash(alice), len({anyone, alice})
(True, True, 1)
>>> tuto.UserKey.from_any_concept_key(anyone) == alice
True
```

`from_any_concept_key()` answers `None` when the instance is not one of the concept. In
Studio, `Admin` is a `Member`:

```{doctest}
>>> admin = studio.AdminKey.create()
>>> member = admin.to_parent_key()          # widening: a MemberKey of the same instance
>>> member.description()
'...:Studio::MemberKey(Studio::AdminKey)'
>>> member == admin
True
>>> member.to_admin_key() == admin          # narrowing, by the parent
True
>>> studio.AdminKey.from_any_concept_key(member) == admin    # narrowing from any view
True
>>> studio.MemberKey.create().to_admin_key() is None         # not an Admin
True
```

A parent gives `to_<child>_key()` only when the child is declared in the parent's
namespace, which the parent can name; otherwise narrow with `from_any_concept_key()`.

A club key is built from a member's key, and converts back to each member; the club
`Principal` has `Member` and `Device` as members. A club has no instances of its own, so
its class has no `create()`; with no argument, it gives the invalid key:

```{doctest}
>>> someone = studio.MemberKey.create()
>>> principal = studio.PrincipalKey.from_member_key(someone)
>>> principal == someone, studio.PrincipalKey(someone) == principal
(True, True)
>>> principal.to_member_key() == someone, principal.to_device_key()
(True, None)
>>> studio.PrincipalKey().is_valid()
False
```

An instance of a concept that descends from a member is in the club too: an `Admin` is a
`Member`, so it is a `Principal`.

```{doctest}
>>> studio.PrincipalKey(admin.to_parent_key()) == admin
True
>>> studio.PrincipalKey.from_any_concept_key(admin.to_any_concept_key()).to_member_key() == admin
True
```

A declared container holds keys of exactly its type: convert a key first.

```{doctest}
>>> containers.Set_of_Tuto_UserKey([anyone])
Traceback (most recent call last):
    ...
dsviper.ViperError: ...expected key<Tuto::User>, got key<any_concept>...
>>> containers.Set_of_Tuto_UserKey([tuto.UserKey.from_any_concept_key(anyone)])
{...}
```

Membership is as strict as storing: `in` on a declared container looks an element up as the
type the container holds, and a key of another view raises.

## Attachments and stores

Data does not live in a key: it is attached to it. An attachment is reached through its
unit and the concept it is keyed on, `<unit>.attachments.<Concept>.<attachment>`, and
each operation takes the store it acts on:

```{doctest}
>>> login_of = tuto.attachments.User.login
>>> login_of
AttachmentProxy(attachment<User, Login> Tuto::login)
>>> login_of.runtime_id
438491ed-5518-5d0c-9836-920ee80dd0e8
```

`runtime_id` is a constant that tells which attachment an id names without resolving the
definitions; `descriptor` is the runtime's `dsviper.Attachment`.

**Reading** — `keys`, `has`, `get`, `enumerate` — takes an `AttachmentGetting` (a state's or
a mutable state's `attachment_getting()`) or a `Database`. `get` returns the document as an
optional, which is a copy: write it back with `set`.

### On a `Database`

A `Database` holds the current state. Extend it with the model once, then `set` and `delete`
write directly, inside a transaction:

```{doctest}
>>> db = dsviper.Database.create_in_memory()
>>> _ = db.extend_definitions(model.definitions())
>>> alice, bob = tuto.UserKey.create(), tuto.UserKey.create()

>>> db.begin_transaction()
>>> login_of.set(db, alice, tuto.Login(nickname="alice"))
True
>>> login_of.set(db, bob, tuto.Login(nickname="bob"))
True
>>> db.commit()

>>> login_of.has(db, alice), len(login_of.keys(db))
(True, 2)
>>> login_of.get(db, alice).unwrap().nickname
'alice'
>>> sorted(document.nickname for _key, document in login_of.enumerate(db))
['alice', 'bob']

>>> db.begin_transaction()
>>> login_of.delete(db, bob)
True
>>> db.commit()
>>> login_of.get(db, bob)
nil
```

(`delete` and not `del`, which is Python's keyword.)

A `Database` writes whole documents. To change one field, read the document, change the
copy, and write it back:

```{doctest}
>>> document = login_of.get(db, alice).unwrap()
>>> document.password = "n3w"
>>> db.begin_transaction()
>>> login_of.set(db, alice, document)
True
>>> db.commit()
>>> login_of.get(db, alice).unwrap().password
'n3w'
```

The field operations below write one field without reading the document, on a
`CommitDatabase`.

### On a `CommitDatabase`

A `CommitDatabase` keeps every commit. Its writes — `set`, `diff` and the field
operations — go to an `AttachmentMutating`, which a `CommitMutableState` gives
(`attachment_mutating()`). `CommitStateBuilder.initial_state(db)` starts the first commit,
`CommitStateBuilder.state(db, commit_id)` carries on from a commit; nothing is stored until
the state is committed with `db.commit_mutations(label, state)`:

```{doctest}
>>> cdb = dsviper.CommitDatabase.create_in_memory()
>>> _ = cdb.extend_definitions(model.definitions())

>>> state = dsviper.CommitMutableState(dsviper.CommitStateBuilder.initial_state(cdb))
>>> login_of.set(state.attachment_mutating(), alice, tuto.Login(nickname="alice"))
>>> login_of.set_password(state.attachment_mutating(), alice, "s3cret")   # a field operation
>>> first = cdb.commit_mutations("Register alice", state)

>>> state = dsviper.CommitMutableState(dsviper.CommitStateBuilder.state(cdb, first))
>>> login_of.set_nickname(state.attachment_mutating(), alice, "alice2")
>>> second = cdb.commit_mutations("Rename alice", state)
```

Every commit stays readable — a past state is built the same way:

```{doctest}
>>> def nickname_at(commit_id):
...     past = dsviper.CommitStateBuilder.state(cdb, commit_id)
...     return login_of.get(past.attachment_getting(), alice).unwrap().nickname
>>> nickname_at(first), nickname_at(second)
('alice', 'alice2')
```

On disk, `dsviper.CommitDatabase.create(path)` makes the file and `extend_definitions` puts
the model in it. The definitions persist in the file: a database reopened with
`dsviper.CommitDatabase.open(path)` already carries them, and needs no second
`extend_definitions`:

```{doctest}
>>> import os, tempfile
>>> path = os.path.join(tempfile.mkdtemp(), "users.cdb")
>>> ondisk = dsviper.CommitDatabase.create(path)
>>> _ = ondisk.extend_definitions(model.definitions())
>>> state = dsviper.CommitMutableState(dsviper.CommitStateBuilder.initial_state(ondisk))
>>> login_of.set(state.attachment_mutating(), alice, tuto.Login(nickname="alice"))
>>> _ = ondisk.commit_mutations("Register alice", state)
>>> ondisk.close()

>>> reopened = dsviper.CommitDatabase.open(path)
>>> latest = dsviper.CommitStateBuilder.state(reopened, reopened.last_commit_id())
>>> login_of.get(latest.attachment_getting(), alice).unwrap().nickname
'alice'
>>> reopened.close()
```

A `Database` works the same way, with `dsviper.Database.create(path)` and
`dsviper.Database.open(path)`.

A field operation on a key that holds no document does nothing and raises nothing: set the
document first.

```{doctest}
>>> state = dsviper.CommitMutableState(dsviper.CommitStateBuilder.state(cdb, second))
>>> login_of.set_nickname(state.attachment_mutating(), bob, "nobody")
>>> login_of.has(state.attachment_getting(), bob)
False
```

The field operations are typed methods named after the field: `set_<field>` for every
field, and for a collection field `union_<field>`, `subtract_<field>` (set, map),
`update_<field>` (map), `insert_<field>`, `remove_<field>` (xarray). A `Database` has no
`AttachmentMutating`, so `diff` and the field operations belong to a commit database; and
`delete` belongs to a `Database`, a commit never removing a key. `diff_keys(current, other)`
compares two states.

The commit model itself — heads, history, merges — is the {doc}`../commit/index`
subsystem's.

### With a `CommitStore`

A `CommitStore` keeps that thread for an application: `dispatch(label, callable, *args)`
runs the callable against a fresh mutable state — it receives the `AttachmentMutating` —
and commits what it wrote; `undo` and `redo` move along the dispatches:

```{doctest}
>>> app = dsviper.CommitStore()
>>> app.use(cdb)
>>> app.dispatch("Rename alice", lambda m: login_of.set_nickname(m, alice, "alice3"))
>>> login_of.get(app.attachment_getting(), alice).unwrap().nickname
'alice3'
>>> app.undo()
>>> login_of.get(app.attachment_getting(), alice).unwrap().nickname
'alice2'
>>> app.redo()
>>> login_of.get(app.attachment_getting(), alice).unwrap().nickname
'alice3'
```

## The bridge to the runtime

`p.unwrap_value()` gives the Viper value a generated object wraps, and `Cls.wrap_value(value)`
boxes a value of exactly that type — both without copying, so a change made through one
shows in the other:

```{doctest}
>>> login = tuto.Login(nickname="grace")
>>> value = login.unwrap_value()
>>> value
{nickname='grace', password=''}
>>> same = tuto.Login.wrap_value(value)
>>> same.nickname = "heidi"
>>> login.nickname
'heidi'
```

Every runtime feature — encoding, JSON, a hexdigest — is called on that value. Bytes are
written with `dsviper.Value.encode` and read back with `dsviper.Value.decode`, where
`encoded=False` asks for the Viper value rather than natives:

```{doctest}
>>> blob = dsviper.Value.encode(login.unwrap_value())
>>> back = tuto.Login.wrap_value(
...     dsviper.Value.decode(blob, tuto.Login.type(), model.definitions(), encoded=False))
>>> back == login
True
```

`Cls.type()` is the runtime type of a generated class, container classes included
(`containers.Set_of_Tuto_UserKey.type()`).

## Errors

The package follows the binding's three layers, and leaves the checking to the runtime.

**An argument of another kind** — a Viper value of another type, a key of another concept —
given to `wrap_value` or to a constructor raises `TypeError`:

```{doctest}
>>> tuto.Login.wrap_value(tuto.Identity().unwrap_value())
Traceback (most recent call last):
    ...
TypeError: this value is not a Tuto::Login
>>> tuto.UserKey(tuto.Identity())
Traceback (most recent call last):
    ...
TypeError: ... is not a Tuto::UserKey: widen it with to_parent_key(), or narrow it with from_any_concept_key()
```

An unknown keyword given to a constructor is a `TypeError` too, and so is a generated object
given as its source (see [Structures](#structures)).

**Content that does not fit** the type, native or generated, in a field, a container or an
attachment, is refused by the runtime with `dsviper.ViperError`, naming the element at
fault:

```{doctest}
>>> tuto.Login().nickname = 42
Traceback (most recent call last):
    ...
dsviper.ViperError: ...expected type 'str', got 'int'...
>>> db.begin_transaction()
>>> login_of.set(db, alice, tuto.Identity())
Traceback (most recent call last):
    ...
dsviper.ViperError: ...expected Tuto::Login, got Tuto::Identity...
>>> db.rollback()
```

**An operation the runtime refuses** raises `dsviper.ViperError` as well — `unwrap()` of a
nil optional, `remove` of an element a vector does not hold:

```{doctest}
>>> containers.Optional_of_Tuto_Login().unwrap()
Traceback (most recent call last):
    ...
dsviper.ViperError: ...Try to unwrap empty optional<Tuto::Login>...
```

**A read keeps Python's names**: `IndexError` past the end, `KeyError` for a missing map key
(and a set's `remove` of an element it does not hold), `ValueError` for an unknown case name
or a variant read as an alternative it does not hold:

```{doctest}
>>> containers.Set_of_Tuto_UserKey()[0]
Traceback (most recent call last):
    ...
IndexError: ...
>>> tuto.Status.from_str("archived")
Traceback (most recent call last):
    ...
ValueError: 'archived' is not a valid Status
```

## Pools

A function pool is a subpackage of its own, imported by its path. Neither Tuto nor Studio
declares one; the laboratory's `service` model declares `Tools` (plain functions) and
`PlayerModel` (functions over an attachment):

```text
function_pool Tools { int64 add(int64 a, int64 b); Vector3 addVector(Vector3 a, Vector3 b); … };
attachment_function_pool PlayerModel {
    mutable key<Player> create(string nickname, Level level);
    optional<key<Player>> hasPlayer(string nickname);
};
```

The package calls a pool only through a service: its `Remote`, over a
`dsviper.ServiceRemote` connected to a running server (the {doc}`../services/services` page
says how the laboratory starts one). `is_available()` says whether the service carries the
pool:

```python
import dsviper
import service
import service.tools
import service.player_model
from service import demo

remote = dsviper.ServiceRemote.connect("localhost", "54328", dsviper.Definitions())

tools = service.tools.Remote(remote)
if tools.is_available():
    tools.add(32, 10)                                              # 42
    tools.add_vector(demo.Vector3(x=1, y=2, z=3), demo.Vector3(x=10, y=20, z=30))
```

An attachment function takes the state its parameter type names: an `AttachmentMutating`
for a `mutable` function, an `AttachmentGetting` for one that only reads. The state must
know the model — one built over the package's `definitions()`, over the `dsviper.Definitions`
given to `connect` (which `connect` fills with the service's model; pass its `const()`),
or a commit database extended with it; over other definitions a call fails on an
unregistered attachment. The service
reads and writes that state in place, and nothing is stored until it is committed:

```python
players = service.player_model.Remote(remote)
state = dsviper.CommitMutableState(dsviper.CommitState(service.definitions()))

key = players.create(state.attachment_mutating(), "zoe", demo.Level.EXPERT)
players.has_player(state.attachment_getting(), "zoe").unwrap() == key   # True
demo.attachments.Player.property.get(state.attachment_getting(), key).unwrap().nickname
```

Each pool module also holds a local `Pool` (with its `NAME` and `UUID`), over a
`dsviper.FunctionPool` or `dsviper.AttachmentFunctionPool`: that pool comes from a C++ host
application exposing its functions to an embedded Python — the wheel cannot build one. Where
services come from is the {doc}`../services/index` chapter's subject.
