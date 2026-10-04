# TypeScript

You defined a data model in DSM and ran Kibo over it with the
{doc}`kibo-template-viper <../kibo-template-viper/index>` pack. What you got back — and
what you work against every day — is a typed ES module package over the
[`@digitalsubstrate/dsviper`](https://www.npmjs.com/package/@digitalsubstrate/dsviper) Node
binding. This page is that daily surface, end to end: what the package holds, how its
objects behave, how documents are stored, how to cross to the runtime, and what is thrown
when something does not fit.

Producing the package is {doc}`kibo-project <../kibo/kibo-project>`'s job, building and
publishing it is described in {doc}`../kibo-template-viper/node`, and the raw runtime the
package delegates to is the {doc}`dsviper for Node <../dsviper-node/index>` chapter. The
TypeScript surface is the {doc}`Python <python>` one in another idiom;
{doc}`../kibo-template-viper/parity` lists where the two differ.

The examples use the `features` model of the generator's laboratory,
[devkit-codegen-test](https://github.com/digital-substrate/devkit-codegen-test), whose
infrastructure name is `features`. It declares one namespace, `Demo`:

```text
namespace Demo {
concept ConceptA;
concept ConceptB;
concept ConceptC is a ConceptB;
concept ConceptD;
club Klub;                         // members: ConceptC, ConceptD
enum EnumerationE { a, b, c };
struct StructureS { float f_float; string f_string; };
struct StructureT { string field_string; StructureS field_structure_s; };
struct StructureU { uint8 f_uint8; int64 f_int64; vector<uint8> f_vector; … };   // every type
struct StructureV { uint8 f_uint8 = 8; string f_string = "Forty Two"; … };       // with defaults
attachment<ConceptA, StructureV> properties;
…
};
```

## The package

```text
features/
├── package.json, tsconfig.json  ← the Package feature: `tsc -p .` builds src/ into dist/
└── src/
    ├── index.ts                 ← definitions(), AnyConceptKey, AnyValue, Key, the containers,
    │                              and each unit as a namespace: demo
    ├── containers.ts            ← one class per container shape the model uses
    ├── demo/                    ← one directory per DSM namespace: Demo is demo
    │   ├── data.ts              ← structures, enumerations, keys, and their runtime ids
    │   └── attachments.ts       ← one class per concept, one accessor per attachment
    ├── pools.ts, <pool>/        ← the function pools (the Pool feature)
    ├── _codegen/                ← the runtime every generated package carries
    └── resources.ts             ← the model's definitions, embedded
```

Every file starts with a header naming the generator, the templates and the runtime range
(`@digitalsubstrate/dsviper >=1.2.14 <1.3.0`), and says *Do not edit by hand*: the package
is a build artifact, regenerated on every model change. A defect in it is fixed in the DSM
model or in the templates, never in the output.

The entry point exports the units, the containers and the model's definitions; the package
also exports every unit directory (`features/demo`) and the pools (`features/pools`):

```ts
import dsviper from "@digitalsubstrate/dsviper";
import { definitions, demo, AnyConceptKey, Vector_of_uint8, Set_of_Demo_StructureS,
         Set_of_Demo_ConceptBKey, Set_of_uint8 } from "features";

const defs: dsviper.DefinitionsConst = definitions();   // the model, decoded once
```

`definitions()` is the model as the runtime knows it: a database is extended with it, and
decoding a value needs it. The entry module's header says where to start, and `_codegen`'s
JSDoc is the reference for the bridge, the containers and the stores.

Names keep the DSM spelling — `f_uint8`, `field_structure_s`, `StructureS` — while
namespaces and pool modules are snake_case (`demo`, `player_model`); a project spells a
name its own way with `[names]` in its `kibo.toml` (see {doc}`../kibo/kibo-project`). A
namespace is a directory, so two namespaces of one model may declare the same name.

### Using it from a project

The package imports `@digitalsubstrate/dsviper`, and so does any code that opens a
database or builds a runtime value. **Both must reach one installation**: make the runtime
a dependency of the project, in the range the package's `package.json` declares, so that
one copy serves both. Two copies of the native binding cannot share a process — the second
one to load stops with a message naming both (`npm ls @digitalsubstrate/dsviper` finds
them).

Type-checking needs the package's own settings — ES modules resolved the Node way, default
imports of the CommonJS binding — as the generated `tsconfig.json` has them:
`"module": "NodeNext"`, `"moduleResolution": "NodeNext"`, `"esModuleInterop": true`,
`"types": ["node"]`, with `"type": "module"` in the project's `package.json`. A bare
`tsc --strict file.ts` uses other defaults and fails on the binding's import.
{doc}`../kibo-template-viper/node` shows a complete project.

## Structures

A structure is constructed from an init object — a generated `<Structure>Init` interface,
one optional member per field — or from a Viper value of its type
(see [Ownership](#ownership)). A field is a get/set accessor:

```ts
const s = new demo.StructureS({ f_float: 1.5, f_string: "hello" });
s.f_string;                        // "hello"
s.f_float = 2.5;
s.toString();                      // "{f_float=2.5, f_string='hello'}"
```

In an init object, an `undefined` member means "not given". The checker flags an unknown
member or a wrong type; at run time an unknown member throws `TypeError`, and a proxy is
not extensible, so assigning a misspelt field throws at the line, in plain JavaScript too.

Equality, hash and order are the runtime's, as methods — `equals`, `hashKey` (a `bigint`
equal for equal values) and `compare` (-1, 0 or 1) — and `copy()` returns an independent
copy:

```ts
const twin = new demo.StructureS({ f_float: 2.5, f_string: "hello" });
s.equals(twin);                    // true
s.hashKey() === twin.hashKey();    // true
[twin, new demo.StructureS()].sort((a, b) => a.compare(b));

const other = s.copy();
other.f_string = "changed";
s.f_string;                        // "hello"
```

### Defaults

A new structure holds the model's defaults: the default a field declares, or else the
default of its type. The declared default is the runtime's, on the structure's type:

```ts
const v = new demo.StructureV();
v.f_uint8;                                         // 8, declared
v.f_string;                                        // "Forty Two", declared
new demo.StructureU().f_uint8;                     // 0, the type's
demo.StructureV.type().fields()[1].defaultValue(); // 8
```

## Enumerations

An enumeration is a union of its case names with a companion object of the same name:

```ts
const e: demo.EnumerationE = demo.EnumerationE.B;  // the constant is "b"
demo.EnumerationE.fromStr("c");                    // "c", spelled as the DSM spells it
demo.EnumerationE.index(e);                        // 1
const viper = demo.EnumerationE.unwrapValue(e);    // a dsviper.ValueEnumeration
demo.EnumerationE.wrapValue(viper);                // "b"
```

A case is a host value, a string: it converts to the runtime's enumeration value with
`unwrapValue` and back with `wrapValue`.

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
- any other copy is explicit: `copy()`, or `new Cls(value.copy())`.

```ts
const t = new demo.StructureT();
t.field_structure_s.f_string = "live";     // a field read is live
t.field_structure_s.f_string;              // "live"

const given = new demo.StructureS({ f_string: "given" });
t.field_structure_s = given;               // a field write keeps `given`
given.f_string = "after";
t.field_structure_s.f_string;              // "after"

const u = new demo.StructureU();
u.f_set_s.add(given);                      // a set element is a copy
given.f_string = "not in the set";
u.f_set_s.toString();                      // "{{f_float=0.0, f_string='after'}}"

const value = given.unwrapValue();
new demo.StructureS(value).f_string = "boxed";          // the same value
given.f_string;                                         // "boxed"
new demo.StructureS(value.copy()).f_string = "copied";  // a copy, asked for
given.f_string;                                         // "boxed"
```

## Containers

A container is a live view over the Viper container it wraps. The package exports one
class per container shape the model uses — in a structure field, an attachment or a pool —
named `<Kind>_of_<element>`: `Vector_of_uint8`, `Set_of_Demo_StructureS`,
`Map_of_string_to_Demo_StructureS`, `Optional_of_Demo_StructureV`,
`Variant_of_string_or_uint8`, `Tuple_of_uint8_and_string`, `XArray_of_uint8`,
`Vec2_of_uint8`, `Mat2x3_of_uint8`. Each kind declares what it does, typed by its element,
so `tsc` refuses a method the kind does not have, a misspelt one and a wrong element:

| DSM | What it does |
|---|---|
| `vector<T>` | `append`, `insert`, `set`, `extend`, `concat`, `pop`, `remove`, `clear`, `count`, `index`, `exchange`, `front`, `back` |
| `set<T>` | sorted: `add`, `remove`, `discard`, `pop`, `popMax`, `extend`, `min`, `max`, `union`, `intersection`, `difference`, `symmetricDifference` and their `…Update` forms, `issubset`, `issuperset`, `isdisjoint` |
| `map<K, V>` | `get` (`undefined` when absent), `at` (throws when absent), `set`, `discard`, `pop`, `popitem`, `setdefault`, `update`, `min`, `max`, `entries` |
| `optional<T>` | `isNil`, `unwrap`, `wrap`, `get(fallback)`, `clear` |
| `variant<A, B>` | per alternative: `isA()`, `getA()`, `setA()` |
| `tuple<A, B>` | `at(i)`, `set(i, e)`, and `get0()`, `get1()`, … typed by member |
| `xarray<T>` | `has`, `index`, `positionOf`, `extend`, `insertPosition`, `disablePosition`, `entries`; `END` and `createPosition()` on its class |
| `vec<T, n>` | `at(i)`, `set(i, e)` |
| `mat<T, c, r>` | column-major: `at(c, r)`, `set(c, r, e)`, `column(c)`, `setColumn(c, …)`; `columns`, `rows`, and `size` its elements |

Every view also has `unwrapValue()`, `copy()`, `equals`, `hashKey`, `compare`, `toJSON`;
the sequences have `size` / `length`, `has`, `toArray` and iterate with `for…of` — a map
iterates its `[key, value]` entries, as a `Map` does.

```ts
const w = new demo.StructureU();
w.f_vector.extend([1, 2, 3]);              // vector<uint8>
w.f_vector.at(0);                          // 1
w.f_map_s2.set("a", new demo.StructureS()); // map<string, StructureS>
w.f_map_s2.get("missing");                 // undefined
w.f_optional = 4;                          // optional<uint8>
w.f_optional.unwrap();                     // 4
w.f_optional.clear();                      // empties the field
w.f_variant.setUint8(7);                   // variant<string, uint8, StructureS>
w.f_variant.isUint8();                     // true
w.f_xarray = [1, 2];                       // xarray<uint8>, from the list of its elements

const defaults = new demo.StructureV();    // mat<uint8, 2, 3> f_mat = {{1, 2, 3}, {4, 5, 6}}
defaults.f_mat.at(1, 2);                   // 6
defaults.f_mat.column(1);                  // [4, 5, 6]
defaults.f_mat.columns;                    // 2
defaults.f_mat.size;                       // 6
```

A container field also takes the host's own collection when nothing in it is generated —
an array, a `Set`, a `Map` or pairs: the runtime decodes it at the line that writes it. A
host collection of generated values is refused with `TypeError`; build its declared class
instead, which checks every element where it is built:

```ts
w.f_vector = [4, 5];
w.f_set_s = new Set_of_Demo_StructureS([new demo.StructureS(), new demo.StructureS({ f_float: 1 })]);
const bytes = new Vector_of_uint8([1, 2, 3]);
```

A shape the model does not use has no class. Build it with the runtime, from Viper values:

```ts
const someKey = demo.ConceptAKey.create();
const keyList = dsviper.Value.create(new dsviper.TypeVector(demo.ConceptAKey.type()),
                                     [someKey.unwrapValue()]);
```

## Keys

A concept or a club gives a key class. A key is an identity, not data — the concept of its
instance and an instance id:

```ts
const a = demo.ConceptAKey.create();              // a fresh instance
a.instanceId();                                   // its dsviper.ValueUUId
a.isValid();                                      // true
new demo.ConceptAKey(a.instanceId()).equals(a);   // true: the key of that instance
new demo.ConceptAKey(a.instanceId().encoded());   // the same, from its string
new demo.ConceptAKey().isValid();                 // false: the invalid key
```

One instance has many views: its own key, its parent's, a club's, the any-concept key.
They are equal (`equals`) and share their `hashKey()` whatever the view. Every conversion is
named and goes through the runtime, which keeps the instance:

```ts
const c = demo.ConceptCKey.create();
const b = c.toParentKey();                         // widening: a ConceptBKey
b.equals(c);                                       // true
b.toConceptCKey();                                 // narrowing: c, or undefined
demo.ConceptCKey.fromAnyConceptKey(b);             // narrowing from any view
demo.ConceptCKey.fromAnyConceptKey(demo.ConceptBKey.create());   // undefined

const klub = demo.KlubKey.fromConceptCKey(c);      // a club key, from a member's key
klub.toConceptCKey();                              // c
klub.toConceptDKey();                              // undefined

const anyone: AnyConceptKey = c.toAnyConceptKey();
anyone.equals(c);                                  // true
```

A parent gives `to<Child>Key()` only when the child is declared in the parent's namespace,
which the parent can name; otherwise narrow with `fromAnyConceptKey()`. A club key is built
from a member's key (`new demo.KlubKey(c)` too). Key classes are nominal: a key of one
concept is not accepted where another is announced.

**A native `Map` or `Set` compares objects by identity**, keys included: two objects for one
instance are two entries. Key a native collection by `hashKey()`, a `bigint` equal for the
keys of one instance whatever the view, or use a declared `Set_of_…` / `Map_of_…`:

```ts
const copyOfA = demo.ConceptAKey.wrapValue(a.unwrapValue().copy());
new Set([a, copyOfA]).size;                        // 2: identity
const names = new Map<bigint, string>([[a.hashKey(), "first"]]);
names.get(copyOfA.hashKey());                      // "first"
names.get(a.toAnyConceptKey().hashKey());          // "first", whatever the view
```

A declared container holds keys of exactly its type — convert a key first, and membership
(`has`) is as strict as storing:

```ts
const parents = new Set_of_Demo_ConceptBKey([c.toParentKey()]);   // not [c]: ViperError
parents.has(c.toParentKey());                                     // true
```

## Attachments and stores

Data does not live in a key: it is attached to it. An attachment is reached through its
unit and the concept it is keyed on, `<unit>.attachments.<Concept>.<attachment>`, and each
operation takes the store it acts on:

```ts
const properties = demo.attachments.ConceptA.properties;
properties.runtimeId;              // a constant: which attachment an id names
properties.descriptor;             // the runtime's dsviper.Attachment
```

**Reading** — `keys`, `has`, `get`, `enumerate` — takes an `AttachmentGetting` (a state's or
a mutable state's `attachmentGetting()`) or a `Database`. `get` returns the document as an
optional, which is a copy: write it back with `set`.

### On a `Database`

A `Database` holds the current state. Extend it with the model once, then `set` and `del`
write directly, inside a transaction:

```ts
const db = dsviper.Database.createInMemory();
db.extendDefinitions(definitions());
const first = demo.ConceptAKey.create();
const second = demo.ConceptAKey.create();

db.beginTransaction();
properties.set(db, first, new demo.StructureV({ f_string: "first" }));    // true
properties.set(db, second, new demo.StructureV({ f_string: "second" }));  // true
db.commit();

properties.has(db, first);                          // true
properties.keys(db).size;                           // 2
properties.get(db, first).unwrap().f_string;        // "first"
for (const [key, document] of properties.enumerate(db)) {
    console.log(key.toString(), document.f_string);
}

db.beginTransaction();
properties.del(db, second);                         // true
db.commit();
properties.get(db, second).isNil();                 // true
```

### On a `CommitDatabase`

A `CommitDatabase` keeps every commit. Its writes — `set`, `diff` and the field
operations — go to an `AttachmentMutating`, which a `CommitMutableState` gives
(`attachmentMutating()`). `CommitStateBuilder.initialState(db)` starts the first commit,
`CommitStateBuilder.state(db, commitId)` carries on from a commit; nothing is stored until
the state is committed with `db.commitMutations(label, state)`:

```ts
const cdb = dsviper.CommitDatabase.createInMemory();
cdb.extendDefinitions(definitions());
const key = demo.ConceptAKey.create();

let state = new dsviper.CommitMutableState(dsviper.CommitStateBuilder.initialState(cdb));
properties.set(state.attachmentMutating(), key, new demo.StructureV({ f_string: "v1" }));
properties.setF_uint8(state.attachmentMutating(), key, 9);                  // a field operation
properties.unionF_set(state.attachmentMutating(), key, new Set_of_uint8([7]));
const v1 = cdb.commitMutations("First version", state);

state = new dsviper.CommitMutableState(dsviper.CommitStateBuilder.state(cdb, v1));
properties.setF_string(state.attachmentMutating(), key, "v2");
const v2 = cdb.commitMutations("Second version", state);

// every commit stays readable
const at = (id: dsviper.ValueCommitId) =>
    properties.get(dsviper.CommitStateBuilder.state(cdb, id).attachmentGetting(), key).unwrap();
at(v1).f_string;                   // "v1"
at(v2).f_string;                   // "v2"
```

A field operation on a key that holds no document does nothing and throws nothing: set the
document first.

The field operations are typed methods named after the field: `set<Field>` for every
field (`setF_uint8`, `setF_string`), and for a collection field `union<Field>`,
`subtract<Field>` (set, map), `update<Field>` (map), `insert<Field>`, `remove<Field>`
(xarray). A `Database` has no `AttachmentMutating`, so `diff` and the field operations
belong to a commit database; and `del` belongs to a `Database`, a commit never removing a
key. `diffKeys(current, other)` compares two states. The commit model itself — heads,
history, merges — is the {doc}`../commit/index` subsystem's.

### With a `CommitStore`

A `CommitStore` keeps that thread for an application: `dispatch(label, callable)` runs the
callable against a fresh mutable state — it receives the `AttachmentMutating` — and commits
what it wrote; `undo` and `redo` move along the dispatches:

```ts
const app = new dsviper.CommitStore();
app.use(cdb);
app.dispatch("Third version", (mutating) => properties.setF_string(mutating, key, "v3"));
properties.get(app.attachmentGetting(), key).unwrap().f_string;   // "v3"
app.undo();
properties.get(app.attachmentGetting(), key).unwrap().f_string;   // "v2"
app.redo();
```

## The bridge to the runtime

`p.unwrapValue()` gives the Viper value a generated object wraps, and `Cls.wrapValue(value)`
boxes a value of exactly that type — both without copying, so a change made through one
shows in the other:

```ts
const grace = new demo.StructureS({ f_string: "grace" });
const same = demo.StructureS.wrapValue(grace.unwrapValue());
same.f_string = "heidi";
grace.f_string;                    // "heidi"
```

Every runtime feature — encoding, JSON, a hexdigest — is called on that value. Bytes are
written with `dsviper.Value.encode` and read back with `dsviper.Value.decode`:

```ts
const blob = dsviper.Value.encode(grace.unwrapValue());
const back = demo.StructureS.wrapValue(
    dsviper.Value.decode(blob, demo.StructureS.type(), definitions()));
back.equals(grace);                // true
```

`Cls.type()` is the runtime type of a generated class, container classes included.

## Errors

The package follows the binding's three layers, and leaves the checking to the runtime.

```ts
// An argument of another kind - a Viper value of another type, a key of another
// concept - given to wrapValue or to a constructor: TypeError.
try { demo.StructureS.wrapValue(new demo.StructureT().unwrapValue()); }
catch (error) { console.log(error instanceof TypeError); }        // true

// Content that does not fit the type, native or generated, in a field, a container or an
// attachment: the runtime's ViperError, naming the element at fault.
try { new demo.StructureU().f_uint8 = 300; }
catch (error) { console.log(error instanceof dsviper.ViperError); }   // true

// An operation the runtime refuses: ViperError too.
try { new demo.StructureU().f_vector.remove(99); }
catch (error) { console.log(error instanceof dsviper.ViperError); }   // true

// A variant read as an alternative it does not hold: TypeError.
try { new demo.StructureU().f_variant.getUint8(); }
catch (error) { console.log(error instanceof TypeError); }        // true

// An index past the end: the binding's RangeError named ViperError.
try { new demo.StructureU().f_vector.at(10); }
catch (error) {
    console.log(error instanceof RangeError, (error as Error).name);   // true ViperError
}
```

That last one is not an instance of `dsviper.ViperError`: test it as a `RangeError`. A map's
`at` of a key it does not hold, `unwrap()` of a nil optional and `fromStr` of an unknown case
name throw `ViperError`.

## 64-bit integers

`int64` and `uint64` are `bigint`, as the binding gives them, in fields, documents and pool
arguments; the other integers and the floats are `number`:

```ts
const big = new demo.StructureU();
big.f_int64 = 9007199254740993n;   // past Number.MAX_SAFE_INTEGER, exact
big.f_int64 + 1n;                  // 9007199254740994n
```

## Pools

The function pools are reached through `<package>/pools`, one namespace per pool: the entry
module belongs to the `Base` feature and cannot import what only the `Pool` feature
renders. The laboratory's `service` model declares `Tools` (plain functions) and
`PlayerModel` (functions over an attachment):

```text
function_pool Tools { int64 add(int64 a, int64 b); Vector3 addVector(Vector3 a, Vector3 b); … };
attachment_function_pool PlayerModel {
    mutable key<Player> create(string nickname, Level level);
    optional<key<Player>> hasPlayer(string nickname);
};
```

A client calls a pool through a service with its `Remote`, over a `dsviper.ServiceRemote`;
`isAvailable()` says whether the service carries the pool, and each pool module exports its
`NAME` and `UUID`:

```ts
import dsviper from "@digitalsubstrate/dsviper";
import { definitions, demo } from "service";
import { tools, player_model } from "service/pools";

const remote = dsviper.ServiceRemote.connect("localhost", "54328", new dsviper.Definitions());

const toolsRemote = new tools.Remote(remote);
if (toolsRemote.isAvailable()) {
    toolsRemote.add(32n, 10n);                     // 42n: int64 is bigint
    toolsRemote.addVector(new demo.Vector3({ x: 1, y: 2, z: 3 }),
                          new demo.Vector3({ x: 10, y: 20, z: 30 }));
}

const players = new player_model.Remote(remote);
const state = new dsviper.CommitMutableState(new dsviper.CommitState(definitions()));
const player = players.create(state.attachmentMutating(), "zoe", demo.Level.EXPERT);
players.hasPlayer(state.attachmentGetting(), "zoe").unwrap().equals(player);   // true
demo.attachments.Player.property.get(state.attachmentGetting(), player).unwrap().nickname;
```

An attachment function takes the state its parameter type names: an `AttachmentMutating`
for a `mutable` function, an `AttachmentGetting` for one that only reads. The state must
know the model — one built over the package's `definitions()`, or a commit database
extended with it. The service reads and writes that state in place, and nothing is stored
until it is committed. Where services come from is the {doc}`../services/index` chapter's
subject.
