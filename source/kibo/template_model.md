# Template Model Reference

This reference documents **Template Model 2**, the model kibo 2.x exposes to
StringTemplate `.stg` files, and the **DSM Model** embedded in it — the two class
hierarchies that the StringTemplate engine consumes when generating code from DSM
definitions.

Understanding this reference is essential for anyone writing or modifying `.stg`
template files.

```{note}
Template Model 1 is the model of kibo 1.2. Template Model 2 renames the accessors that
describe a type as the binding sees it, with no compatibility aliases, and adds the entries
that render a template once per namespace or per pool. If you maintain a pack written for
kibo 1.2, start with [Migrating a template pack](migrating.md).
```

## Code Generation Pipeline

Kibo generates code from a JSON representation of DSM definitions. The pipeline is:

1. **Assemble** — Merge multiple `.dsm` files into a single definition set.
2. **Parse** — Produce the AST from the assembled definitions.
3. **Validate** — Check the semantics of the AST.
4. **Encode** — Serialize the validated definitions to JSON (`.dsm.json`).

[kibo-project](kibo-project.md) runs these four steps with `dsviper` and writes
`<infrastructure>.dsm.json` beside the project file.

5. **Load** — Kibo reads the `.dsm.json` file to construct a hierarchy of objects where
   the root object is an instance of `DSMDefinitions`.
6. **Convert** — The Object-Oriented representation is not suited for the StringTemplate
   engine, so Kibo converts it to a **Template Model** representation that drastically
   simplifies feature implementation with templates. The conversion is made for the target
   named by `-c` (`cpp`, `python` or `typescript`): the target decides how a type is spelled
   through its binding and where each output file lands.
7. **Render** — Each `.stg` file is rendered once per scope it declares (the whole model,
   each namespace, each pool), and each result is saved under the name the target's layout
   gives it.

Before rendering, kibo refuses a model whose outputs would overwrite each other: a namespace
that carries the model's own name (`-n`), and, for `cpp`, two namespaces or pools that lower
snake case spells alike. For `python` and `typescript`, two DSM names that the `snake` format
spells alike in one scope stop the generation too.

```{note}
DSM Model classes are **embedded** in the Template Model classes to provide a basic
introspection API. Template rules can access both layers.
```

## What a Template Is Rendered For

A template file says what it is rendered for by the **entry templates** it declares. Kibo
never sees a template pack, only what `-t` points at, so the entry is the only thing it can
ask.

| Entry | Argument | Rendered | Scope |
|---|---|---|---|
| `main(m)` | `m`: `TemplateDefinitions` | once, for the whole model (as in Template Model 1) | model |
| `model(m)` | `m`: `TemplateDefinitions` | once, for the whole model | model |
| `unit(u)` | `u`: `TemplateNameSpace` | once per DSM namespace, in emission order | unit |
| `pool(p)` | `p`: `TemplateFunctionPool` | once per `function_pool` | unit |
| `attachment_pool(p)` | `p`: `TemplateAttachmentFunctionPool` | once per `attachment_function_pool` | unit |

Kibo renders an entry only when the template **defines it and it takes that argument**: a
`pool(po)` written as a loop body before these names were reserved is not mistaken for an
entry. A template may declare several entries — most declare both
`unit` and `model`, because the concepts and structures of a namespace belong to a unit while
what no unit can claim belongs to the model. `main` and `model` render to the same file, so
declare one of them. A file `-t` names that declares none is an error, not an empty file; in
a directory, such a file is one the others import — a pack's banner — and is skipped.

A pool is a unit too — a namespace holding only functions — so it is named and laid out like
one.

### Where the output lands

The output file name is the generator's, not the project's: it is built by the target's
**layout** from the scope, the model name (`-n`), the unit name and the template file's base
name (its name without `.stg`).

| Target | Model scope | Unit scope |
|---|---|---|
| `cpp` | `<model>_<template>` | `<model>_<unit, lower snake case>_<template>` |
| `python`, `typescript` | `<template>`, at the package root | `<unit, snake>/<template>` |

C++ files go to one flat directory, prefixed by the C++ namespace path they declare. Python
and TypeScript output is a package, where a unit is a directory. Nothing else is inferred
from the template name: a pack that wants a package initialiser writes a template called
`__init__.py.stg`.

For example, with `-n Topology` and a model declaring the namespaces `ModelA` and
`Annotations` and the function pool `Tools`, the first-party pack renders:

| Template | Entry | `cpp` | `python` / `typescript` |
|---|---|---|---|
| `cpp/codec.hpp.stg` | `model(m)` | `Topology_codec.hpp` | |
| `cpp/codec.hpp.stg` | `unit(u)` | `Topology_model_a_codec.hpp` | |
| `cpp/pool.hpp.stg` | `pool(p)` | `Topology_tools_pool.hpp` | |
| `python/__init__.py.stg` | `model(m)` | | `__init__.py` |
| `python/__init__.py.stg` | `unit(u)` | | `model_a/__init__.py`, `annotations_/__init__.py` |
| `python/data.py.stg` | `unit(u)` | | `model_a/data.py` |
| `python/pool.py.stg` | `pool(p)` | | `tools/pool.py` |

A unit directory follows the `snake` format, so a namespace whose snake case Python reserves
takes a trailing underscore (`annotations_`), in both bindings.

### Reaching another artefact: `include` and `guard`

A template never composes the path of another generated artefact: it names the artefact and
the layout answers. `include` and `guard` are maps that answer **every** key: the key is the
artefact's name (the base name of the template that produces it, without extension), and a
key that matches nothing on disk becomes a missing include at compile time.

| Expression | `cpp` | `python` / `typescript` |
|---|---|---|
| `<m.include.codec>` | `Topology_codec.hpp` | `codec` |
| `<u.include.data>` (unit `ModelA`) | `Topology_model_a_data.hpp` | `model_a.data` |
| `<u.guard.data>` | `Topology_model_a_data_hpp` | `model_a_data` |

A C++ path always ends in `.hpp`. A Python or TypeScript path is the module named from the
package root; the leading dots of a relative import are the template's to write, since only
the template knows how deep the importing file sits. A guard is the path with every character
outside `[A-Za-z0-9_]` replaced by an underscore.

### Render diagnostics

A template that reads an accessor the model does not carry renders the empty string. Kibo
reports each such miss on stderr, once per distinct message with its count:

```text
kibo: templates/data.py.stg: context [/main /structure] 12:8 no such property or can't access: …
```

They are warnings: the file is still written and kibo exits zero. A clean render prints
nothing.

## Type Suffix

During the conversion from DSM Model to Template Model, Kibo recursively collects and
decomposes all types and constructs a unique symbol per type called the **type suffix**.

### Decomposition Examples

- `float`
    - `_float`
- `vector<float>`
    - `_vector_float`
    - `_float`
- `map<tuple<int64, float>, vector<key<User>>>`
    - `_map_tuple_int64_float_to_vector_UserKey`
    - `_tuple_int64_float`
    - `_int64`
    - `_float`
    - `_vector_UserKey`
    - `_UserKey`

The type suffix is neutral: it is the same whatever the target, and a type of a namespace
carries the namespace (`_ModelA_MaterialKey`, `_set_ModelA_MaterialKey`).

### Recursive Template Invocation

The type suffix is used in template rules to call the generated implementation for the
inner type (recursion).

In this example, the rule implements the `write` function for the generic type
`map<keyType, elementType>`. The `keyTypeSuffix` and `elementTypeSuffix` are used to call
the implementation of the `write` function for the `keyType` and for the `elementType`:

```text
void StreamWriter::write<v.typeSuffix>(<v.type> const & value) {
    writing->writeUInt64(static_cast<std::uint64_t>(value.size()));
    for (auto const & [k, v] : value) {
        write<v.keyTypeSuffix>(k);
        write<v.elementTypeSuffix>(v);
    }
}
```

The generated code for a `map<int8, string>` is:

```cpp
void StreamWriter::write_map_int8_to_string(std::map<std::int8_t,std::string> const & value) {
    writing->writeUInt64(static_cast<std::uint64_t>(value.size()));
    for (auto const & [k, v] : value) {
        write_int8(k);
        write_string(v);
    }
}
```

In theory, any feature can be implemented by recursively consuming the DSM definitions.
In practice, it is an art to elaborate the patterns used to implement a templated feature.

```{tip}
The best way to learn is by studying the templates of the first-party pack:
- `kibo-template-viper/cpp/*.stg` — the C++ surface
- `kibo-template-viper/python/*.stg` — the Python package
- `kibo-template-viper/typescript/*.stg` — the TypeScript package
```

## The Three Type Spaces

A type has three spellings, and the Template Model carries each of them under its own name.

| Space | Accessor | The concept `ModelA::Material` | The container `set<key<ModelA::Material>>` |
|---|---|---|---|
| DSM — what the model calls it | `dsmType` | `ModelA::Material` | `set<key<ModelA::Material>>` |
| Target — how the native C++ target writes it | `type` | `model_a::MaterialKey` | `std::set<model_a::MaterialKey>` |
| Binding — how the type appears through the binding | `bindingType.type` | `ModelA_MaterialKey` | `Set_of_ModelA_MaterialKey` |

`type` (with `typeInNamespace`, `elementType`, `keyType`, `passBy`, `viperValue`, …) is the
C++ spelling whatever `-c` says. `bindingType` is a `TemplateBindingType` and carries the
spellings of the target named by `-c`: the same 64-bit integer is `int` under `python` and
`bigint` under `typescript`. `dsmType` is identical across the three targets; it is carried
by the entities (concepts, clubs, enumerations, structures), the container functions and the
members of a tuple or a variant.

### Which space to use where

- **In a type position** — a signature, an annotation, a declaration — use the target's
  spelling: `type` for C++, `bindingType` for a binding (`.annotation`, `.qualified`,
  `.type`), or `bindingType.proxy` where you build a *name* rather than write a type.
- **In a comment, a docstring, a `repr` or an exception message** — use `dsmType`. Such a
  message guards a runtime type comparison, and a runtime type is a DSM type; the DSM name is
  what the author of the model wrote, and it reads the same whatever the target.

A template chooses between forms — a module prefix, a wrapped or a plain read, `.qualified`
or `.annotation` — because those depend on the file and the idiom. It never rewrites a type
and carries no lookup table: every spelling comes from the generator. A field read in the
first-party Python pack (`python/data.py.stg`):

```text
read(f) ::= <%<if(f.bindingType.useProxy)>return typing.cast("<hint(f)>", wrap(self._value.at("<f.name>", encoded=False)))<else>return typing.cast("<hint(f)>", self._value.at("<f.name>"))<endif>%>
write(f) ::= <%self._value.set("<f.name>", <if(f.bindingType.useProxy)>unwrap(value)<else>value<endif>)%>

hint(f) ::= <%<f.bindingType.annotation>%>
input_hint(f) ::= <%<f.bindingType.input>%>
```

### TemplateBindingType

A type as it appears through the binding. Every class that describes a type reaches one
through `bindingType` (and the element, key and return variants listed in each class).

```java
public class TemplateBindingType {
    // Proxy
    public String proxy;            // the generated class name, the same whatever the binding
    public Boolean useProxy;        // whether the type crosses as a runtime value to wrap / unwrap
    public Boolean isNamed;         // whether a unit declares the type (enumeration, structure,
                                    // concept, club), as opposed to a container built from others

    // Type
    public String typeSuffix;       // the neutral type suffix
    public String type;             // the proxy name when the type needs one, else the binding's
                                    // own spelling of the primitive
    public String typeInNamespace;  // `type` written from inside the unit in scope

    // Annotation
    public String annotation;       // the type written in full, as a type checker needs it,
                                    // from inside the unit in scope
    public String qualified;        // the annotation written from outside every unit
    public String input;            // the annotation a write accepts, when wider than a read
    public String inputQualified;   // `input` written from outside every unit
    public String constructorInput; // what the constructor of a generated container class takes
                                    // besides an instance of itself
}
```

What each member answers, for a structure field declared in the namespace `ModelA`
(`python` target unless stated):

| Member | `uint8 r` | `key<Material> material` | `set<key<Material>>` (container function) |
|---|---|---|---|
| `proxy` | `uint8` | `ModelA_MaterialKey` | `Set_of_ModelA_MaterialKey` |
| `useProxy` | false | true | true |
| `isNamed` | false | true | false |
| `typeSuffix` | `_uint8` | `_ModelA_MaterialKey` | `_set_ModelA_MaterialKey` |
| `type` | `int` (`number` in `typescript`) | `ModelA_MaterialKey` | `Set_of_ModelA_MaterialKey` |
| `typeInNamespace` | `int` | `MaterialKey` | `Set_of_ModelA_MaterialKey` |
| `annotation` | `int` | `MaterialKey` | `containers.Set_of_ModelA_MaterialKey` |
| `qualified` | `int` | `model_a.MaterialKey` | `containers.Set_of_ModelA_MaterialKey` |
| `constructorInput` | absent | absent | `typing.Iterable[model_a.MaterialKey] \| None` |

- `typeInNamespace` is bare for a type of the unit in scope and prefixed by its module for a
  type of another unit (`Colour` against `model_b.Colour`); it equals `type` where no unit is
  in scope.
- `qualified` qualifies a type of the unit in scope by its module too. A template needs it
  where a name the unit declares at module level can hide the type: the attachments of a
  concept named `MaterialKey` are a class of that name, beside the key of `Material`.
- `input` and `inputQualified` fall back to `annotation` and `qualified` when a write accepts
  exactly what a read returns. They are wider where the runtime decodes more into the type:
  an optional also takes its element or nothing, a variant its members
  (`containers.Variant_of_string_or_uint8_or_Demo_StructureS | str | int | demo.StructureS`).
- `constructorInput` is present only for a container, an optional or a variant: the host's own
  collection, whose generated elements the constructor unwraps, so that the runtime checks
  every element where the container is built.
- On an entity — `TemplateConcept`, `TemplateClub`, `TemplateEnumeration`,
  `TemplateStructure` — `bindingType` is the type seen from the unit that declares it:
  `typeInNamespace`, `annotation` and `qualified` are all the bare name (`MaterialKey`), and
  `type` is the flat proxy name (`ModelA_MaterialKey`). For a concept or a club, `proxy` is
  the namespace and the name without the `Key` suffix (`ModelA_Material`).

```{note}
The native `cpp` target has no binding space. There, `annotation`, `qualified`, `input`,
`inputQualified` and `constructorInput` are absent from a type's `bindingType`, and `type`
and `typeInNamespace` are present only when `useProxy` is true. `proxy`, `useProxy`,
`isNamed` and `typeSuffix` always carry.
```

## Template Naming Convention

Type annotations are not available in StringTemplate, so a good parameter naming
convention improves understanding of the problem decomposition into template rules.

The arguments of the entry templates are fixed by kibo: `main(m)` and `model(m)`, `unit(u)`,
`pool(p)` and `attachment_pool(p)`. There is no convention for naming the other rules, but
the following parameter names are used throughout the first-party pack:

| Parameter | Usage                                              |
|-----------|----------------------------------------------------|
| `m`       | Definitions (model)                                |
| `u`       | Unit (namespace)                                   |
| `d`       | Dependency (a namespace a unit or a pool reaches)  |
| `p`       | Pool                                               |
| `a`       | Attachment, or Function Parameter in a pool        |
| `e`       | Enumeration                                        |
| `em`      | Enumeration Member                                 |
| `s`       | Structure                                          |
| `sf`      | Structure Field                                    |
| `c`       | Concept / Club                                     |
| `cc`      | Concept Child                                      |
| `cd`      | Concept Descendant                                 |
| `cm`      | Club Member                                        |
| `tm`      | Tuple Member                                       |
| `vm`      | Variant Member                                     |
| `f`       | Function                                           |
| `v`       | other                                              |

## String Formats

A string attribute can be rendered through a format: `<u.name;format="lsc">`. The formats
apply to string values only; an unknown format leaves the string unchanged.

| Format | Result | Input | Output |
|---|---|---|---|
| `u` | uppercase | `ModelA` | `MODELA` |
| `l` | lowercase | `ModelA` | `modela` |
| `uf` | first letter uppercase | `userIDs` | `UserIDs` |
| `lf` | first letter lowercase | `ModelA` | `modelA` |
| `sc` | snake case, letters kept as written | `RGBProfile` | `RGB_Profile` |
| `lsc` | lower snake case | `ModelA` | `model_a` |
| `usc` | upper snake case | `ModelA` | `MODEL_A` |
| `snake` | snake case of a static name | `vec3Curves` | `vec3_curves` |
| `usnake` | `snake`, uppercased | `RGBProfile` | `RGB_PROFILE` |
| `string` | body of a double-quoted string literal | `Say "hi"` + newline | `Say \"hi\"\n` |
| `docstring` | body of a Python triple-quoted docstring | `A "quoted" end"` | `A "quoted" end\"` |
| `comment` | body of a `/** … */` block comment | `see a/*b*/` | `see a/*b* /` |

**`lsc` and `snake` are two rules.** `lsc` (with `sc` and `usc`) is the rule the runtime
computes for names it derives itself, and must stay identical to it: C++ namespaces and
names that cross the wire use it. `snake` names a static symbol of a generated package — a
Python field, method, parameter or module, and the package directories of both bindings —
and only there do the two differ:

| Input | `lsc` | `snake` |
|---|---|---|
| `vec3Curves` | `vec_3_curves` | `vec3_curves` |
| `doc_UInt8` | `doc_u_int_8` | `doc_uint8` |
| `render2DAttributes` | `render_2d_attributes` | `render_2d_attributes` |
| `userIDs` | `user_ids` | `user_ids` |
| `from` | `from` | `from_` |

`snake` keeps a name with no capital as written, and an underscore the author wrote; it never
splits the DSM words `UInt`, `UUId` and `XArray`, plus the atoms a project passes with
`--atom`; it takes the name a project gives with `--rename`. A projection that lands on a word
Python reserves — a keyword, or a `__future__` feature such as `annotations` — takes a
trailing underscore; `usnake` needs none (`FROM`).

`string` escapes a backslash, a double quote, a newline, a carriage return and a tab, and is
valid in C++, TypeScript and Python. `docstring` keeps lines as lines and escapes only a
backslash, a `"""` and a final `"`. `comment` breaks every `*/` so the comment cannot close
early.

## Template Model

During the construction of the template model, the converter substitutes complex types
with simple string representations.

For instance, the string values substituted for the type `map<int64, vector<string>>`
in an instance of `TemplateMapFunction` are:

```java
class TemplateMapFunction {
    //...
    public String dsmType;           // "map<int64, vector<string>>"
    public String type;              // "std::map<std::int64_t, std::vector<std::string>>"
    public String typeSuffix;        // "_map_int64_to_vector_string"
    public String keyTypeSuffix;     // "_int64"
    public String elementTypeSuffix; // "_vector_string"
    //...
}
```

The following sections use a **pseudo-class** representation to illustrate the fields
accessible by the StringTemplate engine to generate code and propagate the recursion. In the
Java source most of them are getters (`getTypeSuffix()` is read as `typeSuffix`); a value
noted *absent* renders as the empty string and is false in an `<if(...)>`.

### TemplateDefinitions

The root class exposes all the DSM definitions of the `model.dsm.json` from the Template
Model perspective. It is the `m` of `main(m)` and `model(m)`, and every unit and pool reaches
it as `model`.

```java
public class TemplateDefinitions {

    public String generated;   // "Generated from <definitions> by kibo-X.Y.Z.jar"
    public String namespace;   // the model name, -n

    // Artefacts
    public TemplateIncludePaths include;  // where a model-wide artefact is found: <m.include.codec>
    public TemplateIncludePaths guard;    // the include guard of each model-wide artefact

    // Namespaces, in emission order
    public ArrayList<TemplateNameSpace> nameSpaces;

    // Definitions, sorted by type
    public ArrayList<TemplateConcept> concepts;
    public ArrayList<TemplateClub> clubs;
    public ArrayList<TemplateStructure> structures;
    public ArrayList<TemplateStructure> sortedStructures;  // a structure after those it uses
    public ArrayList<TemplateEnumeration> enumerations;
    public ArrayList<TemplateAttachment> attachments;      // sorted by identifier
    public ArrayList<TemplateAttachedKeyType> attachedKeyTypes;           // distinct, by type suffix
    public ArrayList<TemplateAttachedDocumentType> attachedDocumentTypes; // distinct, by type suffix

    // Pools, sorted by name
    public ArrayList<TemplateFunctionPool> functionPools;
    public ArrayList<TemplateAttachmentFunctionPool> attachmentFunctionPools;

    // Attachment Pool
    public String attachmentsPoolUuid;  // derived from "<namespace>.Pool.Attachments"

    // Functions: one per distinct container shape, sorted by type
    public ArrayList<TemplateVecFunction> vecFunctions;
    public ArrayList<TemplateMatFunction> matFunctions;
    public ArrayList<TemplateTupleFunction> tupleFunctions;
    public ArrayList<TemplateOptionalFunction> optionalFunctions;
    public ArrayList<TemplateVectorFunction> vectorFunctions;
    public ArrayList<TemplateSetFunction> setFunctions;
    public ArrayList<TemplateMapFunction> mapFunctions;
    public ArrayList<TemplateXArrayFunction> xarrayFunctions;
    public ArrayList<TemplateVariantFunction> variantFunctions;
}
```

The container functions belong to the model, not to a unit: a `set<B>` is the same type
wherever it is used. Under `python` and `typescript` they also hold the containers the
generated surface returns without the model declaring them — the set of an attachment's
keys, the optional of a key — since a binding that wraps one runtime value per object needs a
generated class for each.

#### Anatomy of a complete Feature

A feature is a set of templates; each declares the entries it needs. This is
`kibo-template-viper/cpp/codec.hpp.stg`, shortened: one header per namespace, plus one for
the whole model that includes every namespace's.

```text
import "banner.stg"

unit(u) ::= <<
// <u.name> codec -- how the types of this namespace cross to a Viper::Value.
//
<banner(u.model)>

#ifndef <u.guard.codec>
#define <u.guard.codec>

#include "<u.include.data>"
<u.dependencies.types:{d|#include "<d.include.codec>"};separator="\n">

namespace <u.model.namespace>::<u.name;format="lsc"> {

<u.concepts:keyed();separator="\n\n">

<u.clubs:keyed();separator="\n\n">

<u.enumerations:enumeration();separator="\n\n">

<u.structures:plain();separator="\n\n">

} // namespace <u.model.namespace>::<u.name;format="lsc">

#endif

>>

keyed(e) ::= <<
void write(Viper::StaticWriter::Writer & w, <e.name>Key const & value);
<e.name>Key read(Viper::StaticReader::Reader & r, Viper::StaticType::tag\<<e.name>Key>);
>>

...

model(m) ::= <<
// <m.namespace>::codec -- what needs the whole model: its definitions, and the bridge
// between a C++ value and a Viper::Value.
//
<banner(m)>

#ifndef <m.guard.codec>
#define <m.guard.codec>

#include "<m.include.any_concept>"
<m.nameSpaces:{u|#include "<u.include.codec>"
#include "<u.include.model>"};separator="\n">

namespace <m.namespace>::codec {
...
} // namespace <m.namespace>::codec

#endif

>>
```

Rendered with `-c cpp -n Topology`, this writes `Topology_codec.hpp` and one
`Topology_<unit>_codec.hpp` per namespace. A model-wide feature that walks the container
shapes does so from `m`: `<m.setFunctions:set();separator="\n">`, and so on for each list.

### TemplateNameSpace

A unit: the definitions of one DSM namespace, and what its generated code needs to reach.
It is the `u` of `unit(u)`.

```java
public class TemplateNameSpace {
    // Namespace
    public NameSpace nameSpace;   // the DSM namespace (uuid, name)
    public String name;

    // Model
    public TemplateDefinitions model;     // the whole model, for what a unit does not own

    // Artefacts
    public TemplateIncludePaths include;  // where this unit's artefacts are found: <u.include.data>
    public TemplateIncludePaths guard;    // the include guard of each of this unit's artefacts

    // Dependencies
    public TemplateDependencies dependencies;  // the other namespaces this one reaches

    // Definitions
    public ArrayList<TemplateConcept> concepts;    // a parent before its children
    public ArrayList<TemplateClub> clubs;
    public ArrayList<TemplateStructure> structures;
    public ArrayList<TemplateStructure> sortedStructures;
    public ArrayList<TemplateEnumeration> enumerations;
    public ArrayList<TemplateAttachment> attachments;
    public ArrayList<TemplateAttachmentScope> attachmentScopes;  // the same attachments,
                                                                 // grouped by concept

    // Names
    public ArrayList<String> exported;  // every name this unit declares, as the target writes it
}
```

`exported` is the concepts' and clubs' keys (with their `Key` suffix), then the enumerations,
then the structures — `MaterialKey, MaterialKeyKey, Finish, Colour, MaterialKeyNote` for a
namespace declaring the concepts `Material` and `MaterialKey`, the enumeration `Finish` and the
structures `Colour` and `MaterialKeyNote`. It is the list an export list, an import of a unit's
own names or a registry of its classes needs.

`attachments` suits a target where a scope merges (three C++ `namespace Material` blocks are
one); `attachmentScopes` suits one where it does not (three `class Material` definitions leave
one).

### TemplateDependencies

What a unit reaches, separated by the kind of declaration that reaches it. An artefact asks
for the dependencies of *what it emits*: a types header includes `u.dependencies.types`, an
attachments header `u.dependencies.attachments`. Including `all` compiles and is wrong.

```java
public class TemplateDependencies {
    public ArrayList<TemplateNameSpace> types;        // reached by concept parents, club members
                                                      // and structure fields
    public ArrayList<TemplateNameSpace> attachments;  // reached by an attachment's key or
                                                      // document type
    public ArrayList<TemplateNameSpace> functions;    // reached by a function's parameters or
                                                      // return type: a pool's dependencies
    public ArrayList<TemplateNameSpace> all;          // everything the unit reaches, in emission order
}
```

A namespace fills `types`, `attachments` and `all`; a pool fills `functions` and `all`.

### TemplateIncludePaths

Where a template finds another generated artefact, reached as `include` or `guard` on the
model, a unit or a pool. It is a map: the key is the artefact's name, the value is its path
(`include`) or its include guard (`guard`), as described in
[Reaching another artefact](#reaching-another-artefact-include-and-guard). Every key answers.

### TemplateAttachmentScope

The attachments a unit declares on one concept, grouped.

```java
public class TemplateAttachmentScope {
    public String name;                            // the concept, spelled as a scope of this
                                                   // unit can hold it (see conceptScope)
    public TemplateAttachedKeyType keyType;
    public ArrayList<TemplateAttachment> attachments;
}
```

### TemplateConcept

Corresponds to the definition of a `concept`.

```java
public class TemplateConcept {
    // DSM
    public DSMConcept dsmConcept;

    // Components
    public TemplateConcept parent;
    public String parentNameInNamespace;     // the parent, as a C++ scope writes it: Thing,
                                             // or core::Thing from another namespace
    public String parentBindingInNamespace;  // the parent's key, as a module writes it:
                                             // ThingKey, or core.ThingKey from another namespace

    public ArrayList<TemplateConcept> children;
    public ArrayList<TemplateConcept> descendants;        // itself included
    public ArrayList<TemplateConcept> strictDescendants;  // itself excluded
    public ArrayList<TemplateConceptInNamespace> strictDescendantsInNamespace;
    public Boolean hasForeignDescendants;    // whether a strict descendant lives in another
                                             // namespace

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String dsmType;      // the DSM name: ModelA::Material
    public String type;         // the C++ key type: model_a::MaterialKey
    public String typeSuffix;

    // Attachments
    public ArrayList<TemplateAttachment> attachments;

    // Viper C++
    public String viperType;    // "TypeKey"
    public String viperValue;   // "ValueKey"

    // Binding
    public TemplateBindingType bindingType;
}
```

`hasForeignDescendants` exists because namespaces are acyclic and a descendant's namespace
depends on its parent's: the parent's generated code must not name it. A template naming
every concept a key may designate names the local ones only, and widens to the base key
class when this is true.

### TemplateConceptInNamespace

Wraps a `TemplateConcept` to provide namespace-qualified names. Used in
`strictDescendantsInNamespace` and `membersInNamespace` to generate correct type
references when a concept belongs to a different namespace.

```java
public class TemplateConceptInNamespace {
    // Component
    public TemplateConcept concept;

    // Namespace
    public Boolean isLocal;             // whether the concept is declared in the namespace it
                                        // is seen from
    public String nameInNamespace;      // Thing, or core::Thing
    public String asNameInNamespace;    // Thing, or CoreThing
    public String bindingInNamespace;   // the key as a module writes it: ThingKey, or core.ThingKey
}
```

### TemplateClub

Corresponds to the definition of a `club`.

```java
public class TemplateClub {
    // DSM
    public DSMClub dsmClub;

    // Components
    public ArrayList<TemplateConcept> members;
    public ArrayList<TemplateConceptInNamespace> membersInNamespace;
    public ArrayList<TemplateConcept> memberDescendants;

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String dsmType;      // the DSM name, without the Key suffix of `type`
    public String type;
    public String typeSuffix;

    // Viper C++
    public String viperType;    // "TypeKey"
    public String viperValue;   // "ValueKey"

    // Binding
    public TemplateBindingType bindingType;
}
```

### TemplateEnumeration

Corresponds to the definition of an `enum`.

```java
public class TemplateEnumeration {
    // DSM
    public DSMEnumeration dsmEnumeration;

    // Components
    public ArrayList<DSMEnumerationCase> members;

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String dsmType;      // the DSM name, whatever the target
    public String type;
    public String typeSuffix;

    // Viper C++
    public String viperType;    // "TypeEnumeration"
    public String viperValue;   // "ValueEnumeration"

    // Binding
    public TemplateBindingType bindingType;
}
```

### TemplateStructure

Corresponds to the definition of a `struct`.

```java
public class TemplateStructure {
    // DSM
    public DSMStructure dsmStructure;

    // Components
    public ArrayList<TemplateStructureField> fields;

    // Predicates
    public boolean isMovable;

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String dsmType;      // the DSM name, whatever the target
    public String type;
    public String typeSuffix;

    // Viper C++
    public String viperType;    // "TypeStructure"
    public String viperValue;   // "ValueStructure"

    // Binding
    public TemplateBindingType bindingType;
}
```

### TemplateStructureField

```java
public class TemplateStructureField {
    // DSM
    public DSMStructureField dsmField;

    public String name;
    public String passBy;           // " const &", or empty for a type passed by value
    public String defaultValue;     // the C++ default; {} when the model declares none
    public boolean hasDefaultValue; // whether the model declares a default value

    // Predicates
    public boolean isMovable;
    public boolean isTypeAny;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeInNamespace;  // the type as written inside the structure's namespace
    public String typeSuffix;

    // Field
    public TemplateField field;

    // Viper C++
    public String viperValue;

    // Binding
    public TemplateBindingType bindingType;
}
```

### TemplateAttachment

Corresponds to the definition of an `attachment`.

```java
public class TemplateAttachment {
    // DSM
    public DSMAttachment dsmAttachment;

    public String representation;   // attachment<Link, Pair> Projection::pair
    public String conceptScope;     // the concept, spelled as a namespace level can hold it
    public String identifier;       // <Concept>_<Attachment>: Link_Pair

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public TemplateAttachedKeyType keyType;
    public TemplateAttachedDocumentType documentType;
}
```

`conceptScope` is the concept's name when the concept belongs to the attachment's own
namespace (or to the global one), and `<Namespace>_<Concept>` when it does not:
`Material` against `ModelA_Material`. It is a property of the attachment alone, so adding an
attachment never renames another. `identifier`, by contrast, is prefixed by the concept's
namespace only when two attachments of the model would otherwise collide.

### TemplateAttachedKeyType

```java
public class TemplateAttachedKeyType {
    // Namespace
    public String namespace;
    public String name;             // the concept's name; AnyConcept for any_concept

    // Type
    public String type;
    public String typeInNamespace;
    public String typeSuffix;

    // Viper C++
    public String viperValue;

    // Binding
    public TemplateBindingType bindingType;
    public TemplateBindingType bindingKeySetType;  // the set of these keys: what listing an
                                                   // attachment's keys returns
}
```

`bindingKeySetType` is absent under `cpp`.

### TemplateAttachedDocumentType

```java
public class TemplateAttachedDocumentType {
    // Predicates
    public Boolean isStructure;
    public boolean useBlobId;

    // Component
    public TemplateStructure structure;

    // Type
    public String type;
    public String typeInNamespace;
    public String typeSuffix;

    // Field
    public TemplateField field;

    // Viper C++
    public String viperValue;

    // Binding
    public TemplateBindingType bindingType;
}
```

### TemplateField

This class is used to generate **path-based mutators** per container. It is reached as
`field` on a structure field and on an attached document type.

```java
public class TemplateField {
    public String passBy;

    // Predicates
    public Boolean isNotBox;
    public Boolean isBox;
    public Boolean isSet;
    public Boolean isMap;
    public Boolean isXArray;

    // Type
    public String type;                    // BOX, SET, MAP or XARRAY
    public String keyType;
    public String keyTypeInNamespace;      // the key type as written inside the owning namespace
    public String keyTypeSuffix;
    public String elementType;
    public String elementTypeInNamespace;  // the element type as written inside the owning namespace
    public String elementTypeSuffix;

    // Viper C++
    public String elementTypeViperValue;

    // Binding
    public TemplateBindingType bindingType;        // the container itself
    public TemplateBindingType bindingKeyType;
    public TemplateBindingType bindingElementType;
    public TemplateBindingType bindingKeySetType;  // for a map, the set of its keys: what removing
                                                   // entries by key takes; absent otherwise
}
```

The owning namespace is the structure's for a structure field and the attachment's for a
document. A qualified `keyType` or `elementType` can be shadowed there — a concept named like
its namespace makes `Graph::X` name the concept — which is what the `*InNamespace` spellings
avoid. Where the container has no key or no element, the string members read `<None>` and the
binding members are absent.

### TemplateFunctionPool

Corresponds to the definition of a `function_pool`. It is the `p` of `pool(p)`.

```java
public class TemplateFunctionPool {
    // DSM
    public DSMFunctionPool dsmFunctionPool;
    public String name;
    public String uuid;

    // Components
    public ArrayList<TemplateFunction> functions;

    // Model
    public TemplateDefinitions model;     // the whole model, for what a pool does not own

    // Artefacts
    public TemplateIncludePaths include;  // where this pool's own artefacts are found
    public TemplateIncludePaths guard;    // the include guard of each of this pool's artefacts

    // Dependencies
    public TemplateDependencies dependencies;  // fills `functions`: what the signatures reach

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;   // "FunctionPool"
}
```

A pool belongs to no namespace, so every named type its signatures mention is foreign to
it: in a pool template, a binding's `typeInNamespace` and `annotation` are always qualified.

### TemplateFunction

```java
public class TemplateFunction {
    // DSM
    public String name;

    // Components
    public ArrayList<TemplateFunctionParameter> parameters;

    // Predicates
    public Boolean isVoid;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeSuffix;

    // Viper C++
    public String returnViperValue;

    // Binding
    public TemplateBindingType returnBindingType;
}
```

### TemplateFunctionParameter

```java
public class TemplateFunctionParameter {
    // DSM
    public String name;

    public String passBy;

    // Type
    public String type;
    public String typeSuffix;

    // Viper C++
    public String viperValue;

    // Binding
    public TemplateBindingType bindingType;
}
```

### TemplateAttachmentFunctionPool

Corresponds to the definition of an `attachment_function_pool`. It is the `p` of
`attachment_pool(p)`.

```java
public class TemplateAttachmentFunctionPool {
    // DSM
    public DSMAttachmentFunctionPool dsmAttachmentFunctionPool;
    public String name;
    public String uuid;

    // Components
    public ArrayList<TemplateAttachmentFunction> functions;

    // Model
    public TemplateDefinitions model;

    // Artefacts
    public TemplateIncludePaths include;
    public TemplateIncludePaths guard;

    // Dependencies
    public TemplateDependencies dependencies;  // fills `functions`: what the signatures reach

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;   // "AttachmentFunctionPool"
}
```

### TemplateAttachmentFunction

```java
public class TemplateAttachmentFunction {
    // DSM
    public String name;

    // Components
    public ArrayList<TemplateFunctionParameter> parameters;

    // Predicates
    public Boolean isVoid;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeSuffix;
    public String interfaceType;   // "Mutating" or "Getting"

    // Viper C++
    public String returnViperValue;

    // Binding
    public TemplateBindingType returnBindingType;
}
```

### TemplateVecFunction

Corresponds to the definition of a `vec<elementType, size>`.

```java
public class TemplateVecFunction {
    // DSM
    public String dsmType;
    public String size;

    // Type
    public String type;
    public String typeSuffix;
    public String elementTypeSuffix;

    // Viper C++
    public String viperType;    // "TypeVec"
    public String viperValue;   // "ValueVec"

    // Binding
    public TemplateBindingType bindingType;
    public TemplateBindingType bindingElementType;
    public String bindingSequenceType;  // how the target writes this fixed-size sequence
}
```

For `vec<uint8, 2>`, `bindingSequenceType` is `tuple[int, int]` under `python` and
`number[]` under `typescript`.

### TemplateMatFunction

Corresponds to the definition of a `mat<elementType, columns, rows>`.

```java
public class TemplateMatFunction {
    // DSM
    public String dsmType;
    public String columns;
    public String rows;

    // Type
    public String type;
    public String typeSuffix;
    public String elementTypeSuffix;

    // Viper C++
    public String viperType;    // "TypeMat"
    public String viperValue;   // "ValueMat"

    // Binding
    public TemplateBindingType bindingType;
    public TemplateBindingType bindingElementType;
    public String bindingSequenceType;  // how the target writes this matrix: a sequence of columns
    public String bindingColumnType;    // how the target writes one of its columns
}
```

### TemplateType

One member of a `tuple` or a `variant`, carried in all three spaces.

```java
public class TemplateType {
    public String dsmType;                  // what the model calls it: uint8, Demo::StructureS
    public String type;                     // how the native target writes it
    public String typeSuffix;
    public TemplateBindingType bindingType; // how it appears through the binding
}
```

### TemplateTupleFunction

Corresponds to the definition of a `tuple<T0, ...>`.

```java
public class TemplateTupleFunction {
    // DSM
    public String dsmType;

    // Components
    public ArrayList<TemplateType> members;

    // Type
    public String type;
    public String typeSuffix;

    // Viper C++
    public String viperType;    // "TypeTuple"
    public String viperValue;   // "ValueTuple"

    // Binding
    public TemplateBindingType bindingType;
}
```

A member's binding spelling is `<v.members:{tm|<tm.bindingType.type>}>`, and its name for a
message is `<tm.dsmType>`.

### TemplateOptionalFunction

Corresponds to the definition of an `optional<elementType>`.

```java
public class TemplateOptionalFunction {
    // DSM
    public String dsmType;

    // Type
    public String type;
    public String typeSuffix;
    public String elementType;
    public String elementTypeSuffix;

    // Viper C++
    public String viperType;    // "TypeOptional"
    public String viperValue;   // "ValueOptional"

    // Binding
    public TemplateBindingType bindingType;
    public TemplateBindingType bindingElementType;
}
```

### TemplateVectorFunction

Corresponds to the definition of a `vector<elementType>`.

```java
public class TemplateVectorFunction {
    // DSM
    public String dsmType;

    public String valueRef;     // "&", or empty for vector<bool>

    // Type
    public String type;
    public String typeSuffix;
    public String elementTypeSuffix;

    // Viper C++
    public String viperType;    // "TypeVector"
    public String viperValue;   // "ValueVector"

    // Binding
    public TemplateBindingType bindingType;
    public TemplateBindingType bindingElementType;
}
```

### TemplateSetFunction

Corresponds to the definition of a `set<elementType>`.

```java
public class TemplateSetFunction {
    // DSM
    public String dsmType;

    // Type
    public String type;
    public String typeSuffix;
    public String elementTypeSuffix;

    // Viper C++
    public String viperType;    // "TypeSet"
    public String viperValue;   // "ValueSet"

    // Binding
    public TemplateBindingType bindingType;
    public TemplateBindingType bindingElementType;
}
```

### TemplateMapFunction

Corresponds to the definition of a `map<keyType, elementType>`.

```java
public class TemplateMapFunction {
    // DSM
    public String dsmType;

    // Type
    public String type;
    public String typeSuffix;
    public String keyTypeSuffix;
    public String elementTypeSuffix;

    // Viper C++
    public String viperType;    // "TypeMap"
    public String viperValue;   // "ValueMap"

    // Binding
    public TemplateBindingType bindingType;
    public TemplateBindingType bindingKeyType;
    public TemplateBindingType bindingElementType;
}
```

### TemplateVariantFunction

Corresponds to the definition of a `variant<T0, ...>`.

```java
public class TemplateVariantFunction {
    // DSM
    public String dsmType;

    // Components
    public ArrayList<TemplateType> members;

    // Type
    public String type;
    public String typeSuffix;

    // Viper C++
    public String viperType;    // "TypeVariant"
    public String viperValue;   // "ValueVariant"

    // Binding
    public TemplateBindingType bindingType;
}
```

### TemplateXArrayFunction

Corresponds to the definition of a `xarray<elementType>`.

```java
public class TemplateXArrayFunction {
    // DSM
    public String dsmType;

    // Type
    public String type;
    public String typeSuffix;
    public String elementType;
    public String elementTypeSuffix;

    // Viper C++
    public String viperType;    // "TypeXArray"
    public String viperValue;   // "ValueXArray"

    // Binding
    public TemplateBindingType bindingType;
    public TemplateBindingType bindingElementType;
}
```

## DSM Model

The DSM Model is the projection of the DSM definitions into a hierarchy of Java classes.

The pseudo-classes below express the public API that the StringTemplate engine consumes
when evaluating rule substitutions.

```{note}
These classes are **embedded** in the Template Model classes for basic introspection.
For example, `TemplateConcept.dsmConcept` gives access to the underlying `DSMConcept`.
A template reads public fields and getters only: a method such as `representation()` is not
reachable from a template. The Template Model carries what a template needs of it
(`dsmType`, `TemplateAttachment.representation`).
```

### DSMDefinitions

The root class references all the DSM definitions found in the `model.dsm.json`.

```java
public class DSMDefinitions {
    public ArrayList<DSMConcept> concepts;
    public ArrayList<DSMClub> clubs;
    public ArrayList<DSMEnumeration> enumerations;
    public ArrayList<DSMStructure> structures;
    public ArrayList<DSMAttachment> attachments;

    public ArrayList<DSMFunctionPool> functionPools;
    public ArrayList<DSMAttachmentFunctionPool> attachmentFunctionPools;
}
```

### TypeName and NameSpace

A qualified DSM name, and the namespace that qualifies it.

```java
public class TypeName {
    public String name;
    public NameSpace nameSpace;
    public String representation();                    // ModelA::Material
    public String representationIn(NameSpace context); // bare inside its own namespace,
                                                       // qualified from anywhere else
}

public class NameSpace {
    public UUID uuid;
    public String name;
}
```

```{note}
In kibo 2, `representationIn` answers from the name's own namespace: a type of another
namespace is now qualified. It used to return the bare name every time, which was only right
for a model with one namespace. `TemplateAttachment.representation` is built with it.
```

### DSMTypeReference

Used when a reference to another type is needed. For example, to express the list of
members of a `club`.

```java
public class DSMTypeReference extends DSMType {
    public TypeName typeName;
    public DSMTypeReferenceDomain domain;  // ANY, PRIMITIVE, CONCEPT, CLUB, ANY_CONCEPT,
                                           // ENUMERATION, STRUCTURE
}
```

### DSMConcept

Corresponds to the definition of a `concept`.

```java
public class DSMConcept {
    public TypeName typeName;
    public DSMTypeReference parent;
    public String documentation;
    public DSMTypeReference typeReference;
    public UUID runtimeId;
}
```

### DSMClub

Corresponds to the definition of a `club` with related `membership`.

```java
public class DSMClub {
    public TypeName typeName;
    public ArrayList<DSMTypeReference> members;
    public String documentation;
    public DSMTypeReference typeReference;
    public UUID runtimeId;
}
```

### DSMEnumeration

Corresponds to the definition of an `enum`.

```java
public class DSMEnumeration {
    public TypeName typeName;
    public ArrayList<DSMEnumerationCase> members;
    public String documentation;
    public DSMTypeReference typeReference;
    public UUID runtimeId;
}

public class DSMEnumerationCase {
    public String name;
    public String documentation;
}
```

### DSMStructure

Corresponds to the definition of a `struct` and provides access to the definition of the
structure fields.

```java
public class DSMStructure {
    public TypeName typeName;
    public ArrayList<DSMStructureField> fields;
    public String documentation;
    public DSMTypeReference typeReference;
    public UUID runtimeId;

    public String name;            // typeName.name
    public String representation;  // typeName.representation()
}

public class DSMStructureField {
    public String name;
    public DSMType type;
    public DSMLiteral defaultValue;
    public String documentation;
}
```

### DSMAttachment

Corresponds to the definition of an `attachment`.

```java
public class DSMAttachment {
    public TypeName typeName;
    public DSMTypeReference keyType;
    public DSMType documentType;
    public String documentation;
    public UUID runtimeId;

    public String identifier;      // <key type>.<attachment name>
}
```

### DSMLiteral

Used to express the literal value for the initialization of a field.

```java
public class DSMLiteral { }

public class DSMLiteralValue extends DSMLiteral {
    public DSMLiteralDomain domain;  // NONE, BOOLEAN, INTEGER, FLOAT, DOUBLE, STRING, UUID,
                                     // ENUMERATION_CASE
    public String value;
}

public final class DSMLiteralList extends DSMLiteral {
    public final ArrayList<DSMLiteral> members;
}
```

### DSMType

The base class of types.

```java
public abstract class DSMType {
    public abstract String representation();
    public abstract String representationIn(NameSpace nameSpace);
}
```

### DSMTypeKey

Corresponds to the definition of a `key<T>`.

```java
public class DSMTypeKey extends DSMType {
    public DSMTypeReference elementType;
}
```

### DSMTypeVec

Corresponds to the definition of a `vec<T, n>`.

```java
public class DSMTypeVec extends DSMType {
    public DSMTypeReference elementType;
    public long size;
}
```

### DSMTypeMat

Corresponds to the definition of a `mat<T, columns, rows>`.

```java
public class DSMTypeMat extends DSMType {
    public DSMTypeReference elementType;
    public long columns;
    public long rows;
}
```

### DSMTypeTuple

Corresponds to the definition of a `tuple<T0, ...>`.

```java
public class DSMTypeTuple extends DSMType {
    public ArrayList<DSMType> types;
}
```

### DSMTypeOptional

Corresponds to the definition of an `optional<T>`.

```java
public class DSMTypeOptional extends DSMType {
    public DSMType elementType;
}
```

### DSMTypeVector

Corresponds to the definition of a `vector<T>`.

```java
public class DSMTypeVector extends DSMType {
    public DSMType elementType;
}
```

### DSMTypeSet

Corresponds to the definition of a `set<T>`.

```java
public class DSMTypeSet extends DSMType {
    public DSMType elementType;
}
```

### DSMTypeMap

Corresponds to the definition of a `map<K, V>`.

```java
public class DSMTypeMap extends DSMType {
    public DSMType keyType;
    public DSMType elementType;
}
```

### DSMTypeVariant

Corresponds to the definition of a `variant<T0, ...>`.

```java
public class DSMTypeVariant extends DSMType {
    public ArrayList<DSMType> types;
}
```

### DSMTypeXArray

Corresponds to the definition of a `xarray<elementType>`.

```java
public class DSMTypeXArray extends DSMType {
    public DSMType elementType;
}
```

### DSMFunctionPool

Corresponds to the definition of a `function_pool`.

```java
public class DSMFunctionPool {
    public UUID uuid;
    public String name;
    public ArrayList<DSMFunction> functions;
    public String documentation;
}

public class DSMFunction {
    public DSMFunctionPrototype prototype;
    public String documentation;
}

public class DSMFunctionPrototype {
    public String name;
    public ArrayList<DSMFunctionPrototypeParameter> parameters;
    public DSMType returnType;
}

public class DSMFunctionPrototypeParameter {
    public String name;
    public DSMType type;
}
```

### DSMAttachmentFunctionPool

Corresponds to the definition of an `attachment_function_pool`.

```java
public class DSMAttachmentFunctionPool {
    public UUID uuid;
    public String name;
    public ArrayList<DSMAttachmentFunction> functions;
    public String documentation;
}

public class DSMAttachmentFunction {
    public boolean isMutable;
    public DSMFunctionPrototype prototype;
    public String documentation;
}
```
