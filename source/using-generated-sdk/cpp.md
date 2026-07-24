# C++

You defined a data model in DSM and ran Kibo over it. For C++, what you get back is
not a wrapper library — it is **native C++ value types** (`struct`s, `enum class`es,
STL containers) plus the generated machinery that links them to the Viper C++
runtime. You write ordinary, value-semantic C++; the generated code crosses to the
dynamic runtime for you.

This page is that surface, end to end. For *why* the generated code exists (the
adapter/Dual Reality pattern), see {doc}`../kibo-template-viper/index`; for the
persistence model, see {doc}`../commit/index`. The runtime it links against is Viper
C++ (commercial).

```{note}
In the examples, `App` stands for your project name (the `-n` passed to Kibo) and
`Tuto` is the DSM namespace.
```

## Anatomy of the generated C++

C++ is generated **per feature**, not as one importable package: each Kibo run emits
a header/implementation pair, and you link the ones you need into your application.

```text
<App>_Data.hpp / .cpp          ← the types: struct / enum class / key, in namespace Tuto
<App>_Attachments.hpp / .cpp   ← the verbs: get / set / enumerate, in namespace App::Tuto::Attachments
<App>_ValueEncoder.hpp / .cpp  ← static C++ → dynamic Viper::Value
<App>_ValueDecoder.hpp / .cpp  ← dynamic Viper::Value → static C++
<App>_ValueType.hpp / .cpp     ← Viper type handles (plumbing)
```

Two namespaces divide the work: your **value types** land in the DSM namespace
(`Tuto::Login`, `Tuto::UserKey`), the **machinery** in your project namespace
(`App::Tuto::Attachments::…`, `App::ValueEncoder`, `App::ValueDecoder`). Every file
carries a "Do not edit by hand." header — it is a build artifact, regenerated on
every model change.

Unlike Python and Node, C++ has a **lexical namespace**, so the DSM namespace becomes
a real `namespace Tuto`, not a `Tuto_` symbol prefix.

## Two representations, one bridge

This is where C++ differs most from the Python and Node SDKs. There, a proxy object
*holds* the runtime value (`vpr_value` / `vprValue`) — one value seen through a typed
view. In C++ there are **two genuinely separate representations**:

- **Developer Reality** — native C++ value types: `Tuto::Login`, `Tuto::Status`,
  `std::set<Tuto::UserKey>`, `std::optional<Tuto::Login>`. Value semantics, RAII,
  operators, zero wrapper overhead.
- **Runtime Reality** — `Viper::Value` (dynamic, `shared_ptr`, metadata-driven), what
  the engine stores and manipulates.

The bridge between them is the generated `ValueEncoder` / `ValueDecoder` — the
{term}`Dual Reality` made concrete:

```cpp
std::shared_ptr<Viper::ValueStructure> v = App::ValueEncoder::encode(login);  // static → dynamic
Tuto::Login back = App::ValueDecoder::decode_Tuto_Login(v);                    // dynamic → static
```

`encode` is **overloaded** on its argument (`encode(Tuto::Login const&)`,
`encode(std::optional<Tuto::Login> const&)`, `encode(bool)`, …); `decode` is a
**named function per type** (`decode_Tuto_Login`, `decode_bool`, …), because C++
cannot overload on return type.

You rarely call them yourself: the attachment and database verbs take and return
native types and cross the bridge internally. You reach for `encode` / `decode`
explicitly only when you need a raw `Viper::Value` — serialization, RPC, or dynamic
interop. So there is no "don't reach for `vpr_value`" rule here; the discipline is
simply to know which side of the bridge you are on and to cross it deliberately.

## Living in the value types

### Keys — concepts and clubs

A concept or club becomes a value class. A key is an identity, not data:

```cpp
auto user = Tuto::UserKey::create();   // a fresh identity
user.instanceId();                      // its UUId
user.description();                     // "<uuid>:Tuto::UserKey"
user == other;                          // value comparison (operator==)
```

Keys are hashable and ordered (`hash()`, `operator<`), so they drop straight into
`std::set<Tuto::UserKey>` or `std::map<Tuto::UserKey, …>`.

### Structs — plain public members

A struct becomes a value class with public data members and value constructors:

```cpp
Tuto::Login login;
login.nickname = "alice";
login.password = "s3cret";
// or, all at once:
Tuto::Login other{"bob", "hunter2"};

login == other;                         // value equality, generated
```

### Enums — `enum class`

```cpp
Tuto::Account account{Tuto::Status::active};
account.state = Tuto::Status::pending;
```

### Containers — the STL, directly

`vector` / `set` / `map` / `optional` map to their STL counterparts —
`std::vector`, `std::set`, `std::map`, `std::optional` — parameterized by the value
type. There is no proxy collection to learn: you use the STL type the generated API
hands you.

```cpp
std::set<Tuto::UserKey> keys = /* … from an attachment … */;
for (Tuto::UserKey const & k : keys) {
  // …
}
```

## Mutating: calling an attachment verb

Data hangs off a key as **attachments**. Each attachment generates a namespace of
verbs — `set`, per-field `set<Field>`, `get`, `keys`, `diff` — taking native types
and a state drawn from a `CommitDatabase` (see {doc}`../commit/index`).

### Write, then commit

```cpp
using namespace App::Tuto::Attachments;   // brings User_Login, User_Account, … into scope

auto db = CommitDatabase::open("model.cdb");

auto user = Tuto::UserKey::create();
Tuto::Login login{"alice", "s3cret"};

auto state = CommitMutableState::make(CommitStateBuilder::initialState(db));
User_Login::set(state->attachmentMutating(), user, login);
User_Login::setNickname(state->attachmentMutating(), user, "alice2");   // fine-grained
db->commitMutations("Register alice", state);
```

The verbs take native `Tuto::Login` and `std::string` — the encode step is internal.

### Read

```cpp
auto s = CommitMutableState::make(
    CommitStateBuilder::state(db, db->lastCommitId().value()));
auto getting = s->attachmentGetting();

std::set<Tuto::UserKey> users = User_Login::keys(getting);
if (std::optional<Tuto::Login> maybe = User_Login::get(getting, user)) {
  std::cout << maybe->nickname << '\n';   // "alice2"
}
```

`get` returns a `std::optional<Tuto::Login>` — a native value, already decoded.

The mental model is uniform: **a verb is a free function in the attachment's
namespace, taking a getting/mutating handle, a key, and (for setters) a native
value.** A `DatabaseAttachments` feature offers the same verbs against a plain,
non-commit `Viper::Database`.

## Reading a repro

Because every generated name is mechanical, an error written in generated symbols
maps straight back to your model:

- **`Tuto::Login`** → type `Login` in `namespace Tuto` → the `Data` header, and the
  DSM line `struct Login { … }`.
- **`App::Tuto::Attachments::User_Login::set`** → project `App`, namespace `Tuto`,
  attachment `login` on key concept `User`, verb `set` → the DSM line
  `attachment<User, Login> login;`.
- **`App::ValueDecoder::decode_Tuto_Login`** → the decoder that turns a runtime
  `Viper::ValueStructure` back into a `Tuto::Login`.

From there:

1. The generated file says **"Do not edit by hand."** The defect is upstream — in the
   DSM model, or in the template — never a patch to the output.
2. Regenerate after any model change (per feature, `kibo -c cpp -t cpp/<Feature>`);
   the generated code is a build artifact and a stale copy will lie about the model.

That legibility is the payoff of the generated layer: the names you debug are the
names you declared.
