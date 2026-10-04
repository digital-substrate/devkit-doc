# C++

You defined a data model in DSM and ran Kibo over it with the
{doc}`kibo-template-viper <../kibo-template-viper/index>` pack. For C++, what you get
back is not a wrapper library: it is **C++17 value types** — `struct`s, `enum class`es,
key classes, STL containers — and the generated code that crosses them to the Viper C++
runtime. You write ordinary, value-semantic C++; the codec and the attachments cross to the
runtime's dynamic `Viper::Value` for you.

The generated C++ is the pack's base reference: the {doc}`Python <python>` and
{doc}`TypeScript <node>` packages offer what it offers, with its restrictions. Producing it
is {doc}`kibo-project <../kibo/kibo-project>`'s job, and which files a project renders is
the feature selection described in {doc}`../kibo-template-viper/features`. The runtime it
links against is Viper C++ (commercial) on its 1.2 line, with its static layer
(`Viper_StaticType`, `Viper_StaticWriter`, `Viper_StaticReader`, `Viper_StaticHash`).

The examples use the `features` model of the generator's laboratory,
[devkit-codegen-test](https://github.com/digital-substrate/devkit-codegen-test), whose
infrastructure name (Kibo's `-n`) is `features`. It declares one namespace, `Demo`:

```text
namespace Demo {
concept ConceptA;
concept ConceptB;
concept ConceptC is a ConceptB;
concept ConceptD;
club Klub;                         // members: ConceptC, ConceptD
enum EnumerationE { a, b, c };
struct StructureS { float f_float; string f_string; };
struct StructureV { uint8 f_uint8 = 8; string f_string = "Forty Two"; set<uint8> f_set = {1, 2, 3}; … };
attachment<ConceptA, StructureV> properties;
…
};
```

## What is generated

A DSM namespace is a **unit**: a file-name prefix and a C++ namespace inside the
infrastructure's. `Demo` in the infrastructure `features` gives `features_demo_data.hpp`
and `namespace features::demo`, so two namespaces of one model may declare the same name.
Which files are rendered depends on the features a project selects:

| Feature | Files | What they hold |
|---|---|---|
| `Base` | `<ns>_<unit>_data`, `_model`, `_codec`, `<ns>_codec`, `<ns>_any_concept`, `<ns>_resources` | structures, enumerations, keys; their identity in the definitions; the codec to a `Viper::Value` |
| `Fields` | `<ns>_<unit>_fields` | every field's name and path, for code that goes through the dynamic API |
| `Attachments` | `<ns>_<unit>_attachments` | one scope per attachment, its operations |
| `Pool` | `<ns>_<pool>_pool` | the functions an application implements, and the pool it exposes |
| `PoolRemote` | `<ns>_<pool>_remote` | the same pool, called through a service |

Every file starts with a header naming the generator, the templates and the runtime, and
says *Do not edit by hand*: it is a build artifact, regenerated on every model change. A
defect in it is fixed in the DSM model or in the templates, never in the output.

The examples below include:

```cpp
#include "features_codec.hpp"              // the codec, for every namespace of the model
#include "features_demo_attachments.hpp"
#include "Viper_CommitDatabase.hpp"
#include "Viper_CommitMutableState.hpp"
#include "Viper_CommitState.hpp"
#include "Viper_CommitStateBuilder.hpp"
#include "Viper_CommitStore.hpp"
#include "Viper_Database.hpp"

using namespace features;
```

## Structures and enumerations

A structure is a `struct` with public fields, a default constructor and a constructor
taking every field in declaration order; a one-field structure converts from its field.
A new structure holds the model's defaults — the default a field declares, or else the
default of its type:

```cpp
demo::StructureS s(1.5f, "hello");           // every field, in declaration order
demo::StructureS empty;                      // {0.0, ""}
s.f_string = "world";

demo::StructureV v;
v.f_uint8;                                   // 8, declared in the model
v.f_set;                                     // std::set<std::uint8_t>{1, 2, 3}
```

Copying copies. Equality and order are generated (`==`, `!=`, `<`), and so is a
`std::hash` specialization, over the runtime's static hash:

```cpp
bool const same{s == demo::StructureS{1.5f, "world"}};
bool const before{empty < s};
std::size_t const h{std::hash<demo::StructureS>{}(s)};
```

An enumeration is an `enum class` whose enumerators are the DSM cases, capitalized:
`demo::EnumerationE::A`, `B`, `C`.

The types map to C++ as you would write them: `std::string`, the fixed-width integers,
`std::vector`, `std::set`, `std::map`, `std::optional`, `std::tuple`, `std::variant`,
`std::array` for a `vec` and an array of columns for a `mat`, `Viper::XArray` for an
`xarray`, `Viper::Any` for an `any`, `Viper::UUId`, `Viper::Blob`.

## The codec

A value crosses to a `Viper::Value` through the codec, which copies, and back:

```cpp
auto const value{codec::encode(s)};                          // a Viper::ValueStructure
auto const back{codec::decode<demo::StructureS>(value)};     // equal to s
auto const definitions{codec::definitions()};                // the model, as the runtime knows it
```

`encode` takes any generated type and any container of them; `decode<T>` checks the value's
type and throws a `Viper::Error` when it is not `T`. JSON, XML and a hexdigest are one
runtime call on what `encode` returns: the pack generates the bridge, not what composes it
with a runtime feature. The binary form is the runtime's static layer — `write(w, v)` on a
`Viper::StaticWriter::Writer`, `read(r, tag<T>{})` on a `Viper::StaticReader::Reader`, found
by argument-dependent lookup.

## Keys

A concept or a club gives a `final` key class: an instance id and the runtime id of the
instance's concept. `create()` mints a fresh instance, and the default constructor gives
the invalid key:

```cpp
auto const a{demo::ConceptAKey::create()};
demo::ConceptAKey const invalid;
a.isValid();                                 // true
invalid.isValid();                           // false
a.instanceId();                              // a Viper::UUId
```

Keys are values — `==`, `<`, `std::hash` — so they go into `std::set`, `std::map` and
`std::unordered_set` as they are.

A child key widens to its parent's by an implicit conversion or `toParentKey()`, and a
parent key narrows with `Child::from(anyConceptKey)`, or `parent.asChildKey()` for a
child declared in the parent's namespace, which the parent can name. A club key converts
from a member's key and narrows to each member the same way. Every key gives `toAny()`,
also named `toAnyConceptKey()`:

```cpp
auto const c{demo::ConceptCKey::create()};
demo::ConceptBKey const b{c};                                 // widening, implicit
demo::ConceptBKey const parent{c.toParentKey()};              // widening, named
std::optional<demo::ConceptCKey> const child{b.asConceptCKey()};          // narrowing
std::optional<demo::ConceptCKey> const fromAny{demo::ConceptCKey::from(b.toAny())};

demo::KlubKey const klub{c};                                  // a club key, from a member's
std::optional<demo::ConceptDKey> const notD{klub.asConceptDKey()};       // std::nullopt

AnyConceptKey const anyone{c.toAnyConceptKey()};
bool const sameInstance{anyone == b.toAny()};                 // true
```

A narrowing answers `std::nullopt` when the instance is not one of the target concept.

## Attachments

An attachment is a scope, `<ns>::<unit>::attachments::<Concept>::<attachment>`:

- `get`, `has`, `keys` take any `std::shared_ptr<Viper::AttachmentGetting>` — a
  `Viper::Database`, a `Viper::CommitState`, a `Viper::CommitMutableState` are ones;
- `set`, `diff` and the field operations take a `Viper::AttachmentMutating`;
- `set` and `del` also take a `Viper::Database`, inside a transaction.

`runtimeId` is the attachment's runtime id, a constant, and `descriptor()` the runtime's
`Viper::Attachment`.

On a `Viper::Database`, extended with the model once:

```cpp
namespace properties = demo::attachments::ConceptA::properties;

auto const db{Viper::Database::createInMemory()};
db->extendDefinitions(codec::definitions());
auto const key{demo::ConceptAKey::create()};

db->beginTransaction(Viper::DatabaseTransactionMode::Deferred);
properties::set(db, key, demo::StructureV{});
db->commit();

std::optional<demo::StructureV> const document{properties::get(db, key)};
std::set<demo::ConceptAKey> const stored{properties::keys(db)};

db->beginTransaction(Viper::DatabaseTransactionMode::Deferred);
properties::del(db, key);
db->commit();
```

On a `Viper::CommitDatabase`, the writes go to a `Viper::CommitMutableState` — built from
`CommitStateBuilder::initialState(db)` for the first commit, `CommitStateBuilder::state(db,
commitId)` to carry on — and are stored once it is committed:

```cpp
auto const cdb{Viper::CommitDatabase::createInMemory()};
cdb->extendDefinitions(codec::definitions());

auto state{Viper::CommitMutableState::make(Viper::CommitStateBuilder::initialState(cdb))};
properties::set(state, key, demo::StructureV{});
properties::setF_string(state, key, "v1");                   // a field operation
properties::unionF_set(state, key, {7});
auto const v1{cdb->commitMutations("First version", state)};

state = Viper::CommitMutableState::make(Viper::CommitStateBuilder::state(cdb, v1));
properties::setF_string(state, key, "v2");
auto const v2{cdb->commitMutations("Second version", state)};

auto const past{Viper::CommitStateBuilder::state(cdb, v1)};  // every commit stays readable
std::string const first{properties::get(past, key)->f_string};   // "v1"
```

The field operations are named after the field: `set<Field>` for every field, and for a
collection field `union<Field>`, `subtract<Field>` (set, map), `update<Field>` (map),
`insert<Field>`, `remove<Field>` (xarray). A field operation on a key that holds no document
does nothing: set the document first. A `Viper::CommitStore` keeps that thread for an
application, with undo and redo:

```cpp
auto const store{Viper::CommitStore::make()};
store->use(cdb);
store->dispatch("Third version", [&](std::shared_ptr<Viper::AttachmentMutating> const & mutating) {
    properties::setF_string(mutating, key, "v3");
});
store->undo();
```

The commit model itself — heads, history, merges — is the {doc}`../commit/index`
subsystem's.

## Pools

A function pool is a namespace, `<ns>::<pool>`. The laboratory's `service` model (the
infrastructure `service`) declares `Tools`:

```text
function_pool Tools { int64 add(int64 a, int64 b); Vector3 addVector(Vector3 a, Vector3 b); … };
```

With the `Pool` feature, the application implements the functions in that namespace, and
`pool()` returns the `Viper::FunctionPool` it exposes; `poolName` and `poolId` name it:

```cpp
#include "service_tools_pool.hpp"

namespace service::tools {

std::int64_t add(std::int64_t a, std::int64_t b) {
    return a + b;
}

demo::Vector3 addVector(demo::Vector3 const & a, demo::Vector3 const & b) {
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}

// … every function the pool declares

} // namespace service::tools

std::shared_ptr<Viper::FunctionPool> const exposed{service::tools::pool()};
```

With the `PoolRemote` feature, a client calls the same pool through a service, with
`Remote` over a `Viper::ServiceRemote`; it links without the functions only a server
implements. An attachment function takes an `AttachmentMutating` when it is `mutable`, an
`AttachmentGetting` when it only reads:

```cpp
#include "service_codec.hpp"
#include "service_tools_remote.hpp"
#include "service_player_model_remote.hpp"
#include "Viper_CommitMutableState.hpp"
#include "Viper_CommitState.hpp"

auto const remote{Viper::ServiceRemote::connect("localhost", "54328", Viper::Definitions::make())};
service::tools::Remote const tools{remote};
if (tools.isAvailable()) {
    std::int64_t const sum{tools.add(32, 10)};            // 42
}

service::player_model::Remote const players{remote};
auto const state{Viper::CommitMutableState::make(Viper::CommitState::make(service::codec::definitions()))};
auto const player{players.create(state, "zoe", service::demo::Level::Expert)};
std::optional<service::demo::PlayerKey> const found{players.hasPlayer(state, "zoe")};
```

Most projects do not expose their pools as a service; where services come from is the
{doc}`../services/index` chapter's subject.
