# Tutorial

This tutorial walks through a complete example from Node.js: loading a data
model, seeding a database, and performing a full write / read / history cycle
with `CommitDatabase`. It is the Node twin of the Python
{doc}`../dsviper/tutorial`.

> **Prerequisites**: This tutorial assumes you have read {doc}`dsm` and
> understand the `assemble → parse → introspect` workflow, plus the
> {doc}`database` lifecycle (stage → commit → reconstruct).

```js
const {
  DSMBuilder, DefinitionsInspector,
  CommitDatabase, CommitMutableState, CommitStateBuilder, Path,
} = require('@digitalsubstrate/dsviper');
```

## The User/Login Model

We'll use a simple model with Users who have Login credentials and Identity
information.

### Step 1: Define the Data Model

Create a file `model.dsm`:

```{literalinclude} ../_fixtures/Tuto/model.dsm
:language: dsm
```

### Step 2: Validate the Model

Parsing both validates the syntax and hands back the runtime definitions. Always
check the report before trusting the result:

```js
const [report, dsmDefs, defs] = DSMBuilder.assemble('model.dsm').parse();
report.hasError(); // false
```

`defs` is a `DefinitionsConst` — the immutable runtime snapshot, ready for a
database to adopt.

### Step 3: Create a Database

Unlike the Python flow — which builds a `.cdb` file up front with `dsm_util` —
the Node lifecycle creates the store in process and extends it with the
definitions you just parsed:

```js
const db = CommitDatabase.createInMemory();
db.extendDefinitions(defs);
defs.isEqual(db.definitions()); // true
```

### Step 4: Open and Explore

A `DefinitionsInspector` lists the types and attachments the database carries:

```js
const insp = new DefinitionsInspector(defs);

insp.conceptTypeNames().map(String);     // ['Tuto::User']
insp.enumerationTypeNames().map(String); // ['Tuto::Status']
insp.structureTypeNames().map(String);
// ['Tuto::Account', 'Tuto::Identity', 'Tuto::Login', 'Tuto::Texture', 'Tuto::Thumbnail']

insp.attachmentIdentifiers();
// ['Tuto::User.account', 'Tuto::User.avatar', 'Tuto::User.identity',
//  'Tuto::User.login', 'Tuto::User.portrait']
```

### Step 5: Look Up the Attachment

```{note}
**No constant injection.** The Python API can `inject()` types as constants
into the caller's namespace (`TUTO_A_USER_LOGIN`). Node has no such global
injection: you look a type or attachment up explicitly, by its identifier, from
the inspector. The identifier strings are exactly the ones
`attachmentIdentifiers()` returns.
```

```js
const login_att = insp.queryAttachment('Tuto::User.login');
login_att.keyType().typeName().name();      // 'User'
login_att.documentType().typeName().name(); // 'Login'
```

`query*` returns `undefined` on a miss; use `check*` (e.g. `insp.checkAttachment`)
when you want a `ViperError` thrown instead.

### Step 6: Create a Key and Document

Create a key for a new User. `instanceId()` returns the underlying UUID
(randomly generated):

```js
const key = login_att.createKey();
key.instanceId().isValid(); // true
```

Create a Login document and fill its fields. Structures have no attribute
protocol — read with `.at()`, write with `.assign()` (a batch setter that
returns the structure) or `.set(field, value)` for a single field:

```js
const login = login_att.createStructure({ nickname: '', password: '' });
login.at('nickname'); // ''

login.assign({ nickname: 'zoop', password: 'robust' });
login.at('nickname'); // 'zoop'
```

### Step 7: Commit to Database

Stage the document against the key on a mutable state, then seal the batch into
a commit:

```js
const state = new CommitMutableState(CommitStateBuilder.initialState(db));
state.attachmentMutating().set(login_att, key, login);

const commitId = db.commitMutations('First Commit', state);
String(commitId).length;          // 40  (a ValueCommitId)
db.lastCommitId().equals(commitId); // true
```

```{note}
**Scope of this tutorial**

The single-author flow shown here does not exercise the reduction behaviour
described in {doc}`../commit/index`: with one author committing in sequence,
mutations are never silently dropped and no last-writer-wins arbitration takes
place. The contract becomes load-bearing once **several authors' writes are
reduced automatically** — see {doc}`../commit/commit_modes` for the diagnostic
and which mode applies to your application.
```

### Step 8: Read from Database

A read is a *reconstruction*: `CommitStateBuilder.state` replays the mutation
trace up to a commit and hands you an immutable snapshot. `get` returns a
`ValueOptional` — `.unwrap()` peels it to the document:

```js
const s = CommitStateBuilder.state(db, commitId);
const result = s.attachmentGetting().get(login_att, key);

result.isNil();             // false
result.unwrap().at('nickname'); // 'zoop'
```

Value semantics are Java-like: compare documents with `.equals()`, never with
`==` between two Values (that is reference equality).

### Step 9: Update a Field

Update one location through a `Path` rather than re-setting the whole document.
Capture the new commit id that `commitMutations` returns — reads always address
an explicit commit, so chaining requires the id:

```js
const next = new CommitMutableState(CommitStateBuilder.state(db, commitId));
next.attachmentMutating().update(login_att, key, new Path().field('nickname').const(), 'zoopy');

const updatedId = db.commitMutations('Update Nickname', next);
```

### Step 10: View History

Each commit is a point in the history; reconstruct the state at any of them:

```js
CommitStateBuilder.state(db, updatedId)
  .attachmentGetting().get(login_att, key).unwrap().at('nickname'); // 'zoopy'

CommitStateBuilder.state(db, commitId)
  .attachmentGetting().get(login_att, key).unwrap().at('nickname'); // 'zoop'

// Before any write, the document is absent:
CommitStateBuilder.initialState(db)
  .attachmentGetting().get(login_att, key).isNil(); // true
```

### Step 11: Inspect Commit Headers

```js
const header = db.commitHeader(updatedId);
header.label();                          // 'Update Nickname'
header.parentCommitId().equals(commitId); // true
```

---

The walkthrough above uses the **dynamic API** (definitions loaded at runtime).
The same operations are available through the **static API** — a typed
TypeScript package generated from the model by Kibo, catalogued under
{doc}`../kibo-template-viper/features`. See {doc}`../ecosystem/value-chains` for
the contrast.
