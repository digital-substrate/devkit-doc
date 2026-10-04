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

The examples are doctests, run against the package generated from this small model:

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

The infrastructure name (Kibo's `-n`) is `model`, so the package is `model`. Tuto has no
nested structure, no container field, no concept inheritance, no club and no pool; where a
feature needs one, the example uses the `features` model of the generator's laboratory,
[devkit-codegen-test](https://github.com/digital-substrate/devkit-codegen-test) — a
namespace `Demo` with `concept ConceptC is a ConceptB;`, a club `Klub` whose members are
`ConceptC` and `ConceptD`, and structures `StructureS`, `StructureT`, `StructureU`,
`StructureV` — and says so. Those snippets assume `from features import demo, containers`.

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
| `containers.Set_of_Tuto_UserKey` | a container shape | `set<key<User>>` |
| `tuto.LOGIN` | the runtime id of a type | `struct Login` |

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

In the `features` model, `StructureV` declares `uint8 f_uint8 = 8;`:

```python
v = demo.StructureV()
v.f_uint8                                            # 8
demo.StructureV.type().fields()[1].default_value()   # 8
```

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
- a constructor given a Viper value boxes it, without copying;
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

In the `features` model, `StructureT` holds a `StructureS` field and `StructureU` a
`set<StructureS>`:

```python
t = demo.StructureT()
t.field_structure_s.f_string = "live"       # a field read is live
t.field_structure_s.f_string                # 'live'

s = demo.StructureS(f_string="given")
t.field_structure_s = s                     # a field write keeps s
s.f_string = "after"
t.field_structure_s.f_string                # 'after'

u = demo.StructureU()
u.f_set_s.add(s)                            # a set element is a copy
s.f_string = "not in the set"
u.f_set_s                                   # {{f_float=0.0, f_string='after'}}
```

## Containers

A container is a live view over the Viper container it wraps. The package declares one
class per container shape the model uses — in a structure field, an attachment or a pool —
in `containers`, named `<Kind>_of_<element>`: Tuto's attachments use
`containers.Set_of_Tuto_UserKey` for their keys and `containers.Optional_of_Tuto_Login` for
a read document.

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
| `variant<A, B>` | `Variant_of_A_or_B` | per alternative: `is_A()`, `get_A()`, `set_A()` |
| `tuple<A, B>` | `Tuple_of_A_and_B` | fixed length: `t[i]`, `set(i, e)`, and `get_0()`, `get_1()`, … typed by member |
| `xarray<T>` | `XArray_of_T` | positions that survive concurrent edits: `append`, `insert`, `remove`, `positions`, `position_of`, `disable_position`, … |
| `vec<T, n>` | `Vec<n>_of_T` | fixed length: `v[i]`, `set(i, e)` |
| `mat<T, c, r>` | `Mat<c>x<r>_of_T` | column-major: `m[c, r]`, `m[c]` a column, `at`, `set`; `len` its columns, `size()` its elements |

Every view also has `unwrap_value()`, `copy()`, `==`, `hash()` and `<`, and the sequences
`len`, `in`, `empty()`, `to_list()`.

In the `features` model:

```python
u = demo.StructureU()
u.f_vector.extend([1, 2, 3])                # vector<uint8>
u.f_vector[0]                               # 1
u.f_map_s2["a"] = demo.StructureS()         # map<string, StructureS>
u.f_optional = 4                            # optional<uint8>
u.f_optional.unwrap()                       # 4
u.f_variant.set_uint8(7)                    # variant<string, uint8, StructureS>
u.f_variant.is_uint8(), u.f_variant.get_uint8()   # (True, 7)

v = demo.StructureV()                       # mat<uint8, 2, 3> f_mat = {{1, 2, 3}, {4, 5, 6}}
v.f_mat[1, 2], v.f_mat[1]                   # (6, (4, 5, 6))
len(v.f_mat), v.f_mat.size()                # (2, 6)
```

A container field also takes the host's own collection when nothing in it is generated
(`u.f_vector = [1, 2]`, `u.f_set = {1, 2}`): the runtime decodes it at the line that writes
it. A host collection of generated values is refused with `TypeError`; build its declared
class instead, `containers.Set_of_Demo_StructureS([s1, s2])`, which checks every element
where it is built.

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
the `features` model, `ConceptC` is a `ConceptB`, both in `Demo`, and `Klub` has `ConceptC`
and `ConceptD` as members:

```python
c = demo.ConceptCKey.create()
b = c.to_parent_key()                       # widening: a ConceptBKey of the same instance
b                                           # …:Demo::ConceptBKey(Demo::ConceptCKey)
b.to_concept_c_key() == c                   # narrowing, declared in the parent's namespace
demo.ConceptBKey.create().to_concept_c_key()          # None: not a ConceptC
demo.ConceptCKey.from_any_concept_key(b) == c         # narrowing from any view

k = demo.KlubKey.from_concept_c_key(c)      # a club key, from a member's key
k == c, k.to_concept_c_key() == c, k.to_concept_d_key()   # (True, True, None)
```

A parent gives `to_<child>_key()` only when the child is declared in the parent's
namespace, which the parent can name; otherwise narrow with `from_any_concept_key()`. A club
key is built from a member's key (`demo.KlubKey(c)` too); it has no `create()`, since a club
has no instances of its own.

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

An unknown keyword given to a constructor is a `TypeError` too.

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

A function pool is a subpackage of its own, imported by its path. Tuto declares none; the
laboratory's `service` model declares `Tools` (plain functions) and `PlayerModel` (functions
over an attachment):

```text
function_pool Tools { int64 add(int64 a, int64 b); Vector3 addVector(Vector3 a, Vector3 b); … };
attachment_function_pool PlayerModel {
    mutable key<Player> create(string nickname, Level level);
    optional<key<Player>> hasPlayer(string nickname);
};
```

A client calls a pool through a service with its `Remote`, over a `dsviper.ServiceRemote`;
`is_available()` says whether the service carries the pool:

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
know the model — one built over the package's `definitions()`, or a commit database extended
with it; over other definitions a call fails on an unregistered attachment. The service
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
