# DSM & definitions

This bucket holds the two ways to obtain runtime definitions: build them in code
with {js:class}`Definitions`, or parse them from `.dsm` source with
{js:class}`DSMBuilder`. Both yield the same kind of registry — concepts, clubs,
enumerations, structures and attachments — that the rest of the runtime resolves
types against. The `DSM*` classes additionally model the parsed declarations
themselves (a {js:class}`DSMStructure`, its {js:class}`DSMStructureField`s, and so
on) for introspection.

**When to use**: reach for {js:class}`Definitions` to assemble a schema
programmatically (registering types one call at a time); reach for
{js:class}`DSMBuilder` to load and introspect an existing model file. Wrap either
result in a {js:class}`DefinitionsInspector` (or {js:class}`DSMDefinitionsInspector`)
to query types by name.

```{note}
The static (code-generation) path that turns a parsed model into a typed module
ships in a later release. This page covers the runtime introspection surface only.
```

## Quick Start

Build a `Definitions` registry in code:

```js
const {
  Definitions, NameSpace, ValueUUId, Type,
  TypeEnumerationDescriptor, TypeStructureDescriptor,
  DefinitionsInspector,
} = require('@digitalsubstrate/dsviper');

const defs = new Definitions();
const ns = new NameSpace(ValueUUId.create(), 'Game');

// Concepts and clubs
const player = defs.createConcept(ns, 'Player', 'a participant');
const team = defs.createClub(ns, 'Team');
defs.createMembership(team, player);

// An enumeration, described then registered
const levelDesc = new TypeEnumerationDescriptor('Level');
levelDesc.addCase('beginner');
levelDesc.addCase('expert');
const level = defs.createEnumeration(ns, levelDesc);

// A structure, described field by field
const propsDesc = new TypeStructureDescriptor('Props', 'player properties');
propsDesc.addField('name', Type.STRING);
propsDesc.addField('score', Type.INT64);
const props = defs.createStructure(ns, propsDesc);

// An attachment keys a document type onto a concept
defs.createAttachment(ns, 'props', player, props);

// Inspect the assembled registry
const insp = new DefinitionsInspector(defs.const());
insp.structureTypeNames();              // [ TypeName('Props') ]
insp.checkStructure(props.typeName());  // -> TypeStructure (throws if absent)
```

Or parse a `.dsm` model and introspect the result:

```js
const { DSMBuilder } = require('@digitalsubstrate/dsviper');

// assemble(path) loads a file or a directory of .dsm files; or append() in code
const builder = DSMBuilder.assemble('model.dsm');
const [report, dsm, defs] = builder.parse();

// Always check the report before using the definitions
if (report.hasError()) {
  for (const err of report.errors()) console.error(err.message());
  throw new Error('DSM parse failed');
}

// Walk the parsed declarations
for (const struct of dsm.structures()) {
  console.log(`struct ${struct.typeName().name()}`);
  for (const field of struct.fields()) {
    console.log(`  ${field.name()}: ${field.type().typeName().name()}`);
  }
}
```

A parse error is reported through the {js:class}`DSMParseReport`, not thrown; a
runtime failure (an unknown type, a duplicate case) surfaces as a JS `Error` whose
`.name` is `'ViperError'`.

## Choosing an entry point

| Goal | Start with | Then |
|------|-----------|------|
| Assemble a schema in code | {js:class}`Definitions` | `createConcept` / `createClub` / `createEnumeration` / `createStructure` / `createAttachment` |
| Load a schema from `.dsm` | {js:class}`DSMBuilder` | `assemble(path)` / `append(name, src)`, then `parse()` |
| Query types by name | {js:class}`DefinitionsInspector` | `query*` (returns the type or `undefined`) / `check*` (throws on miss) |
| Introspect a parsed model | {js:class}`DSMDefinitions` | `structures()` / `concepts()` / `enumerations()` / `attachments()` |

The mirror of this page for the Python binding is {doc}`../../dsviper/api/dsm`; for a
narrative walkthrough see the {doc}`DSM guide <../dsm>`. The type classes referenced
by fields live on {doc}`types`.

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Summary

| Class | Description |
|-------|-------------|
| {js:class}`DSMAttachment` | A class used to represent the definition of an attachment |
| {js:class}`DSMAttachmentFunction` | A class used to represent the definition of an attachment function |
| {js:class}`DSMAttachmentFunctionPool` | A class used to represent the definition of an attachment function pool |
| {js:class}`DSMBuilder` | A class used to assemble a collection of DSM Definitions from various sources |
| {js:class}`DSMBuilderPart` | A class used to represent a part of the assembled definitions |
| {js:class}`DSMClub` | A class used to represent the definition of a club |
| {js:class}`DSMConcept` | A class used to represent the definition of a concept |
| {js:class}`DSMDefinitions` | A class used to represent DSM definitions |
| {js:class}`DSMDefinitionsInspector` | DSMDefinitionsInspector(definitions) |
| {js:class}`DSMEnumeration` | A class used to represent the definition of an enum |
| {js:class}`DSMEnumerationCase` | A class used to represent the definition of a case for an enum |
| {js:class}`DSMFunction` | A class used to represent the definition of a function |
| {js:class}`DSMFunctionPool` | A class used to represent the definition of a function pool |
| {js:class}`DSMFunctionPrototype` | A class used to represent the definition of a function prototype |
| {js:class}`DSMLiteral` |  |
| {js:class}`DSMLiteralList` | A class used to represent the definition of a literal list |
| {js:class}`DSMLiteralValue` | A class used to represent the definition of a literal value |
| {js:class}`DSMParseError` | A class used to represent a parse error |
| {js:class}`DSMParseReport` | A class used to collect the error occurred while parsing the assembled definitions |
| {js:class}`DSMStructure` | A class used to represent the definition of a struct |
| {js:class}`DSMStructureField` | A class used to represent the definition of a field for a struct |
| {js:class}`DSMType` |  |
| {js:class}`DSMTypeKey` | A class used to represent the type key<element_type> |
| {js:class}`DSMTypeMap` | A class used to represent the type map<key_type, element_type> |
| {js:class}`DSMTypeMat` | A class used to represent the type vec<element_type, columns, rows> |
| {js:class}`DSMTypeOptional` | A class used to represent the type optional<element_type> |
| {js:class}`DSMTypeReference` | A class used to represent a reference to a type |
| {js:class}`DSMTypeSet` | A class used to represent the type set<element_type> |
| {js:class}`DSMTypeTuple` | A class used to represent the type tuple<T0, ...> |
| {js:class}`DSMTypeVariant` | A class used to represent the type variant<T0, ...> |
| {js:class}`DSMTypeVec` | A class used to represent the type vec<element_type, size> |
| {js:class}`DSMTypeVector` | A class used to represent the type vector<element_type> |
| {js:class}`DSMTypeXArray` | A class used to represent the type xarray<element_type> |
| {js:class}`Definitions` | A class used to register concept, club, enumeration, structure and attachment |
| {js:class}`DefinitionsCollector` | A class used to collect referenced types |
| {js:class}`DefinitionsConst` | A class used to retrieve registered concepts, clubs, enumerations, structures and attachments |
| {js:class}`DefinitionsExtendInfo` | A class used to represent the types exchanged during the synchronization of two databases |
| {js:class}`DefinitionsInspector` | DefinitionsInspector(definitions) |
| {js:class}`DefinitionsMapper` | A class use for INTERNAL DEVELOPMENT |

## Reference

```{js:autoclass} DSMAttachment
:members:
```

```{js:autoclass} DSMAttachmentFunction
:members:
```

```{js:autoclass} DSMAttachmentFunctionPool
:members:
```

```{js:autoclass} DSMBuilder
:members:
```

```{js:autoclass} DSMBuilderPart
:members:
```

```{js:autoclass} DSMClub
:members:
```

```{js:autoclass} DSMConcept
:members:
```

```{js:autoclass} DSMDefinitions
:members:
```

```{js:autoclass} DSMDefinitionsInspector
:members:
```

```{js:autoclass} DSMEnumeration
:members:
```

```{js:autoclass} DSMEnumerationCase
:members:
```

```{js:autoclass} DSMFunction
:members:
```

```{js:autoclass} DSMFunctionPool
:members:
```

```{js:autoclass} DSMFunctionPrototype
:members:
```

```{js:autoclass} DSMLiteral
:members:
```

```{js:autoclass} DSMLiteralList
:members:
```

```{js:autoclass} DSMLiteralValue
:members:
```

```{js:autoclass} DSMParseError
:members:
```

```{js:autoclass} DSMParseReport
:members:
```

```{js:autoclass} DSMStructure
:members:
```

```{js:autoclass} DSMStructureField
:members:
```

```{js:autoclass} DSMType
:members:
```

```{js:autoclass} DSMTypeKey
:members:
```

```{js:autoclass} DSMTypeMap
:members:
```

```{js:autoclass} DSMTypeMat
:members:
```

```{js:autoclass} DSMTypeOptional
:members:
```

```{js:autoclass} DSMTypeReference
:members:
```

```{js:autoclass} DSMTypeSet
:members:
```

```{js:autoclass} DSMTypeTuple
:members:
```

```{js:autoclass} DSMTypeVariant
:members:
```

```{js:autoclass} DSMTypeVec
:members:
```

```{js:autoclass} DSMTypeVector
:members:
```

```{js:autoclass} DSMTypeXArray
:members:
```

```{js:autoclass} Definitions
:members:
```

```{js:autoclass} DefinitionsCollector
:members:
```

```{js:autoclass} DefinitionsConst
:members:
```

```{js:autoclass} DefinitionsExtendInfo
:members:
```

```{js:autoclass} DefinitionsInspector
:members:
```

```{js:autoclass} DefinitionsMapper
:members:
```
