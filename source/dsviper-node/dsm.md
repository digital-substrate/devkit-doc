# DSM Processing

This chapter covers building runtime definitions in memory and loading DSM
(Digital Substrate Model) files from Node.js. This is the **dynamic path**: the
type universe is constructed or parsed at runtime, with no code generation. The
**static path** — importing a typed TypeScript package produced by Kibo — is a
separate route, planned for a later release.

This is the Node twin of the Python {doc}`../dsviper/dsm` page.

```js
const {
  Definitions, NameSpace, ValueUUId, Type,
  TypeStructureDescriptor, TypeEnumerationDescriptor,
} = require('@digitalsubstrate/dsviper');
```

## Building Definitions in Memory

`Definitions` is the runtime registry of the type universe. You add types to it
directly, then freeze the result with `const()` — an immutable snapshot that a
database adopts or that you introspect and serialize.

```{tip}
Every namespaced type lives under a `NameSpace`, built from a fresh UUID and a
name: `new NameSpace(ValueUUId.create(), 'Tuto')`.
```

### Concepts

A concept is an identity type. `createConcept` returns its runtime handle:

```js
const ns = new NameSpace(ValueUUId.create(), 'Tuto');
const defs = new Definitions();

const user = defs.createConcept(ns, 'User', 'A user.');
user.typeName().name();        // 'User'
user.documentation();          // 'A user.'
user.parent();                 // undefined — no parent
```

Pass a parent concept as the fourth argument to declare inheritance:

```js
const admin = defs.createConcept(ns, 'Admin', '', user);
admin.parent().equals(user);   // true
```

### Clubs and Memberships

A club groups concepts. Add members with `createMembership`:

```js
const a = defs.createConcept(ns, 'A');
const b = defs.createConcept(ns, 'B');
const club = defs.createClub(ns, 'Group', 'A grouping.');

defs.createMembership(club, a);
defs.createMembership(club, b);

club.members().length;         // 2
club.isMember(a);              // true
```

### Enumerations

Describe an enumeration with a `TypeEnumerationDescriptor`, then register it.
Each case is added with `addCase(name, documentation?)`; a duplicate case name
throws:

```js
const de = new TypeEnumerationDescriptor('Status', 'Account status.');
de.addCase('pending', 'Awaiting activation.');
de.addCase('active');

const status = defs.createEnumeration(ns, de);
status.cases().length;             // 2
status.cases()[0].name();          // 'pending'
status.cases()[0].documentation(); // 'Awaiting activation.'
```

### Structures

Describe a structure with a `TypeStructureDescriptor` and `addField`. A field
takes either a `Type` or a default value (which fixes both the field type and
its default):

```js
const { TypeVector, ValueVector } = require('@digitalsubstrate/dsviper');

const ds = new TypeStructureDescriptor('Login', 'Login record.');
ds.addField('nickname', Type.STRING);
ds.addField('tags', new ValueVector(new TypeVector(Type.INT64), [1n, 2n, 3n]));

const login = defs.createStructure(ns, ds);
login.fields().length;                 // 2
login.fields()[1].name();              // 'tags'
[...login.fields()[1].defaultValue()]; // [1n, 2n, 3n]  (INT64 → bigint)
```

```{note}
Structures have no attribute protocol: there is no `value.tags`. Construct and
read structure values via object construction and `.at` / `.set` — see
{doc}`structures`.
```

### Attachments

An attachment is a typed map from a key type to a document type. The key type is
a concept, a club, or a built-in abstraction such as `Type.ANY_CONCEPT`; the
document type is any `Type`:

```js
const login_att = defs.createAttachment(ns, 'login', user, login);
login_att.keyType().equals(user);          // true
login_att.documentType().equals(login);    // true

// A concept-agnostic attachment keyed by ANY_CONCEPT, holding an INT64:
const score = defs.createAttachment(ns, 'score', Type.ANY_CONCEPT, Type.INT64);
```

### Freezing and Seeding a Database

`const()` returns the immutable snapshot. A database adopts it via
`extendDefinitions`:

```js
const { CommitDatabase } = require('@digitalsubstrate/dsviper');

const constDefs = defs.const();        // DefinitionsConst

const db = CommitDatabase.createInMemory();
db.extendDefinitions(constDefs);
constDefs.isEqual(db.definitions());   // true
db.close();
```

See {doc}`database` for the full write/read lifecycle that follows.

## Loading DSM Files

`DSMBuilder.assemble(path)` reads a `.dsm` file (or a directory of them, parsed
as one unit). `parse()` validates syntax and semantics and returns a triple:

```js
const { DSMBuilder } = require('@digitalsubstrate/dsviper');

const [report, dsmDefs, defs] = DSMBuilder.assemble('model.dsm').parse();
report.hasError();   // false
```

| Return Value | Type               | Description                           |
|--------------|--------------------|---------------------------------------|
| `report`     | `DSMParseReport`   | Errors and warnings                   |
| `dsmDefs`    | `DSMDefinitions`   | Structured DSM data                   |
| `defs`       | `DefinitionsConst` | Runtime definitions (ready to adopt)  |

### Handling Errors

`report.errors()` yields the diagnostics; iterate before trusting `dsmDefs` or
`defs`:

```js
const [report, dsmDefs, defs] = DSMBuilder.assemble('model.dsm').parse();
if (report.hasError()) {
  for (const error of report.errors()) {
    console.error(error.message());
  }
} else {
  console.log('Parse successful!');
}
```

A parsed `DSMDefinitions` converts to a runtime snapshot at any point with
`toDefinitions()`, the bridge between the structured form and the runtime
registry:

```js
const runtime = dsmDefs.toDefinitions();   // a DefinitionsConst
```

## DSM Introspection

`DSMDefinitions` exposes the parsed model as structured collections —
`concepts()`, `clubs()`, `enumerations()`, `structures()`, `attachments()`,
plus `functionPools()` and `attachmentFunctionPools()`.

### Concepts

```js
const concept = dsmDefs.concepts()[0];
concept.typeName().name();     // e.g. 'User'
concept.documentation();
concept.parent();              // a DSMTypeReference, or undefined at the root
concept.runtimeId();
```

For a model with inheritance, `parent()` returns a `DSMTypeReference` to the
parent concept; follow `parent().typeName().name()` up the chain.

### Structures and Fields

```js
const struct = dsmDefs.structures().find(s => s.typeName().name() === 'Login');
struct.fields().map(f => f.name());      // ['nickname', 'password']

const field = struct.fields()[0];
field.name();                            // 'nickname'
field.type().typeName().name();          // 'string'
field.documentation();
field.defaultValue();                    // a DSMLiteralValue
```

A field's `type()` is a `DSMType`. Primitives and named types come back as
`DSMTypeReference` (read `type.typeName().name()`); container types are distinct
subclasses you can branch on with `instanceof`:

```js
const { DSMTypeVector, DSMTypeMap, DSMTypeKey } = require('@digitalsubstrate/dsviper');

const t = field.type();
if (t instanceof DSMTypeVector) {
  t.elementType().typeName().name();     // the element type
} else if (t instanceof DSMTypeMap) {
  t.keyType().typeName().name();         // map key
  t.elementType().typeName().name();     // map value
} else if (t instanceof DSMTypeKey) {
  t.elementType().typeName().name();     // the referenced concept/club
}
```

Other container wrappers include `DSMTypeSet`, `DSMTypeOptional`,
`DSMTypeTuple` and `DSMTypeVariant` (`.types()` over their members),
`DSMTypeXArray`, and the math types `DSMTypeVec` (`.size()`) and `DSMTypeMat`
(`.rows()` / `.columns()`). Container element types nest, so a
`vector<vector<int64>>` is a `DSMTypeVector` whose `elementType()` is another
`DSMTypeVector`.

### Enumerations

```js
const enumeration = dsmDefs.enumerations()[0];
enumeration.typeName().name();                  // e.g. 'Status'
enumeration.members().map(c => c.name());       // ['pending', 'active', 'completed']
enumeration.members()[0].documentation();
```

### Clubs

```js
const club = dsmDefs.clubs()[0];
club.members().map(m => m.typeName().name());   // member concept names
```

### Attachments

```js
const att = dsmDefs.attachments()[0];
att.identifier();                  // a string id that round-trips queryAttachment
att.keyType();                     // a DSMType
att.documentType();                // a DSMType
```

## Inspecting Runtime Definitions

`DefinitionsInspector` wraps a `DefinitionsConst` snapshot and answers
type-name / identifier queries without rebuilding anything:

```js
const { DefinitionsInspector } = require('@digitalsubstrate/dsviper');

const insp = new DefinitionsInspector(defs);   // defs is a DefinitionsConst

insp.conceptTypeNames();           // array of TypeName
insp.clubTypeNames();
insp.enumerationTypeNames();
insp.structureTypeNames();
insp.attachmentIdentifiers();      // array of attachment id strings
insp.nameSpaces();                 // array of NameSpace
```

Lookups come in two flavours. `query*` returns the type or `undefined` on a
miss; `check*` throws a `ViperError` on a miss:

```js
const { TypeConcept } = require('@digitalsubstrate/dsviper');

const c = insp.queryConcept(someTypeName);   // TypeConcept | undefined
c instanceof TypeConcept;                    // true on a hit

insp.queryEnumeration(conceptTypeName);      // undefined — not an enumeration
insp.checkConcept(someTypeName);             // returns the type, or throws

// Attachments are addressed by an identifier string from attachmentIdentifiers():
insp.queryAttachment(insp.attachmentIdentifiers()[0]);  // an Attachment
insp.queryAttachment('NOPE');                // undefined
```

`representation(typeName)` renders a type to a readable string. The same
`query*` / `check*` pair (keyed by runtime id rather than type name) is also
available directly on `DefinitionsConst`.

## Serialization

`DSMDefinitions` can be serialized for distribution and round-trips losslessly.

### JSON

The canonical on-disk form consumed by Kibo and `dsm_util`. `jsonEncode()`
returns a string; `DSMDefinitions.jsonDecode(str)` rebuilds it. Encode → decode
→ re-encode is byte-stable:

```js
const { DSMDefinitions } = require('@digitalsubstrate/dsviper');

const json = dsmDefs.jsonEncode();
const restored = DSMDefinitions.jsonDecode(json);
restored.jsonEncode() === json;             // true

DSMDefinitions.jsonDecode('invalid json{{{'); // throws a ViperError
```

A malformed payload throws a `ViperError` whose message quotes a JSON path
locating the offending node (e.g. `structures[2].fields[0].type`).

### Binary and BSON

`encode()` returns a compact binary `ValueBlob` (`DSMDefinitions.decode(blob)`
restores it); `bsonEncode()` / `bsonDecode()` is the BSON equivalent. All three
codecs cross-convert — a binary blob decoded and re-emitted as JSON matches a
direct JSON encode:

```js
const blob = dsmDefs.encode();              // a ValueBlob
DSMDefinitions.decode(blob).jsonEncode() === dsmDefs.jsonEncode();  // true
```

The runtime registry itself also has a binary codec: `defs.encode()` returns a
blob and `Definitions.decode(blob)` restores a `Definitions`.

### Generating DSM Text

`toDsm()` reconstructs DSM source from a parsed model. It takes positional
booleans — `toDsm(showDocumentation, showRuntimeId, html)`:

```js
dsmDefs.toDsm();                  // default render
dsmDefs.toDsm(true, true, false); // append // Runtime ID comments
dsmDefs.toDsm(true, false, true); // HTML-wrapped output
```

A fourth argument filters the rendered attachment set to a given array of
`DSMAttachment`s; passing a non-array or a non-attachment element throws.
```
