# DSM & Definitions

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

The mirror of this page for the Python binding is {doc}`../../dsviper-python/api/dsm`; for a
narrative walkthrough see the {doc}`DSM guide <../dsm>`. The type classes referenced
by fields live on {doc}`types`.

Generated from the `@digitalsubstrate/dsviper` TypeScript declarations (`index.d.ts`) by TypeDoc.

## Source map

Pass a `DSMSourceMap` to `DSMBuilder.parse(sourceMap)` and the parser records, as a
by-product, the exact source span of every declaration, field, case, namespace, type
sub-expression and *resolved* type-reference. That is what makes a span-precise codemod
possible: patch a hand-authored `.dsm` in place under a transformation — file split,
comments and ordering preserved — instead of regenerating it. Opt-in: a `parse` without a
source map is unchanged.

```js
const { DSMBuilder, DSMSourceMap } = require('@digitalsubstrate/dsviper');

const sourceMap = new DSMSourceMap();
const [report, dsmDefs, defs] = DSMBuilder.assemble('model.dsm').parse(sourceMap);
```

## Parsing

```{js-summary}
DSMBuilder
DSMBuilderPart
DSMDefinitions
DSMDefinitionsInspector
DSMParseReport
DSMParseError
```

## Model Elements

```{js-summary}
DSMConcept
DSMClub
DSMStructure
DSMStructureField
DSMEnumeration
DSMEnumerationCase
DSMAttachment
```

## DSM Types

```{js-summary}
DSMType
DSMTypeKey
DSMTypeVector
DSMTypeSet
DSMTypeMap
DSMTypeXArray
DSMTypeOptional
DSMTypeTuple
DSMTypeVec
DSMTypeMat
DSMTypeVariant
DSMTypeReference
```

## Functions

```{js-summary}
DSMFunction
DSMFunctionPool
DSMFunctionPrototype
DSMAttachmentFunction
DSMAttachmentFunctionPool
```

## Literals

```{js-summary}
DSMLiteral
DSMLiteralValue
DSMLiteralList
```

## Definitions

```{js-summary}
Definitions
DefinitionsConst
DefinitionsCollector
DefinitionsInspector
DefinitionsExtendInfo
```

## Source Map

```{js-summary}
DSMSourceMap
DSMSourceSpan
DSMSourceDeclaration
DSMSourceField
DSMSourceCase
DSMSourceNameSpace
DSMSourceReference
DSMSourceType
```

## Reference

```{js:autoclass} DSMBuilder
:members:
```

```{js:autoclass} DSMBuilderPart
:members:
```

```{js:autoclass} DSMDefinitions
:members:
```

```{js:autoclass} DSMDefinitionsInspector
:members:
```

```{js:autoclass} DSMParseReport
:members:
```

```{js:autoclass} DSMParseError
:members:
```

```{js:autoclass} DSMConcept
:members:
```

```{js:autoclass} DSMClub
:members:
```

```{js:autoclass} DSMStructure
:members:
```

```{js:autoclass} DSMStructureField
:members:
```

```{js:autoclass} DSMEnumeration
:members:
```

```{js:autoclass} DSMEnumerationCase
:members:
```

```{js:autoclass} DSMAttachment
:members:
```

```{js:autoclass} DSMType
:members:
```

```{js:autoclass} DSMTypeKey
:members:
```

```{js:autoclass} DSMTypeVector
:members:
```

```{js:autoclass} DSMTypeSet
:members:
```

```{js:autoclass} DSMTypeMap
:members:
```

```{js:autoclass} DSMTypeXArray
:members:
```

```{js:autoclass} DSMTypeOptional
:members:
```

```{js:autoclass} DSMTypeTuple
:members:
```

```{js:autoclass} DSMTypeVec
:members:
```

```{js:autoclass} DSMTypeMat
:members:
```

```{js:autoclass} DSMTypeVariant
:members:
```

```{js:autoclass} DSMTypeReference
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

```{js:autoclass} DSMAttachmentFunction
:members:
```

```{js:autoclass} DSMAttachmentFunctionPool
:members:
```

```{js:autoclass} DSMLiteral
:members:
```

```{js:autoclass} DSMLiteralValue
:members:
```

```{js:autoclass} DSMLiteralList
:members:
```

```{js:autoclass} Definitions
:members:
```

```{js:autoclass} DefinitionsConst
:members:
```

```{js:autoclass} DefinitionsCollector
:members:
```

```{js:autoclass} DefinitionsInspector
:members:
```

```{js:autoclass} DefinitionsExtendInfo
:members:
```

```{js:autoclass} DSMSourceMap
:members:
```

```{js:autoclass} DSMSourceSpan
:members:
```

```{js:autoclass} DSMSourceDeclaration
:members:
```

```{js:autoclass} DSMSourceField
:members:
```

```{js:autoclass} DSMSourceCase
:members:
```

```{js:autoclass} DSMSourceNameSpace
:members:
```

```{js:autoclass} DSMSourceReference
:members:
```

```{js:autoclass} DSMSourceType
:members:
```
