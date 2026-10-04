# Migrating application code from 1.2

You have code — an application, a script, a service — written by hand against a package that
kibo 1.2 generated, and the project now generates with **kibo 2** and
**kibo-template-viper 2.0**. The generated surface changed throughout, and there are no
compatibility aliases: code that calls the 1.2 names does not run against the 2.0 package
until it is migrated. This page says what moved, why, and in what order to move it, for
Python, TypeScript and C++, and ends with a worked example: a public Python application
migrated from one to the other.

It is about the code that *calls* the generated package. Migrating a template pack is
{doc}`../kibo/migrating`; generating the package is {doc}`../kibo/kibo-project`'s job. The
2.0 surface itself is described on the {doc}`Python <python>`, {doc}`TypeScript <node>` and
{doc}`C++ <cpp>` pages, which this one links to rather than repeats.

## What does not move

The model and the runtime stay. The 2.0 templates target the runtimes of the 1.2 line, with
floors: `dsviper >= 1.2.29`, `@digitalsubstrate/dsviper >= 1.2.14`, and a `viper` C++ runtime
that carries its static layer. Every generated file names its runtime range in its header.

So what an application does with the runtime directly — opening a `Database` or a
`CommitDatabase`, building a `CommitMutableState`, dispatching through a `CommitStore`,
committing — is written as before. The migration touches, for the most part, the lines
that name a generated type, a generated function or a generated module.

## The method

What worked, in this order:

1. **Regenerate** the package with kibo-project, from a `kibo.toml` that replaces the
   project's `generate.py` (see {doc}`../kibo/kibo-project`, *Coming from a generate.py*).
   Remove the 1.2 package first, or generate into a new directory: a 1.2 module left
   lying around still imports, and hides a call not yet migrated.
2. **Fix the imports first.** One module per DSM namespace replaces the flat 1.2 package, so
   every file that imported from it stops at its first line, and a checker cannot check a
   name from a module it cannot find.
3. **Let the type checker drive the rest**, row by row through the tables below: `mypy` for
   Python, `tsc --strict` with the package's settings for TypeScript (see
   {doc}`node`, *Using it from a project*), the compiler for C++. The generated Python is
   fully annotated, its runtime included, and the TypeScript containers are typed by their
   element, so each 1.2 name the 2.0 package no longer has is an error at its line.
4. **Run the application**, and whatever checks its behaviour. A type checker sees names,
   not what a function writes: the proof that the migrated code does what the 1.2 code did
   is a run. The worked example below kept one recording, made from the 1.2 code before the
   migration started, and replayed it on the migrated code.

Do the migration as one change and nothing else. Taking up something 2.0 makes possible — a
host collection where a declared container was built, a different way to read a document —
is a second change, made once the first runs.

## What moved, and why

Six ideas account for nearly every row of the tables. Read them once; the tables are then
mechanical.

**A namespace is a unit.** In 1.2 every type of the model lived in one flat scope and
carried its namespace as a prefix: `Graph_VertexKey`, `Demo_StructureS`. In 2.0 a DSM
namespace is a unit of generated code — a Python module, a TypeScript directory, a C++
namespace and file prefix — and a type no longer carries the prefix: `graph.VertexKey`,
`demo.StructureS`. Two namespaces of one model may now declare the same name. `-n`
(kibo-project's `infrastructure`) names the generated infrastructure — the Python or
TypeScript package, the outer C++ namespace — and the application keeps its own.

**Containers are named by their shape.** A container class is named by its kind and its
elements: `Vector_of_uint8`, `Set_of_Graph_VertexKey`, `Map_of_A_to_B`,
`Variant_of_A_or_B`, `Tuple_of_a_and_b`, `Vec2_of_uint8`, `Mat2x3_of_uint8`. In Python they
live in the package's `containers` module, in TypeScript at the package root. In both, a
container field is a live view over the runtime value, not a copy.

**An attachment is an object.** 1.2 generated one free function per attachment and per
operation, under a composed name: `graph_graph_selection_union_vertex_keys`. 2.0 groups the
attachments of a unit by the concept they are keyed on, and an attachment is an object whose
operations are its methods: `attachments.Graph.selection.union_vertex_keys`. The same object
carries the attachment's `runtime_id` (`runtimeId` in TypeScript and C++), which 1.2 kept in
a separate `AttachmentRuntimeIds` table, and it takes a `Database` as well as a state, which
replaces 1.2's separate `database_attachments` functions.

**The bridge is `wrap_value` / `unwrap_value`.** A generated object is a box around one
Viper value. 1.2 exposed that value as an attribute, `vpr_value` (`vprValue`). 2.0 makes the
crossing a pair of named operations: `p.unwrap_value()` gives the value, `Cls.wrap_value(value)`
boxes one of exactly the class's type, both without copying (see
{doc}`python`, *The bridge to the runtime*). A constructor given a Viper value of its type
boxes it too, as 1.2's `Cls(value)` did; a copy is explicit, `p.copy()`.

**Runtime features go through the bridge.** 1.2 gave every proxy its own `encode`,
`decode`, `hexdigest` and stream `write` / `read`. 2.0 removes them: bytes, JSON, XML and a
hexdigest are one runtime call on the unwrapped value. Python reads bytes back with
`dsviper.Value.decode(blob, Cls.type(), definitions(), encoded=False)`, where
`encoded=False` asks for the Viper value rather than natives, then boxes it with
`wrap_value`. In C++, the codec moves into its own namespace, `<ns>::codec`.

**Static names follow one snake_case rule.** In Python, every static name — fields,
enumeration cases, attachments, modules — goes through kibo's one snake_case rule, which
spells some names with digits differently from 1.2: a field `f_uint_8` in 1.2 is `f_uint8`
in 2.0, `channel_0` is `channel0`, an enumeration case `A_0` is `A0`. Where the rule cannot
know better, a project fixes a name with `[names]` in its `kibo.toml` (see
{doc}`../kibo/kibo-project`). TypeScript keeps the DSM spelling for fields and types and
uses snake_case for modules; C++ uses snake_case for unit and pool namespaces.

## Python

| 1.2 | 2.0 |
|---|---|
| `from pkg.data import *`; `Demo_StructureS`, `Demo_ConceptAKey` | `from pkg import demo`; `demo.StructureS`, `demo.ConceptAKey` |
| `Vector_uint8`, `Set_X`, `Map_A_to_B`, `Optional_X`, `XArray_X`, at the package root | `containers.Vector_of_uint8`, `Set_of_X`, `Map_of_A_to_B`, `Optional_of_X`, `XArray_of_X` |
| `Variant_A_B`, `Tuple_a_b`, `Vec_uint8_2`, `Mat_uint8_2_3` | `containers.Variant_of_A_or_B`, `Tuple_of_a_and_b`, `Vec2_of_uint8`, `Mat2x3_of_uint8` |
| `pkg.definitions.definitions()` | `pkg.definitions()` |
| `RuntimeIds.Demo_StructureS` | `pkg.demo.STRUCTURE_S` |
| `AttachmentRuntimeIds.Demo_ConceptA_Properties` | `pkg.demo.attachments.ConceptA.properties.runtime_id` |
| `<ns>_<concept>_<att>_get(getting, key)`, `_set`, `_has`, `_keys`, `_diff` | `pkg.<ns>.attachments.<Concept>.<att>.get(getting, key)`, … |
| `database_attachments.<ns>_<concept>_<att>_set(db, …)`, `_get`, `_del` | the same attachment, given the `Database`: `.set(db, …)`, `.get(db, …)`, `.delete(db, key)` |
| `p.vpr_value`; `Cls(value)` to view a stored value | `p.unwrap_value()`; `Cls.wrap_value(value)` or `Cls(value)`, both boxing it |
| `p.encode()`; `Cls.decode(blob)` | `Value.encode(p.unwrap_value())`; `Cls.wrap_value(Value.decode(blob, Cls.type(), pkg.definitions(), encoded=False))` |
| `value_type.type_X()` | `Cls.type()`: `demo.StructureS.type()`, `containers.Vector_of_uint8.type()` |
| a field `f_uint_8`, `channel_0`, an enumeration case `A_0` | `f_uint8`, `channel0`, `A0` |
| an `any` read as the runtime `ValueAny` | `AnyValue`; `unwrap()` gives the runtime value, as before |

The right-hand column, run against the `model` package this chapter uses (its `Tuto`
namespace is the module `model.tuto`; see {doc}`python` for the model). A namespace is a
module, a container is named by its shape, and the model's definitions are a function of
the package:

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

Runtime ids are exported by the unit, and an attachment carries its own:

```{doctest}
>>> tuto.LOGIN
f223819a-167a-b9f8-e483-3abf4a0c2518
>>> tuto.attachments.User.login.runtime_id
438491ed-5518-5d0c-9836-920ee80dd0e8
```

An attachment's operations take the store they act on; given a `Database`, they replace the
1.2 `database_attachments` functions:

```{doctest}
>>> login_of = tuto.attachments.User.login
>>> db = dsviper.Database.create_in_memory()
>>> _ = db.extend_definitions(model.definitions())
>>> alice = tuto.UserKey.create()

>>> db.begin_transaction()
>>> login_of.set(db, alice, tuto.Login(nickname="alice"))
True
>>> db.commit()
>>> login_of.get(db, alice).unwrap().nickname
'alice'

>>> db.begin_transaction()
>>> login_of.delete(db, alice)
True
>>> db.commit()
>>> login_of.has(db, alice)
False
```

`vpr_value` becomes `unwrap_value()`, and a stored value is boxed by `wrap_value` or by the
constructor — a box, not a copy:

```{doctest}
>>> login = tuto.Login(nickname="grace")
>>> value = login.unwrap_value()
>>> boxed = tuto.Login(value)
>>> boxed.nickname = "heidi"
>>> login.nickname
'heidi'
>>> tuto.Login.wrap_value(value) == login
True
```

`p.encode()` and `Cls.decode(blob)` become calls on the bridge, and `value_type.type_X()`
becomes the class's own `type()`:

```{doctest}
>>> blob = dsviper.Value.encode(login.unwrap_value())
>>> back = tuto.Login.wrap_value(
...     dsviper.Value.decode(blob, tuto.Login.type(), model.definitions(), encoded=False))
>>> back == login
True
>>> tuto.Login.type(), containers.Set_of_Tuto_UserKey.type()
(Tuto::Login, set<key<Tuto::User>>)
```

What reads the same: an attachment's `get` still answers an optional, so the 1.2 pattern
`opt = …get(…)` / `if opt:` / `opt.unwrap()` carries over unchanged. Structures are
constructed by naming their fields as keywords (`tuto.Login(nickname="alice")`), and
setting a field after construction works as before. Keys, their views and their
conversions are described in {doc}`python`, *Keys*; errors in *Errors*.

## TypeScript

| 1.2 | 2.0 |
|---|---|
| `Demo_Vector3`, `Demo_Level`, from the package root | `demo.Vector3`, `demo.Level`: each unit is a namespace of the package, and a subpath export (`pkg/demo`) |
| `Vector_uint8`, `Map_A_to_B`, … | `Vector_of_uint8`, `Map_of_A_to_B`, …, at the package root |
| `attachments.player_Property.get(…)` | `demo.attachments.Player.property.get(…)` |
| `functionPoolRemotes.Tools`, `attachmentFunctionPoolRemotes.PlayerModel` | `tools.Remote`, `player_model.Remote`, from `pkg/pools` |
| a pool function `add_vector`, `has_player` | `addVector`, `hasPlayer`: the DSM spelling |
| `x.compareTo(y)` | `x.compare(y)` |
| an enumeration as a proxy class: `e.name()`, `e.vprValue` | a string-literal union with a companion: `e` is the case name, `E.unwrapValue(e)`, `E.index(e)` |
| `p.vprValue` | `p.unwrapValue()` |
| `new X(value)` over a stored value | `X.wrapValue(value)` or `new X(value)`, both boxing it |

**An enumeration is a string.** In 1.2 an enumeration case was an instance of a generated
proxy class, and you asked it for its `name()` or its `vprValue`. In 2.0 the case *is* its
name, typed as a union of the case names — `"a" | "b" | "c"` — with a companion object of
the same name that holds the constants and the bridge, so two cases compare as strings:

```ts
const e: demo.EnumerationE = demo.EnumerationE.B;  // the constant is "b"
demo.EnumerationE.index(e);                        // 1
const viper = demo.EnumerationE.unwrapValue(e);    // a dsviper.ValueEnumeration
demo.EnumerationE.wrapValue(viper);                // "b"
```

The generator's laboratory,
[devkit-codegen-test](https://github.com/digital-substrate/devkit-codegen-test), keeps a
hand-written client of its `service` model on both lines; most rows of the table show in
it. Against 1.2:

```ts
import {
    Demo_Vector3,
    Demo_Level,
    functionPoolRemotes as fpr,
    attachmentFunctionPoolRemotes as afpr,
    attachments as sea,
} from "./service/dist/index.js";

const tools = new fpr.Tools(serviceRemote);
const vr = tools.add_vector(v1, v2);

const pm = new afpr.PlayerModel(serviceRemote);
const key = pm.create(mutating, nickname, Demo_Level.BEGINNER);
const pk = pm.has_player(mutating, nickname);
const property = sea.player_Property.get(mutating, pk.unwrap());
```

Against 2.0:

```ts
import { Vector3, Level } from "../generated/dist/demo/index.js";
import { Player } from "../generated/dist/demo/attachments.js";
import { tools, player_model } from "../generated/dist/pools.js";

const toolsRemote = new tools.Remote(serviceRemote);
console.log(`addVector(v1,v2) -> ${toolsRemote.addVector(v1, v2)}`);

const playerModel = new player_model.Remote(serviceRemote);
console.log(`key is ${playerModel.create(mutating, nickname, Level.BEGINNER)}`);
const found = playerModel.hasPlayer(mutating, nickname);
const document = Player.property.get(mutating, found.unwrap());
```

Bytes go through the bridge, as in Python: `dsviper.Value.encode(p.unwrapValue())`, and
`X.wrapValue(dsviper.Value.decode(blob, X.type(), definitions()))`. The full surface is
{doc}`node`.

## C++

| 1.2 | 2.0 |
|---|---|
| `NS::Demo::StructureS`, `NS::definitions()` | `ns::demo::StructureS`, `ns::codec::definitions()` |
| `ValueEncoder::encode_X(v)`, `ValueDecoder::decode_X(val)` | `ns::codec::encode(v)`, `ns::codec::decode<T>(val)` |
| `Writer{enc}.write_X(v)`, `Reader{dec, defs}.read_X()` | `write(w, v)` on a `Viper::StaticWriter::Writer`, `read(r, tag<T>{})` on a `Viper::StaticReader::Reader` — the same bytes |
| `NS::Demo::Attachments::Concept_Att::get(…)`, `NS::Demo::DatabaseAttachments::…` | `ns::demo::attachments::Concept::att::get(…)`, the `Database` overloads included |
| `NS::Database::create(…)` (the model registered for you) | `Viper::Database::create(…)` then `extendDefinitions(ns::codec::definitions())` |
| `AttachmentRuntimeIds::C_a` | `ns::demo::attachments::C::a::runtimeId` |
| `NS::FunctionPools::tools()`, `FunctionPoolBridges::Tools::add_vector` | `ns::tools::pool()`, `ns::tools::addVector` |
| `NS::AttachmentFunctionPools::playerModel()` | `ns::player_model::pool()` |
| `NS::AttachmentFunctionPools::attachments()` | gone: see below |

**The codec has its own namespace.** The types stay C++17 value types, and a structure keeps
the constructors 1.2 gave it. What crosses them to a `Viper::Value` is now one pair of
overloaded functions, `codec::encode` and `codec::decode<T>`, in place of one function per
type; JSON, XML and a hexdigest are one runtime call on what `encode` returns, and the
binary form is the runtime's static layer (see {doc}`cpp`, *The codec*).

**The database is the runtime's.** 1.2 generated an `NS::Database` class that registered the
model for you. 2.0 generates none: open a `Viper::Database` (or a `Viper::CommitDatabase`)
and extend it with the model once, with `extendDefinitions(ns::codec::definitions())`. The
attachments then take that database directly, inside a transaction.

**The generated attachment pool is gone.** 1.2 could generate every attachment's elementary
operations as one function pool for the dynamic world, under composed names
(`graph_graph_selection_union_vertex_keys`). Code written ahead calls the generated
attachments instead (`Graph::selection::unionVertexKeys`); a session without generation
uses the runtime directly, with the constants `Definitions.inject()` gives and an
`AttachmentMutating`. The model's own attachment function pools are still generated, by the
`Pool` feature, one namespace per pool.

In the laboratory's `service`, the server-side function over an attachment, against 1.2:

```cpp
using namespace Service::Demo;

namespace Service::AttachmentFunctionPoolBridges::PlayerModel {

PlayerKey create(std::shared_ptr<Viper::AttachmentMutating> const & mutating, std::string const & nickname, Demo::Level level) {
    auto const key{PlayerKey::create()};
    auto const property{PlayerProperty{nickname, level}};
    Attachments::Player_Property::set(mutating, key, property);
    return key;
}
```

Against 2.0:

```cpp
using namespace service::demo;

namespace service::player_model {

PlayerKey create(std::shared_ptr<Viper::AttachmentMutating> const & mutating, std::string const & nickname, service::demo::Level level) {
    auto const key{PlayerKey::create()};
    auto const property{PlayerProperty{nickname, level}};
    attachments::Player::property::set(mutating, key, property);
    return key;
}
```

and the server that exposes the pools, from `Service::FunctionPools::tools()` and
`Service::AttachmentFunctionPools::playerModel()` to:

```cpp
Viper::Service::make(
    service::codec::definitions(),
    {
        service::tools::pool(),
    },
    {
        service::player_model::pool()
    })
```

(The laboratory also changed its infrastructure name from `Service` to `service` between
the two lines; the outer namespace is whatever a project's `infrastructure` says.) Two
internal C++ applications were migrated along the same rows. The full surface is {doc}`cpp`.

## A worked example: dsviper-ge

[dsviper-ge](https://github.com/digital-substrate/dsviper-ge) is a graph editor written in
Python with Qt, over a commit database. Its business functions — create a vertex, select,
restore a graph's integrity — and its Qt components call a package generated from a model
with one DSM namespace, `Graph`. The `LTS-1.2` branch is the application against the 1.2 package; the kibo 2
line carries the migration.

### What it took

The project took the occasion to rename two packages: the generated one, `ge` in 1.2,
became `gei` (`infrastructure = "gei"` in its `kibo.toml`), and the business functions,
`model/` in 1.2, took the name `ge`. Over the hand-written Python files — the generated
package and the test added for the migration excluded — `git diff --stat` between the two
lines reports:

- **42 files changed, 737 insertions, 870 deletions** (rename detection on; one module,
  `graph.py`, counts twice, as a deletion under `model/` and an addition under `ge/`);
- for scale, the application has 56 hand-written Python files, 6,119 lines, on the kibo 2
  line (its shared `dsviper_components` package and the Qt-generated `ui_*.py` files not
  counted);
- of the 737 inserted lines, 184 call an attachment through its new path and 134 are
  imports.

The safety net was a scenario that runs the business functions step by step on an
in-memory database and records every document left behind, read through the runtime's
dynamic API so that it depends on neither package. It was recorded from the 1.2 code before
the migration started; the same scenario passes on the 1.2 code and on the migrated code,
all 19 steps.

### Before and after

The excerpts are copied from the two lines, trimmed; in each pair, the first block is the
1.2 code and the second the migrated code. **Imports**: the flat 1.2 package,
one name per line, becomes two modules — the unit and its containers — and the unit's
attachments:

```python
from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexKey,
    Graph_VertexVisualAttributes,
    Graph_Vertex2DAttributes,
    Graph_Position,
    Graph_Color,
    Set_Graph_VertexKey)
```

```python
from gei.graph import attachments
from gei import containers, graph
```

**A structure, a key, an attachment set in a mutation**: the types lose their prefix, and
each composed function name becomes a path to the attachment and its operation:

```python
def create(attachment_mutating: AttachmentMutating,
           value: int,
           position: Graph_Position,
           color: Graph_Color) -> Graph_VertexKey:

    vertex_key = Graph_VertexKey.create()

    visual_attributes = Graph_VertexVisualAttributes()
    visual_attributes.value = value
    visual_attributes.color = color
    attachments.graph_vertex_visual_attributes_set(attachment_mutating, vertex_key, visual_attributes)
```

```python
def create(attachment_mutating: AttachmentMutating,
           value: int,
           position: graph.Position,
           color: graph.Color) -> graph.VertexKey:

    vertex_key = graph.VertexKey.create()

    visual_attributes = graph.VertexVisualAttributes()
    visual_attributes.value = value
    visual_attributes.color = color
    attachments.Vertex.visual_attributes.set(attachment_mutating, vertex_key, visual_attributes)
```

**A container and a field operation**: `Set_Graph_VertexKey` is `containers.Set_of_Graph_VertexKey`,
and the read of an optional document is untouched:

```python
def select_all(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Select all vertices in the graph."""
    vertex_keys = Set_Graph_VertexKey()
    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        vertex_keys = opt.unwrap().vertex_keys

    attachments.graph_graph_selection_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)
```

```python
def select_all(attachment_mutating: AttachmentMutating, graph_key: graph.GraphKey) -> None:
    """Select all vertices in the graph."""
    vertex_keys = containers.Set_of_Graph_VertexKey()
    opt = attachments.Graph.topology.get(attachment_mutating, graph_key)
    if opt:
        vertex_keys = opt.unwrap().vertex_keys

    attachments.Graph.selection.union_vertex_keys(attachment_mutating, graph_key, vertex_keys)
```

**A dispatch from a Qt component**: the `CommitStore` call is the runtime's and does not
move; only the attachment inside the lambda does:

```python
lambda m: attachments.graph_vertex_visual_attributes_set_value(m, vertex_key, value)
```

```python
lambda m: attachments.Vertex.visual_attributes.set_value(m, vertex_key, value)
```

**The definitions and an attachment's runtime id**: the keys of an attachment no longer
need the attachment resolved from its runtime id first:

```python
result.extend_definitions(definitions.definitions())

attachment = self.store.state().definitions().check_attachment(
    definitions.AttachmentRuntimeIds.Graph_Graph_Description)
count = len(self.store.state().attachment_getting().keys(attachment)) + 1
```

```python
result.extend_definitions(definitions())

count = len(attachments.Graph.description.keys(self.store.state().attachment_getting())) + 1
```

**The bridge**, where a key is handed to a component that works on runtime values:

```python
self._commit_documents_dialog.documents().use_key(vertex_key.vpr_value)
```

```python
self._commit_documents_dialog.documents().use_key(vertex_key.unwrap_value())
```

dsviper-ge stores no bytes of its own, so it has no `encode` / `decode` to migrate; the
Python table above shows that row.

### One thing to watch: a unit is a module name

A unit is now a module with a short, common name — `graph` — and it can collide with a name
the application already uses. dsviper-ge met it twice and aliased the import: once where its
own business module was also called `graph`, once where a function parameter was:

```python
from gei import definitions, graph
from gei.graph import attachments
from ge import graph as ge_graph
```

```python
from gei.graph import attachments
from gei import graph as gei_graph
```

## Checklist

1. Write the project's `kibo.toml` and regenerate the package in place with kibo-project.
2. Fix the imports: one module per DSM namespace, `containers`, the unit's `attachments`.
3. Run the type checker and work through its errors with the tables: types without their
   prefix, containers named by shape, attachments as objects, the bridge, `type()`.
4. Move every `encode` / `decode` / `hexdigest` onto the bridge.
5. In C++, open the runtime's database and `extendDefinitions(codec::definitions())`.
6. Run the application, and whatever records its behaviour, against what the 1.2 code did.
