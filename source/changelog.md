# Release notes

User-facing release notes for the Viper runtime and the two `dsviper` bindings, and for
the code generator that targets them, kibo, with its template pack.

There is **one runtime contract** — Viper C++ on the `1.2` line (`MAJOR.MINOR`) —
delivered through **two installable packages**, each with its **own independent
`PATCH` stream**:

- **dsviper for Python** — the wheel on PyPI (`pip install dsviper`)
- **@digitalsubstrate/dsviper** — the Node.js binding on npm

See {doc}`ecosystem/naming` for how these names relate. The Viper C++ runtime is
**not installed on its own** — it ships inside both packages; each binding entry
notes the runtime version it carries. Only released versions are listed, and
**breaking** changes are flagged inline.

## What LTS-1.2 guarantees

The label was applied early. The line was still in late alpha when it went on,
and additions were still arriving four months after it. What follows is what the
commitment covers — narrower than the name suggests, and the part that has held.

**Three things are frozen for the life of the line.** The **type and value
system** — `Definitions`, `Type`, `Value` and the relations between them: a model
that types correctly on one `1.2.x` types correctly on every later one. **DSM
governance** — what a `.dsm` may declare, and the rules deciding whether a set of
definitions is expressible. And the **on-disk format**: a database written by any
`1.2.x` is readable by any other. No migration is needed inside the line, and none
is offered.

**Patches are a quality programme, not a feature stream.** What a patch carries
is a defect closed — a docstring describing what the code does not do, a guard
that never fired, a value that could be corrupted. The rule has not been
absolute: a third serialization dialect arrived in July, two months past the
lock, and that is a feature by any reading. A patch may also break something,
and each time that is a severity judgement — leaving a data-corrupting API in
place under a deprecation was judged the worse trade every time. Both kinds are
listed below and breaks are flagged inline, so neither claim rests on being
believed.

**The freeze is what opened the ecosystem.** Viper was one private repository
holding the runtime and every tool built on it. On a single day in May 2026, seven
repositories were created out of it — `kibo`, `kibo-template-viper`, and the
`dsviper-*` tools and sample applications — each with its own changelog, its own
version, and a surface someone outside can read. The per-artifact changelogs did
not precede that split; they were written during it. What came next is the part
that counts: `dsviper-jsonrpc`, `dsviper-query` and `dsviper-database-tools` were
written *after* the lock, in pure Python over the published binding and nothing
else — one of them on top of another. A contract you can build new work on is the
only evidence that freezing it was worth doing.

**Semantic versioning is operational everywhere except the runtime.** Every
satellite versions itself strictly and independently: `dsviper-query` is at 0.1.0,
`dsviper-database-tools` at 0.2.4, and neither number tracks `1.2`. Viper does not
yet — it is the runtime, it is still stabilising, and the breaking changes listed
below are what that looks like.

## Code generation — kibo 2.0 and kibo-template-viper 2.0

Kibo and its template pack version themselves on their own: their `2.0.0` is a
generator line, not a runtime one. Both generate over the **1.2 runtime** described on
this page, which does not change; kibo 1.2 and the 1.2 pack stay supported on their
`LTS-1.2` line, documented in the 1.2 version of this site. The full lists are the two
repositories' CHANGELOGs:
[kibo](https://github.com/digital-substrate/kibo/blob/main/CHANGELOG.md),
[kibo-template-viper](https://github.com/digital-substrate/kibo-template-viper/blob/main/CHANGELOG.md).

### kibo 2.0.0 — 2026-10-05

- **Template Model 2.** The accessors that describe a type as a binding sees it are
  renamed (`pythonType` → `bindingType`, …) and answer for the target being generated;
  every entity carries its DSM name, `dsmType`. **Breaking** for a template pack: a
  Model 1 pack does not render until migrated, and some values read differently under the
  same accessors — a C++ type names its namespace in lower snake case, a container class
  is named after what it holds — so a migrated pack's output changes too; each change is
  listed in {doc}`kibo/migrating`.
- **`--converter` selects a target** — `cpp`, `python` or `typescript` — and kibo knows
  how each binding spells the DSM types.
- **A template renders once per scope it declares**: `model(m)` once, `unit(u)` once per
  DSM namespace, `pool(p)` and `attachment_pool(p)` once per pool, beside `main(m)`. A
  namespace carries what it needs to be generated on its own: its dependencies, its
  include guard, its attachments grouped by concept.
- **Formats** carry a model's documentation into generated code (`string`, `docstring`,
  `comment`), and one snake_case rule names static symbols (`snake`, `usnake`).
- **A model whose outputs would collide is refused before rendering**, and a template
  that reads a name the model does not carry is reported on stderr.
- **kibo-project** drives a project's generation from a `kibo.toml`, in place of each
  project's `generate.py` — {doc}`kibo/kibo-project`.

### kibo-template-viper 2.0.0 — 2026-10-05

Requires kibo 2. Targets `dsviper >= 1.2.29`, `@digitalsubstrate/dsviper >= 1.2.14` and a
`viper` C++ runtime that carries its static layer. **Breaking**: the generated surface
changes throughout, and code written against the 1.2 output needs migrating —
{doc}`using-generated-sdk/migrating`.

- **One DSM namespace is one unit**: a C++ namespace and file prefix, a Python module, a
  TypeScript directory. Types lose their namespace prefix, and two namespaces may
  declare the same name.
- **A project selects features** from `features.json`, and the dependencies follow —
  {doc}`kibo-template-viper/features`.
- **Python and TypeScript are proxies over the runtime**: a proxy is a box around one
  Viper value, with its type and the bridge `wrap_value` / `unwrap_value`
  (`wrapValue` / `unwrapValue`); containers are declared classes named by their shape
  (`Vector_of_uint8`); keys follow the runtime's model, one instance seen through many
  views; errors follow the binding's three layers. The two packages expose the same
  surface, member by member, each in its language's idiom —
  {doc}`kibo-template-viper/parity`.
- **Attachments are objects**, grouped by the concept they are keyed on, in every target.
- **The generated Python is fully annotated**, its runtime included, and the generated
  TypeScript compiles under `--strict`.
- **The generated C++ goes through the runtime's static layer** to cross to a `Value`,
  to serialize and to hash; `Stream`, `ValueCodec`, `Json`, `ValueHasher`, `Database` and
  the generated attachment pool are removed, their work done by the runtime.
- **Function pools use the DSM spelling** for their functions, in C++ and on the wire;
  each language keeps its idiom for the static names. `Pool` is the server side,
  `PoolRemote` the client side.
- **Added**: `Fields` (C++), every field's name and path as constants; `Package`
  (TypeScript), a ready-to-build npm package.

## Viper C++ runtime

The engine shipped inside both bindings; `viperVersion()` reports this version.
Binding- or packaging-only releases are omitted — except a *phantom* version (a runtime
number minted with no runtime change, from a lockstep bump), listed to explain the gap.

### 1.2.28 — 2026-10-04

**Changed (breaking)**

- Enumeration values order by their definition, as a C++ enum class does: they ordered by case name. A set or a map keyed by an enumeration iterates, encodes and hashes in that order; stored data reads unchanged.

**Changed**

- `ValueXArray::append` returns the position it created, as `insert` does; it returned END, which named no element. `extend` still returns END.
- A remote attachment function that only reads takes an `AttachmentGetting`: `ServiceRemote::call` widens from `AttachmentMutating`. A function that mutates, given a state that only reads, is refused with `ServiceErrors::ReadOnlyState`. The wire is unchanged.
- A default mat is all zeros, as a vec, a number and generated C++ are: `Value::create` built the identity. `ValueMat::make(typeMat, identity)` still builds it on request. Data written before reads back unchanged.
- A default key of a concept names that concept, as generated C++ does; a key of a club or of `any_concept` still names none. Data written before reads back unchanged; test an unset key with `is_valid()`, not by comparison.

**Added**

- The static side of the dual reality, for C++ code that holds a model's values as C++ types — what kibo 2 generates — each found by argument-dependent lookup, so a model adds the overloads for its own types: `StaticType` (`type(tag<T>{})`, the runtime type a C++ type stands for, and `ValueOf<T>`, the `Value` class it becomes); `StaticWriter` and `StaticReader`, the static unfolding of `ValueWriter` and `ValueReader`; `StaticHash`, the hash of a C++ value over the vocabulary and every standard container.
- `ValueHashKey::of(value)`, a value-identity token that follows `Value::equal`, for a host whose collections key on a primitive: equal values give equal tokens.

**Fixed**

- An xarray compares its elements by position: `equal` and `compare` ignored how many elements each array held and where, so an array with an element removed equalled the array before the removal, or read past the end of the other.

### 1.2.27 — 2026-09-27

**Added**

- `DatabaseToCommitDatabaseConverter::commitId()` and `CommitDatabaseFlattener::commitId()` answer the commit the transfer made. Both refuse a second run, so the answer is never ambiguous.
- `DatabaseTransferErrors`, raised when a transfer is asked to run twice.

**Fixed**

- A blob pack writes the same bytes for the same descriptor: each region record carried the three padding bytes of its `BlobLayout`, which nothing wrote, so two equal packs could differ, and so could their `BlobId`.
- `Html.document` escapes its title: a title carrying markup closed `<title>` early and could put a script in the head. `body()` still passes its fragment through raw.
- Decoding a value refuses a blob holding bytes past it (`StreamErrors::BytesPastTheValue`, 3): what remained meant the value read was wrong too, another type or another codec.
- A locked file answers `SQLiteErrors::Busy` (31) wherever the wait runs out: `prepare` answered it with `Function` (30), so a reader opening a file held exclusively saw "prepare failed".
- A blob read or write tells a missing blob (`UnknownBlob`, 33) from an offset out of range; not-frozen and frozen carry their own codes, 30 and 32, not the 2 GB one.
- A merge decree applies only to its own merge: `reconcile` refuses a commit that is not a merge, and `reconcile` / `materializeMerge` refuse a resolution analysed against another (ours, theirs), the reversed pair included, before writing anything.
- A call on a closed `ServiceRemote` or `DatabaseRemote` is refused as closed (`ServiceErrors::IsClosed`, `DatabaseRemoteErrors::IsClosed`), as `CommitDatabaseRemote` already was. `DatabaseRemote` sent on the released descriptor and reported "Bad file descriptor".
- `DatabaseRemote::extendDefinitions` refreshes the definitions the client holds: an attachment it added was refused as unregistered until a reconnection.
- `ServiceRemote::peername` over a unix socket is the path connected to; it was the client's descriptor number.
- A value unwrapped from an optional has the optional as its `DocumentNode` parent; it named itself, so nothing walked up from it. An `any` displays `value is <type>.` (it showed a stray `%1`), a `variant` a space before its type.
- `SharedMemory::fd()` answers the descriptor the region is mapped from (-1 on Windows). A descriptor of 0 is now closed, and a failed `create` releases its descriptor and name. On Windows, `create` refuses a name already published, as on POSIX.
- `Semaphore::tryWait` answers false on a zero count, as documented; it threw on POSIX and answered true on Windows. On Windows, `create` refuses a name already published, an opened semaphore can post, and the count is no longer capped at one.
- A DSM source map cuts the text it names: a documented field's type span started at its docstring, a `key<>`, `vec<>` or `mat<>` occurrence at its element name, so a rewrite deleted a docstring or truncated a type.
- `Definitions::createMembership` records the membership in its own registry, not on the club object it is handed, which may belong to another.
- A file cannot take the path `InMemory`, the one a database in memory answers: `SQLite` refuses to create or open it (`SQLiteErrors::ReservedPath`), and `isCompatible` answers false. `inMemory()` answered true for such a file.
- `CommitDatabaseServer::step` answers false once the server stopped or was cancelled; it kept answering true, so a loop on it never ended.
- `Socket::acceptNonBlock` refuses a closed socket, as `waitReadable` does, instead of selecting on a released descriptor.
- Deleting a blob stream drops it. `blobStreamDelete`, and a close onto a blob already held, matched the wrong key: the stream stayed writable, and one a `CommitDatabase` abandoned stayed in the file.
- `DatabaseSQLite::blobStreamDelete` requires a transaction, like every other blob write.
- `freezeBlob` answers false for a blob already frozen, as documented; it answered true.
- `CommitDatabaseSQLite::createBlobs` joins a transaction the caller opened. It opened its own, failed, and its rollback discarded the caller's earlier writes.
- An encoder refusal says where the value sits, as `while encoding '.deep[1]'`. It said what was wrong and never which value, so a wide document named no culprit. The decoder side already carried its path.
- A runtime message names a mechanism, not a call. A blob past 2 GB named `readBlob(blobId, size, offset)` and a repeated transfer named `commitId` — spellings a Python caller does not have.
- A failed blob-stream write abandons the stream and keeps its error. The cleanup closed the stream, which refuses an incomplete one, so it threw: the original error was lost, the delete skipped, and the stream stayed usable.
- `BlobStream::append` refuses a chunk past the end (`BlobStreamErrors::ExceedingBytes`) instead of wrapping its `size_t` counter.
- `json_encode` refuses infinity and not-a-number (`TypeErrors::InvalidJsonNumber`) instead of writing `null`, which left the document complete and failed on whoever read it next. The stream codecs and XML carry them, unchanged.
- `bson_encode` refuses what BSON cannot hold: those same numbers, and an integer above its signed 64-bit range (`TypeErrors::InvalidBsonInteger`), which escaped as the writing library's own exception rather than a Viper error.
- `DatabaseSQLite::isCompatible` answers instead of throwing for a file that is not SQLite3. It opened whatever it was handed; `CommitDatabaseSQLite::isCompatible` already guarded with `SQLite::isSQLite3`.
- `CommitStore::extendDefinitions` leaves the store able to write. It kept the state built at `use()` on the old definitions, so every later dispatch failed silently through the notifier, writing no commit.
- `to_dsm()` names its second block `// Mapping for Core::User.profile`, where it said only `// Definition` with a trailing space.
- The default HTML stylesheet defines `details_indent`, the class its nesting renderer emits, so nested documents no longer render flat.
- `SQLiteTableBlobErrors` names `BlobStream` and `readBlob` instead of a `BlobIO` API that exists nowhere, and its component lost a trailing space; `DSMErrors` says `DSMTypeReference`.
- `Path::patch` refuses a path that addresses no key, naming the shape it is not. An entry with nothing after it answered "invalid index 2", and one whose index addressed the entry's value had its key replaced instead.
- `TypeVec::make` and `TypeMat::make` refuse a dimension of zero, which holds no data, as the empty enumeration, structure and variant already do. The DSM checker reports it against the model's own line.

### 1.2.26 — 2026-09-20

**Changed**

- An RPC message holds its payload twice at most while it crosses the wire, not three times.

**Removed (breaking)**

- `ValueBlob::make(std::size_t)` and `BlobView::make(BlobLayout const &, std::size_t)` — both made a blob of zeros whose hash and `BlobId` were computed on those zeros, before the caller overwrote them. Use a builder.

**Added**

- `BlobArrayBuilder` and `BlobPackBuilder` fill the bytes of a blob, then seal them, with `BlobBuilderErrors` for a builder asked to write after `build()`.

**Fixed**

- A document is written with the type its attachment declares, and a namespace cycle closed through an attachment or a key reference is now seen: the dependency graph missed both.
- An RPC peer can no longer make the reader reserve what it never sends, and `CommitDatabaseRemote::uploadSpeed` / `downloadSpeed` report the direction they measure.
- A database repository server confines `setDatabase` to its own folder, and `XArray::operator!=` compiles.

### 1.2.25 — 2026-08-27

**Changed**

- `FunctionLambda` is renamed `FunctionCallable` and takes its name at construction: every instance was named `"lambda"`, so a `FunctionPool`, which indexes by name, kept only the last one.

**Removed (breaking)**

- `RPCPacketReturnBlobId`, the answer of the id-less `createBlob` that 1.2.24 removed.
- `RPCSideClientCall::returnVectorOfUUId`, declared and never defined.

**Fixed**

- `TypeTuple` and `TypeVariant` answer the representation of the namespace asked for: they cached the first answer whatever the namespace, and filled that cache unsynchronised from server threads.

### 1.2.24 — 2026-08-04

**Changed**

- Every error domain string names its namespace: `DatabaseErrors::Domain` is `"DatabaseErrors"`, and so on.

**Removed (breaking)**

- Five surfaces nothing called, five guards nothing reached, the `UnsetDatabase` packet and `RPCPacketReturnOptionalInt64`.
- The id-less `createBlob` packet.

**Added**

- Servers stop when asked: `CommitDatabaseServer`, `ServiceServer` and the repository server run `step(timeoutInSec)` under a `Cancelation`, and `finishBefore(sec)` answers how many client threads it could not join.
- `RPCConnection::stepFor` tells a read that timed out from a closed connection, and `Socket::waitReadable` waits for a peer without blocking the accept loop.

**Fixed**

- `createZeroBlob` works over RPC: the server answered an `int64` where the client waited for a `bool`, so every remote call failed (`RPCProtocolErrors`, 10) and blobs could not be streamed to a remote database.
- A partial `send()` no longer truncates a message on POSIX, and the accept loop rebuilds the descriptor set `select()` modified.
- A client thread that throws, or cannot open its database, no longer aborts or hangs the server.
- A length header announcing an empty payload is refused.
- Windows builds without ATL: `UuidCreate` comes from `<rpc.h>`.
- A vec or mat field given a scalar default raises `notALiteralList`, not `notALiteralValue`; three XML decoder guards that were declared are now applied.
- `dsm_check` and `DSMHelper::assemble` refuse a path that does not exist, and the repository server exits non-zero when it cannot start.

### 1.2.23 — 2026-07-23

**Fixed**

- `CommitState::get` returns a value its cache does not share: a first read handed out the cached value itself, so mutating it changed what every later read of that key returned.

### 1.2.22 — 2026-07-22

**Added**

- `DSMSourceMap`: passed to `DSMBuilder::parse`, it records the source span of every declaration, field, case, namespace, type expression and resolved reference, so a `.dsm` can be edited in place.

**Fixed**

- A `CommitMergeResolution` copies its chosen value: changing that value after building the resolution changed the decree.
- The ambiguous-reference diagnostic spells "ambiguous".

### 1.2.21 — 2026-07-19

**Changed**

- A `ValueString` holds UTF-8: `ValueString::make` refuses anything else (`TypeErrors::InvalidUtf8`). A blob holds bytes.
- Documentation cannot contain `"""`, which the DSM cannot escape; it is refused at construction and at JSON or XML import (`TypeErrors::InvalidDocumentation`).

**Added**

- DSM syntax errors speak DSM: the offending token is quoted and what was expected is named (`unexpected \`strcut\`; expected a definition or \`}\``). Error recovery is unchanged.

**Fixed**

- The HTML renderer escapes what it prints: a name, string or docstring carrying `<`, `&` or a quote injected markup.
- The XML value codec round-trips any string: it cut at `U+0000`, turned CR into LF and dropped whitespace-only text. XML-forbidden controls are refused (`TypeErrors::InvalidXmlText`).
- Strings are escaped wherever they enter DSM, `repr` or a docstring: a quote or a backslash produced text that did not parse back.
- A name arriving through JSON or XML import is checked as an identifier (`InvalidName`).
- A DSM error at end of input names its file and a 1-based column.
- A variant's arms are de-duplicated by `runtimeId`, not by description.

### 1.2.20 — 2026-07-12

**Added**

- `CommitIdCollector` gathers every `CommitId` a value references, as `BlobIdCollector` does for blobs; `useCommitId(type)` says whether a type can hold one.

**Fixed**

- Extending the definitions of a database with a type redefined under a new `runtimeId` is refused before any write (`conflictInTypeNameGovernance`); it stored a second definition of the name, and the database no longer opened.
- The construction API refuses what the DSM cannot write: a DSM keyword as identifier, a forked or cyclic namespace, a non-literal default (`inf`, `nan`), a duplicate parameter name, a non-identifier field or case name.
- A default equal to the type's own default is stored as no default.

### 1.2.19 — 2026-07-06

**Added**

- An XML wire format for values and DSM definitions: `XmlValueEncoder`, `XmlValueDecoder`, `XmlDSMDefinitionsEncoder` and `XmlDSMDefinitionsDecoder`, beside JSON and BSON, on a vendored pugixml.

### 1.2.18 — 2026-07-03

**Fixed**

- The JSON value decoder reads an integer literal into a `float` or `double` field: `5` is `5.0`, JSON having one number type. The encoder still writes `5.0`.

### 1.2.17 — 2026-06-28 (phantom)
- *No runtime change. The runtime number was bumped in lockstep with the dsviper Python
  wheel 1.2.17 (a binding bug-fix release) — the last lockstep bump before `viper_version()`
  decoupled the wheel and runtime streams. Shipped unchanged by dsviper for Node.js 1.2.1
  and 1.2.2.*

### 1.2.16 — 2026-06-13

**Added**

- A merge can be analysed and reconciled before it is written: `CommitStateBuilder::mergeState` and `mergeEnabledByCommitId` compute what `mergeCommit(ours, theirs)` would give, without writing it.
- `CommitMergeAnalyzer::analyzeVirtualMerge`, `reconcileState` and `materializeMerge`: analyse that state, compose the chosen values in memory, then write the merge and its reconciliation together. `CommitMergeAnalysis::mergeCommit` becomes optional, empty for a virtual analysis.

**Fixed**

- A document holding a set or a map builds its `DocumentNode` tree: the node identity encoded paths through set elements and map entries, which the path writer refused.
- A path through a set element or a map entry is written and read back whole; the path codec handled regular paths only.

### 1.2.15 — 2026-06-11

**Changed**

- Head navigation and state construction leave `CommitDatabase`: `reduceHeads`, `forward` and `fastForward` move to `CommitDatabaseHelper`, `initialState`, `state` and `enabledByCommitId` to `CommitStateBuilder`, each taking the database.
- `CommitDatabaseHelper::reduceHeads(db, anchor)` merges the other heads into the head you name, refusing one that is not a head (`CommitErrors::notAHead`); without an anchor it starts from `lastCommitId`.

**Removed (breaking)**

- `CommitStore::Instance()`, the process-wide store. Build one with `CommitStore::make()` and own it.

**Fixed**

- `XArray::contains` and `positionOf` compile for keys and structures, which define `==` only; they called an `isEqual` those types lack.
- The runtime builds with MSVC again.

### 1.2.14 — 2026-06-10

**Changed**

- A `Fuzzer` is reproducible: one seeded generator drives every draw, the UUID family included, and `seed()` answers the seed, so a run can be replayed. A seed can be passed at construction.

### 1.2.13 — 2026-06-04

**Added**

- `StreamReading::remaining()` and `StreamRawReading::size()`: how many bytes are left to decode, and how many the source holds.

**Fixed**

- A malformed JSON or BSON document raises a `Viper::Error`, value or DSM definitions; the parser's own exception escaped the runtime.
- Hashing a shared value or id from two threads is safe: the hash was cached lazily under a `const` method. Ids now hash at construction, strings and blobs once.
- `CommitStore::Instance()` initialises safely under concurrent first use.
- `UUId::hash()` no longer reads a misaligned integer, undefined behaviour on some platforms; the hash is unchanged.

### 1.2.12 — 2026-05-31

**Changed**

- The Database ↔ CommitDatabase converters take open databases, local or remote, instead of file paths. The commit to read, or the label to write, is explicit; the result is a `DatabaseTransferInfo` (documents, blobs) instead of text on standard output.
- A transfer copies only the blobs the copied state references, streamed in 64 MiB chunks, so a blob past 2 GB is carried.
- `Databasing::createBlob(blobId, layout, blob)` takes the id and answers whether it created the blob, as `CommitDatabasing` does; it computed the id and returned it.

**Added**

- `DatabaseCopier` copies a `Database` into another one whole, orphan blobs included.
- `CommitDatabaseFlattener` collapses one commit of a `CommitDatabase` into a new `CommitDatabase` holding that state as its only commit, with the blobs it references.

### 1.2.11 — 2026-05-29

**Added**

- `CommitMergeAnalyzer` reconstructs what a merge dropped: `analyzeMerge` lists, per document, the paths where a branch's change did not survive, and `reconcile` writes the chosen values as one commit on top of the merge (`CommitMergeAnalysis`, `CommitMergeDocument`, `CommitMergeConflict`, `CommitMergeResolution`).

**Fixed**

- Every decoder checks a key against its field's type: the binary one accepted any concept. A key must name the field's concept or a descendant, or a descendant of a club member (`notAConceptDescendant`, `notAClubMemberDescendant`).
- The JSON decoder refuses a club key whose concept is not a member; the check was inverted and never raised.
- The JSON value decoder names the failing node by its path, checks the shape of an xarray, and refuses a negative number for an unsigned type.
- The binary Definitions decoder refuses a stored `runtimeId` that does not match its type; four of its five checks built the error without raising it.

### 1.2.10 — 2026-05-11

**Changed**

- `CommitId` hashes the parent, the type, the target and the opcodes only — no longer the timestamp or the label, so replaying the same opcodes from the same parent gives the same commit. Every `CommitId` computed before changes.

**Fixed (breaking)**

- `lastCommitId` breaks a timestamp tie by insertion order; SQLite answered either of two commits sharing a timestamp.

**Fixed**

- `reduceHeads` runs in an exclusive transaction: a head added between its read and its merges was left unreduced.

### 1.2.9 — 2026-05-08

**Changed**

- A JSON DSM definitions decoding error names the failing node by its path, where it gave the kind of node only.

**Fixed**

- The JSON DSM definitions decoder keeps `isMutable`: it set every attachment function mutable, so a pure one turned mutable after a JSON round trip.

### 1.2.7 — 2026-04-16

**Changed**

- NaN has a place in the total order: it equals itself, sorts before every other value, and every NaN hashes alike, so a set or a map key can hold one.
- A map diff emits `MapUpdate` for a modified key, where it folded it into `MapUnion`: the program reads Subtract, Update, Union, one opcode per kind of change.

**Added**

- `ValueDouble` and `ValueFloat` carry `INF`, `NEG_INF` and `NAN`, beside `ZERO` and `ONE`. `make()` answers these singletons for the special values.

**Fixed**

- `ValueFloat` accepts ±inf and NaN: the range check that guards the narrowing from double refused them as overflow.
- An empty set is disjoint from itself: the shortcut for a set compared with itself answered false whether it was empty or not.
- `ValueMap::pop(key, default)` answers the default on an empty map; it raised.
- `CommitDatabase::isAncestor` stays linear on a DAG with many merges: it walked shared ancestors once per path, exponential in the number of merges.
- `DatabaseSQLite::delBlob` outside a transaction is refused, as every other mutation is; it deleted.
- `Service::make` refuses two pools with the same name or UUID: the duplicate check searched maps it never filled, so any duplicate passed.
- `Definitions::createStructure` refuses a structure without fields (`TypeErrors::EmptyStructure`, 44), as the DSM checker does; one broke the `to_dsm` round trip.
- An enumeration or a variant may hold 256 cases, what a `uint8` index addresses; the checker stopped at 255.
- `BlobPackDescriptor::addRegion` refuses an empty name (`NameEmpty`, 2) and a count of zero (`CountZero`, 3).
- A blob pack whose region count is corrupt is refused before the size computed from it overflows.
- A string holding a NUL byte is written whole by the binary, raw and hashing streams, which cut it at the first NUL.
- `StreamWriterFile::write` reports a failed write (a full disk, a closed stream); the bytes were lost without a word.
- `ValueXArray::disablePosition` refuses a position it does not hold; it recorded a tombstone for it.
- A path into an xarray reads the position it names: `isApplicable` used the component's rank as an index, reading another element or past the end.
- `CommitStore::reset` on an empty database, or without a notifier, does nothing; it dereferenced what was not there.
- `SharedMemory` works on Windows: `create` and `open` swapped the handle and the address, so the first access crashed.
- An unset `HOME` no longer crashes the path helpers, which built a string from a null pointer.
- The runtime builds with GCC and links `librt` on manylinux, where `shm_open` lives; the wheel failed to import there.

### 1.2.5 — 2026-03-24

**Fixed**

- Extending the definitions of a `Database` keeps what it held: `DatabaseSQLite` stored the new definitions alone instead of the merged ones.
- A path through nested collections pivots on its last entry or element: `isEntryKeyPath`, `isElementPath`, `entryKeyInfo` and `elementInfo` took the first, and misread a set inside a map value.

### 1.2.0 — 2026-03-20
Initial release.

- Type/Value system with reference semantics; Database engine (SQLite backend);
  Commit engine with content-addressable storage (SHA-1); blob storage with
  attachment support; JSON and binary stream codecs; RPC and network services; a
  single structured exception type.
- Platforms: macOS 15, Windows 10/11, Linux Ubuntu 24.04 LTS (x86_64 / arm64).

## dsviper for Python

The PyPI wheel (`pip install dsviper`). Its `PATCH` stream is independent of the
runtime; each release notes the runtime version it ships.

### 1.2.29 — 2026-10-05

*Ships runtime 1.2.28.*

**Changed (breaking)**

- Enumeration values order by their definition, as the runtime now does: a `ValueSet` or a `ValueMap` keyed by an enumeration iterates and encodes in declaration order; it ordered by case name.

**Changed**

- A default key of a concept names that concept: `Value.create(TypeKey(c))` and an unset key field answer `type_concept()` c, with no instance id. A key of a club or of any concept names none.
- `ValueXArray.append` returns the position of the element it appended, which `at` reads and `remove` removes; it returned END.

**Added**

- A remote attachment function that only reads also takes an `AttachmentGetting`, a database's or a commit state's; one that mutates still requires an `AttachmentMutating`.
- `ValueMat(type_mat, *, identity=True)` builds the identity; with no initial value and no flag, a mat is all zeros.
- `Attachment` compares, orders and hashes by its `runtime_id()`, which its definition determines, so it can key a `dict`, join a `set` or be sorted.

**Fixed (breaking)**

- A bool is not an integer: `True` given for an integer, an enumeration's index included, is refused, as a float is and as the Node binding does.
- A dict is not a set, nor a Value of another type its elements: a set, a vector or an xarray refuses them instead of converting their keys or elements, as the Node binding does.

**Fixed**

- An xarray compares its elements by position: `==` and ordering ignored where each element sat, so an array with an element removed equalled the array before the removal.
- `xarray[position]` reads `None` for a position that holds no element — `END`, or a removed position — as `at()` does, instead of killing the interpreter.
- A structure is decoded from a mapping only: a `str`, a `list` or a `tuple` where a structure is expected raises `ViperError`, as a wrong scalar does, instead of an `AttributeError`.
- `Value.create(key_type, key)` takes a key already made, checked against the type, as the Node binding does; it took a uuid only. A key of a club or of any concept with no value is the invalid key; it raised.
- A mat built from columns that are not sequences raises `ViperError`, naming the column, instead of Python's `TypeError`.
- A value constructor given a value of its type builds a deep copy, as every other already did: a vector shared its elements. The constructors' documentation now says so.
- `TypeStructureField.default_value()` says it is None when the declared default is the type's zero (0, "", false, an enumeration's first case): such a default is not kept.
- The README no longer says only `dispatch_*` is undoable: the store's own `commit_mutations` is too; a commit made on the `CommitDatabase` directly is not.
- `ValueBlobId` says it names a blob and stores nothing: a document holding one is written only once the blob is stored, otherwise the write fails with Missing blob.
- `ValueXArray.positions()` says what it lists: every position created, a removed one included, and END last, so a fresh array gives `[END]`; `items()` pairs only those holding an element.
- `AttachmentMutating` no longer says every write creates a missing key: `set` and `diff` create the document; `update` and the in-set, in-map and in-xarray writes have no effect on a key holding none, and raise nothing.
- Every method of the stub has a return annotation, so `mypy --strict` callers no longer get `no-untyped-call` from `Database.commit`, a type's constructor or a pool function's call.
- Seven parameters the stub declares `| None` refused None (`documentation`, `parent`, `path`, `stream_codec_instancing`); they take it as absent.

### 1.2.28 — 2026-09-27

*Ships runtime 1.2.27.*

**Changed (breaking)**

- `BlobArray(blob_layout, blob)` replaces `BlobArray.from_blob`, and `BlobArrayBuilder(blob_layout, count)` replaces the removed allocating constructor.

**Changed**

- A transfer runs once. `convert()` and `flatten()` raise on a second call, so `commit_id()` is never ambiguous.
- `from dsviper import *` no longer re-exports the compiled submodule.
- Passing a non-Value where one is required raises `TypeError` rather than `RuntimeError`.

**Added**

- `ValueXArray.size()` and `BlobArray.data_count()`, answering what `len()` answers, as every other container and blob array already did.
- `TypeName(name_space, name)` builds one, and `representation()` / `representation_in()` render it qualified or short.
- `DefinitionsInspector.is_ambiguous(attachment)` says whether a short name still names one thing.
- `BlobGetting.read_blob(blob_id, size, offset)` reads a blob in pieces, including past 2 GB where `blob()` refuses.
- `FunctionPrototype.name()` answers the name of the function it describes.
- `DatabaseToCommitDatabaseConverter.commit_id()` and `CommitDatabaseFlattener.commit_id()` answer the commit the transfer made, or None before it ran.
- `BlobArrayBuilder.data_count()` answers the range an index walks: `count()` times `blob_layout.components()`.
- `Codec.query` and `Codec.check` name the three stream codecs, say what each keeps, and which transport each belongs to. Mixing `STREAM_RAW` and `STREAM_BINARY` cannot be reported: on a little-endian host they write the same bytes.
- The integer types state their range, and `help(dsviper)` answers with what the package is.
- The type stub carries the binding's prose, so an editor shows the same text as `help()`.
- The READMEs show undo and redo, a database on disk, the NumPy path, a commit pattern that no longer forks the history, `Database` and the converters, `parse()` to an `Attachment`, `ServiceRemote`, and a pinned namespace uuid.

**Fixed (breaking)**

- `ValueMat` is the sequence of columns it says it is. `len(m)` counts the columns, the indices `m[i]` accepts; `size()` still counts the elements. A negative index counts from the end, and `list(m)` gives the columns.

**Fixed**

- Four stub declarations were wrong: `add_field(type=...)` type-checked and raised, the keyword being `type_or_value`; `memberships()` returns `dict[ValueUUId, set[ValueUUId]]`; `CommitData.data()` returns a `ValueBlob`; `inject` is on `DefinitionsConst`.
- `Value.create` is declared to return the class the type names, not `Value`: a type checker refused `Value.create(TypeVector(Type.STRING)).append(...)`, which runs.
- The stub no longer declares what the binding lacks: `BlobPackRegion.copy` and `ServiceRemoteAttachmentFunctionPool.definitions` raised `AttributeError`; `TypeVector.cast` declared a `TypeOptional`.
- `Value` states the runtime's total order: across types by kind, then type; a vector, a set or a map by size first, so `[3, 1, 2]` sorts after `[4]`.
- A read that is a snapshot says so: `keys()`, `CommitStore.state()`, `attachment_getting()`. A `ValueBlob` copies its bytes and `encoded()` returns a copy; a `ValueSet` copies its elements, a `ValueMap` its keys.
- The container texts say what an index does: `at()` raises on a negative index where `v[-1]` counts from the end; a set element is addressed by position; a field is written as an attribute.
- The `CommitStore` texts say what `close()` releases, that an undo after `use_commit` opens a second head, that `timestamp` orders nothing, and that a merge drops one side unsignalled, `CommitMergeAnalyzer` reconstructing it.
- A dispatch says what it raises and what it notifies: it raises before running; a failure once running goes to the notifier and `dispatch` returns None. Nothing removes a key: set nil over an optional document.
- A name is an identifier and not a C++, Python or TypeScript keyword; `inject()` spells names in upper snake case; `KeyNamer` says which attachment carries a display name; a `DefinitionsInspector` goes stale after a later create.
- The DSM texts say what they count: `DSMParseError.line()` and `pos()` are 1-based, `pos()` in characters; a function pool is declared beside the namespace; `from_function_pool` takes the runtime pool.
- The database texts say what they answer: `path()` of a database in memory, that transactions do not nest, that `'Deferred'` is the default, and that an exclusively locked file waits 10 s, then raises.
- A transfer states its target and its failure: it writes into a freshly created database, a run that raises part-way keeps what it wrote, and an exception raised by the stepper is ignored.
- The blob texts say what runs: `BlobEncoderLayout.type()` and `element_type()` were swapped, `BlobLayout.data_type()` returns a code, and a failed stream append or close deletes the stream.
- The codecs and services say what they do: XML keeps every value, JSON writes a uint64 bare; `set` takes a regular path, `patch` the others; `ServiceRemote.connect` extends the definitions it is given.
- `ValueStructure.set` with an undeclared field raises the runtime's `ViperError`, as `at` does; it raised an `IndexError` of its own.
- An any or a variant compares with a native decoded to the type of the value it holds: `ValueAny(ValueInt32(5)) == 5` and a variant holding `"txt"` equal to `"txt"` answered False. None against an any is the empty any.
- None as an input is read by the type it is decoded to: empty in an optional or an any, void in a void slot, no default where the type cannot hold it.
- `ValueMap.get(key, None)` no longer raises, `pop` honours a None default, and None decoded into an any is empty, not `Any(void)`.
- `ValueTuple.at`, `ValueMat.at` and `ValueMat.set` raise IndexError on a negative index, as their texts and every other container read do; they raised OverflowError.
- `ValueVoid.encoded()` returns None, as `Value.dumps` does; it returned a `ValueVoid`, the one primitive whose `encoded()` disagreed with `dumps`.
- A call on a closed `ServiceRemote` raises `ViperError`; it raised a bare `Exception` naming the client's own, empty, address.
- The stub declares `ServiceRemote.pools` and `attachment_pools` as properties, which they are: a type checker refused `service.pools.Tools`, the route their own text teaches.
- A `Path` and a `PathConst` with the same components compare equal, both ways. They carry the same path; `==` answered False across the two.
- `SharedMemory.fd()` returns the file descriptor; it returned the region's size.
- `StepperDelegate.step(action, percent)` checks its arguments, as its signature says; the default accepted anything.
- `DocumentNode` states the fifteen kinds `type()` answers, what `string_value()`, `string_component()` and `string_value_tooltip()` show for each, and that a uuid or a blob id is primitive. `ValueKey.detail_type_representation()`, `BlobPack(descriptor)`, `Attachment.description()` and the passive `Socket` factories say what they do.
- `Semaphore.wait()` says that it holds the interpreter lock, so only another process can end it.
- The stub lets `collect_blob_ids` / `collect_commit_ids` take the Path, CommitState, CommitMutableState or ValueProgram they document; it declared only `Value`.
- `is_compact`, `is_sized` and `pack_sized` say what they are: compact is bool-or-number fields, sized is fixed and readable alone (not a key), a pack-sized vector hands out copies.
- `concept_members` says what it answers: the concept and its descendants, not its clubs; the source-map span docs say where each span starts and stops.
- A parameter the stub declares `X | None` takes None, as the signature says: every `documentation`, `stream_codec_instancing` and `hashing` argument, `create_key`, `representation`, `description`, `byte_count`, `ValueXArray.insert`. They raised `TypeError`.
- `Fuzzer.set_blob_id(None)` gives each blob its own id again, as documented; `None` was refused.
- An error raised by the caller's own object reaches the caller. A sequence whose `__getitem__` raised crashed the interpreter; one whose `__len__` raised, or a string that cannot be encoded (a lone surrogate), ended in `SystemError` or a misleading error.
- A `str`, `bytes` or `bytearray` is not a sequence of elements: a vector, set, tuple or xarray built from one is refused, as in Node; `"abc"` became `['a', 'b', 'c']`. A set from a non-iterable raises `ViperError` instead of `SystemError`.
- `NameSpace` refuses an invalid name or uuid with `ValueError`; it raised `RuntimeError`.
- An enumeration case is read one way everywhere: `case`, `.case` or `Enum.case`, the enumeration named; the constructor accepted `Enum.case.extra` and refused `.case`, `loads` took any name. A string that is not base64 names its path.
- A deduce that cannot read its object has a code of its own (27); it shared an unrelated one. The empty-case message is well formed.
- `ViperError` names the three layers a call crosses and what each raises; it said a wrong type raises `TypeError`, which a native that does not fit its type does not.
- The `CommitStore` operations say what they do to the undo stack; `dispatch_diff` says what `recursive` walks; `is_closed` and the `*_speed` measures say what they measure.
- `CommitData.blob_ids` answers the empty set for a commit without mutations; it raised.
- `need_transmit` and `sync` say they read `data_version()`, which a write through the synchronized connection does not move.
- A notifier that raises no longer fails the store call with `SystemError`. Its exception is dropped, as for a logger or a stepper: the store has already acted.
- `sync_data` no longer promises the blobs its commits reference; they travel through `blob_datas`.
- `blob()` and `create_zero_blob` say that a reserved blob raises until `freeze_blob` seals it; `blob()` promised None.
- `begin_transaction(None)` is accepted on `Databasing` and `CommitDatabasing`, as the stub declares; it raised `TypeError`.
- `help()` no longer shows a phantom first parameter on a static method. All 202 read `from_index(module, /, index)` or `cast(self, /, value)`; they now read `from_index(index)`.
- A negative index or size raises instead of wrapping. It was read modulo 264, so `position(-264)` answered the first position and `Path.from_index(-1)` built a path to index 18446744073709551615. `Float16.to_float` refuses bits past 16.
- `SQLite.get_pragma` declares its key a `str`, and `runtime_id` on an attachment and on an opcode key no longer calls it a type. Three function classes said nothing in the package hands one back; their pool does.
- `ValueXArray[i]` follows Python's own indexing: `IndexError` past the end, a negative index counting from the end, and `KeyError` for a position the array does not hold. It answered `None` to all three.
- `PathConst.encode` named the wrong codec. It documented `STREAM_TOKEN_BINARY` where it and `Path.decode` both use `STREAM_BINARY`, so the round trip it describes would not have worked as written.
- `StreamCodecInstancing.name()` said the name travels in the stream. It does not: a stream carries no record of which codec wrote it.
- `chunked()` said a chunked blob reads like any other. Past 2 GB it is written with `blob_stream_create` / `_append` / `_close` and read with `read_blob`; `blob()` refuses it.
- `DSMSourceSpan` offsets are characters, start 0-based and stop inclusive, as `DSMParseError.pos()` counts them; and `DSMAttachment.identifier` cited two calls that class does not have.
- Seventeen static methods were documented `$self` - `Error.parse`, `Path.from_unwrap`, `diff_keys` and the fourteen `cast` - and `front`, `back`, `pop_max` and `documents_details` named the wrong default.
- `get()` and `enumerate()` hand back a copy, which only the write side stated; `StepperDelegate.step` takes `percent` as a fraction from 0.0 to 1.0.
- `FunctionPool.funcs` is a property, which its class described as a call.
- `blob()` past 2 GB raises, which its `-> ValueBlob | None` signature did not say; the message now names `read_blob`.
- Three classes could segfault the interpreter from pure Python, and three methods were uncallable or refused an argument they document.
- 25 constructors named a keyword the binding does not accept, and five classes promised what they do not do.
- `get()` raises on a key of another concept, which `is_nil()` does not report; `create()`, `open()` and `set()` now state their preconditions.
- `nodes()` is keyed by `ValueCommitId`, not a uuid, and holds one entry more than there are commits: the root the layout starts from.
- `commit_ids()` answers a set, in no order to rely on; the undo label is `Undo [...]` and `commit_type()` is what answers `Disable`.
- `is_equal` compares content, so two registries built apart from the same model are equal, and `hexdigest()` answers the same question on a string.
- `Value.create` wraps and the constructor copies shallowly, `Definitions.const()` is a live view where a store's `definitions()` is a snapshot, and crossing a store copies.
- `runtime_id` is computed, not assigned, and from three different things depending on what carries it; it was documented as "the uuid assigned by the runtime" on 40 methods.
- An out-of-range integer names the type you asked for, and the docstrings no longer name classes the package does not have.
- The transaction rule is stated on `Databasing`, the class a caller meets, and the stub says what an `encoded` getter hands back.
- `NameSpace` says its uuid is the model's lasting identity, which is what lets a later run read what an earlier one wrote.
- `to_dsm()` says how its output is arranged — types sorted, then the mapping, per attachment.
- The package says what a `.dsm` looks like, and can render your own definitions back as DSM source.
- `reconcile_state` says where it applies: over a materialized merge, and only there.
- `Definitions.create_concept`, `create_club` and `create_attachment` say where the documentation they take ends up.
- Every class in the stub carries its summary, and two declarations that disagreed with the binding were corrected.
- The relations comment no longer overstates what is total.
- `PathConst.patch` says which two shapes address a key, an element of a set and a map entry's key, where it described an entry of a set and sent a reader into a raise.
- `TypeMat` refuses a dimension of zero, and a negative one, which it read as unsigned and built into a matrix of 18446744073709551615 columns. Both it and `TypeVec` take a dimension as wide as a count, and state their bound.

### 1.2.27 — 2026-09-20

**Changed**

- The blob readers no longer write. `BlobArray` and `BlobPackRegion` lost their writable paths: writing into a sealed value would change what its `BlobId` names.
- A `BlobPack` is no longer declared a `Mapping`, having none of `keys`, `items` or `values`; `pack['absent']` now raises what `check('absent')` raises.
- `AttachmentMutating` is an `AttachmentGetting`, which the binding always built and the stub did not declare.
- A remote database holds a blob twice at most while it crosses the wire, not three times, and a blob read from a store is copied once less.

**Removed (breaking)**

- `BlobArray(blob_layout, size)` — it allocated a blob of zeros whose hash and `BlobId` were computed on those zeros. Use `BlobArrayBuilder` to fill, `BlobArray(layout, blob)` to read.
- `BlobArray.__setitem__`, `BlobPackRegion.__setitem__` and `BlobPackRegion.copy()` — they wrote into a blob shared with whoever held the value.

**Added**

- `py.typed` — mypy and Pyright now check your code against the binding's real surface.
- `BlobArrayBuilder(blob_layout, count)` fills the bytes of a blob, then seals them.
- `AttachmentMutating.attachment_getting()` reads back what a mutable state holds.
- `encoded=True` on the fourteen reads that projected to a native with no way back.
- `DSMType` and `DSMLiteral` are declared, with their subclasses.

**Fixed**

- Nothing writes into a `ValueBlob` any more, and a read-only buffer refuses a writable request.
- The class hierarchy the type hints declare is the one the binding builds, the protocols it answers are declared, and `copy` is typed by its receiver.
- The type hints say what a projecting read returns, accept what the binding accepts, and a read that can answer `None` says so where one that cannot does not.
- `AttachmentMutating.set` and `diff` refuse a document of another type, and a merge resolution keeps the type of its locus.
- A namespace cycle closed through an attachment or a key is rejected.
- A remote database no longer reserves the memory a peer announces but never sends, and `CommitDatabaseRemote.upload_speed` / `download_speed` report the direction they measure.
- `ValueMap.setdefault` returns the value, `ValueMat` says it is column-major, and `CommitSynchronizer.sync()` takes `None` for its logging.

### 1.2.26 — 2026-09-05

*Ships runtime 1.2.25.*

**Changed (breaking)**

- Seven constructor keywords are renamed, and a caller passing one by keyword breaks: `CommitDatabaseServer(database_path=)`, `ValueString`, `ValueUInt16` and `ValueBool` `(initial_value=)`, `TypeVec` and `TypeMat` `(numeric_type=)`, `DefinitionsMapper` `(source_…, target_…)`.

**Changed**

- The docstrings say what each class and method does, rewritten against the C++ they wrap; the stream writers state which Python types each accepts and converts.
- The docstrings state the decided behaviours: `ValueSet` and `ValueMap` iterate sorted, NaN equals itself and sorts below `-inf`, and `Value.dumps`' `json` flag changes two things.

**Fixed**

- Eight stub returns admit `None`: `DSMConcept.parent`, `DSMStructureField.default_value`, and `blob` / `blob_info` on `CommitDatabase`, `Database` and `BlobGetting`.
- `get()` is documented as returning a `ValueOptional`, always; the text said `None`, so a `get(...) is not None` test was always true.
- Four signatures render as signatures in `help()`, and three stream constructors no longer claim to take no argument.
- `Socket` and `StreamWriting` describe themselves, not `SharedMemory` and a reader; `DSMTypeMat` describes a matrix, and three classes state their instantiability correctly. Ships runtime 1.2.25.

### 1.2.25 — 2026-08-27

*Ships runtime 1.2.25.*

**Fixed**

- `Type.representation()` of a tuple or a variant no longer depends on call order, nor races between the client threads of a `CommitDatabaseServer`.
- `ValueXArray.rebuild_from` refuses a source of the wrong type with CPython's own `TypeError`. Ships runtime 1.2.25.

### 1.2.24 — 2026-08-04

*Ships runtime 1.2.24.*

**Added**

- `CommitDatabaseServer.finish_before(timeout_in_sec)` bounds the teardown and returns how many client threads it could not join; `step(timeout_in_sec)` is a bounded wait, so `SIGINT` is handled between steps.
- `Socket.close()` and `Socket.is_closed()`: a passive local socket is a file, which a host can now release.

**Fixed**

- `CommitDatabaseServer` refuses a logger that calls back into Python (`LoggerPrint`, one built with `Logging.create`) with a `TypeError`; its client threads run outside the GIL and would corrupt the interpreter.

**Packaging**

- A source file added to the runtime is picked up without re-running CMake. Ships runtime 1.2.24.

### 1.2.23 — 2026-07-23

*Ships runtime 1.2.23.*

**Fixed**

- `AttachmentGetting.get` on a `CommitState` returns a document its cache does not share: mutating a first read changed every later read of that key. Ships runtime 1.2.23.

### 1.2.22 — 2026-07-22

*Ships runtime 1.2.22.*

**Added**

- `DSMSourceMap`: `DSMBuilder.parse(source_map=DSMSourceMap())` records the source span of every declaration, field, case, namespace, type and resolved reference.

**Fixed**

- `CommitMergeResolution.chosen` returns a copy: it handed out the stored decree itself, which a caller could then change. Ships runtime 1.2.22.

### 1.2.21 — 2026-07-20

*Ships runtime 1.2.21.*

**Changed**

- A `ValueString` must be valid UTF-8, and documentation cannot contain `"""`; both were accepted before.

**Fixed**

- A string holding a NUL byte crosses the binding whole; it was cut at the first NUL.
- The HTML renderer escapes names, strings and documentation. Ships runtime 1.2.21.

### 1.2.20 — 2026-07-13

*Ships runtime 1.2.20.*

**Added**

- `Value.collect_commit_ids(value, type, definitions)` and `Type.use_commit_id(type)`, the commit-id twins of `collect_blob_ids` and `use_blob_id`.
- `ValueXArray.items(encoded=...)`, as on `ValueMap`: `encoded=False` yields the typed elements.
- `ValueXArray.rebuild_from(source, ...)` copies a source xarray's positions and tombstones and installs new elements in one step.

**Fixed**

- `extend_definitions` with a type redefined under a new `runtimeId` is refused before any write; it left a database that no longer opened.
- A `DSMDefinitions` built through the binding is refused where the DSM could not write it: keywords as names, forked or cyclic namespaces, non-literal defaults, duplicate parameters. Ships runtime 1.2.20.

### 1.2.19 — 2026-07-06

*Ships runtime 1.2.19.*

**Changed**

- The third-party notices list pugixml, now linked into the wheel. Ships runtime 1.2.19.

**Added**

- `Value.to_xml_string(value, indent=...)`, `Value.from_xml_string(string, type, definitions)`, `DSMDefinitions.to_xml_string(indent=...)` and `DSMDefinitions.from_xml_string(string)`.

### 1.2.18 — 2026-07-03

*Ships runtime 1.2.18.*

**Changed**

- The documentation link points at the `dsviper-python` landing page. Ships runtime 1.2.18.

**Fixed**

- `==` and `!=` between values never raise: they converted the other operand to the receiver's type and raised on a mismatch. Two values now compare in the runtime's total order; a native that does not fit compares unequal.
- `ValueAny` and `ValueVariant` compare symmetrically: an any equalled its raw content while the content did not equal the any. An any now equals an any only; unwrap it to compare the content.
- `Type.ANY_CONCEPT == Type.ANY_CONCEPT` is `True`: the comparison used the `TypeAny` singleton, so it also equalled `Type.ANY`.

### 1.2.17 — 2026-06-28

*Ships runtime 1.2.17.*

**Added**

- `viper_version()` answers the runtime the wheel embeds, apart from `version()`, the wheel's own; from here the wheel's patch number moves on its own.

**Fixed**

- `ValueBlobId.encoded()` returns a `str`, as `ValueCommitId` and `ValueUUId` do; it returned a `ValueBlobId`.
- `TypeMap.values_type()` is a vector of the elements; it answered the key set.
- `StreamReaderSharedMemory.size()`, `ValueOptional.hash()` and `ValueEnumeration.hash()` exist; the stub declared them and calling them raised `AttributeError`.
- The stub states `ValueOptional.unwrap` and `get` default to `encoded=True`, as they do, and that `CommitStore.dispatch` returns the callable's result.
- The stub no longer declares `CommitData.transcode` or `DSMParseError.part`, which exist nowhere.
- The README's example builds states through `CommitStateBuilder`, as 1.2.15 requires. Ships runtime 1.2.17.

### 1.2.16 — 2026-06-13

*Ships runtime 1.2.16.*

**Added**

- `CommitStateBuilder.merge_state`, `merge_enabled_by_commit_id`, and `CommitMergeAnalyzer.analyze_virtual_merge`, `reconcile_state`, `materialize_merge`: a merge analysed and reconciled before it is written.

**Fixed**

- `DefinitionsExtendInfo.memberships()` maps each club to its members; it mapped each club to itself.
- `DefinitionsInspector.check_attachment` reads its identifier: a wrong argument format made every call undefined.
- `blob` and `del_blob` refuse a `blob_id` that is not a `ValueBlobId` with a `TypeError`; they read any object as one and crashed.
- An error inside `DefinitionsConst.inject` or `discard`, a tuple's `repr` or `len`, or an xarray's iteration becomes a Python exception; it escaped into the interpreter.
- Returned tuples, dicts and map items no longer leak: some twenty sites kept a reference per element. Ships runtime 1.2.16.

### 1.2.15 — 2026-06-11

*Ships runtime 1.2.15.*

**Changed**

- `CommitDatabase.forward`, `fast_forward`, `reduce_heads`, `initial_state`, `state` and `enabled_by_commit_id` are gone: use `CommitDatabaseHelper` and `CommitStateBuilder`, which take the database first.
- `CommitDatabaseHelper.reduce_heads(commit_database, commit_id=None)` merges the other heads into the one you name.

**Removed (breaking)**

- `CommitStore.instance()`: build a `CommitStore()` and keep it. Ships runtime 1.2.15.

### 1.2.14 — 2026-06-10

*Ships runtime 1.2.14.*

**Added**

- `Fuzzer(definitions, seed=...)` and `Fuzzer.seed()`: a run replays from its seed. Ships runtime 1.2.14.

### 1.2.13 — 2026-06-04

*Ships runtime 1.2.13.*

**Added**

- `remaining()` on the stream readers and `size()` on the raw readers.

**Fixed**

- A stream read over a temporary `ValueBlob` reads valid memory: the reader did not keep the blob alive, and read freed bytes. Ships runtime 1.2.13.

### 1.2.12 — 2026-05-31

*Ships runtime 1.2.12.*

**Changed (breaking)**

- `Databasing.create_blob(blob_id, blob_layout, blob)` takes the id and returns a `bool`, whether it created the blob, as `CommitDatabasing` does; it returned the computed id. Ships runtime 1.2.12.

**Added**

- `DatabaseToCommitDatabaseConverter`, `CommitDatabaseToDatabaseConverter`, `DatabaseCopier` and `CommitDatabaseFlattener` move documents and blobs between the two stores, each answering a `DatabaseTransferInfo`.
- `StepperDelegate`, subclassed in Python, receives the progress of a transfer.

### 1.2.11 — 2026-05-29

*Ships runtime 1.2.11.*

**Added**

- `CommitMergeAnalyzer`, `CommitMergeAnalysis`, `CommitMergeDocument`, `CommitMergeConflict` and `CommitMergeResolution`: what a merge dropped, per document and per path, and the commit that writes the chosen values back.

**Fixed**

- A key built from Python natives is checked against its field's type, as the runtime's decoders now do: its concept must be the field's or a descendant. Ships runtime 1.2.11.

### 1.2.10 — 2026-05-11
- *Ships runtime 1.2.10* (content-addressed `CommitId` narrowed — **breaking**;
  `reduceHeads` atomicity; `lastCommitId` tie-break).

### 1.2.9 — 2026-05-08

*Ships runtime 1.2.9.*

**Changed**

- An editable install rebuilds incrementally on import (`editable.rebuild`, a persistent build directory). Ships runtime 1.2.9.

### 1.2.8 — 2026-05-03

**Changed**

- Packaging — PEP 639 license metadata: `LICENSE` + `THIRD-PARTY-NOTICES.txt` embedded under `dist-info/licenses/`; `License-Expression: LicenseRef-DigitalSubstrate-Commercial-1.2` (the deprecated proprietary classifier removed).
- Ecosystem — runtime/DevKit split: the viper repo scopes to the runtime (`src/Viper`, `src/P_Viper`, `dsviper_wheel`); DevKit content extracted to standalone repos. README rewritten around the runtime-only scope; `requirements.txt` dropped.

### 1.2.7 — 2026-04-16

*Ships runtime 1.2.7.*

**Changed**

- The wheel builds with scikit-build-core (PEP 517), configured in `pyproject.toml`; `setup.py` and `build.py` are gone.

**Added**

- Wheels for Linux, macOS and Windows are built, tested and published by CI — five Python versions per platform, a release candidate to TestPyPI first; publication was manual.
- `ValueDouble.INF`, `NEG_INF`, `NAN`, and the same on `ValueFloat`.

**Fixed**

- `ValueString(None)` is the empty string, as `ValueBool`, `ValueInt*` and `ValueDouble` already default on `None`.
- `ValueFloat` accepts a Python float that is ±inf or NaN.
- A set the binding returns no longer leaks: every `wrapSetOf*` kept one reference per element.
- A buffer is released when decoding it fails; `decodeBlobBuffer` released it on success only.
- A C++ exception of any type becomes a Python error: one not derived from `std::exception` crossed the C API boundary, which is undefined.
- Ten return types in the stub were wrong: `Definitions.extend`, `extend_concepts`, `ValueVoid.encoded`, `CommitDatabase.reduce_heads` and `SharedMemory.unlink` said `None`, as did the in-place set and map operators.
- PyPI lists all three supported operating systems; each wheel advertised its own build machine's.
- Wheels build on manylinux, which ships no `libpython`: CMake asked for `Development` instead of `Development.Module`.

### 1.2.5 — 2026-03-24

*Ships runtime 1.2.5.*

**Fixed**

- `CommitStore.dispatch` reports a failing Python callback through `notify_dispatch_error` instead of raising, as the C++ store does; `notify_error` is renamed to match.
- `DefinitionsConst.inject` and `discard` take an optional namespace, a dict or a module, so an embedded editor evaluating in its own globals sees the constants; they wrote into `__main__`.
- Every wheel carries its long description and full metadata. Ships runtime 1.2.5.

### 1.2.0 — 2026-03-20
Initial release.

- Strong-typed Python C-API binding with seamless conversion; native Python
  collections accepted as input (metadata-driven). Published on PyPI
  (`pip install dsviper`).
- *Ships runtime 1.2.0.*

## dsviper for Node.js

The npm package `@digitalsubstrate/dsviper`. See {doc}`dsviper-node/index`.

### 1.2.14 — 2026-10-04

*Ships runtime 1.2.28.*

**Changed (breaking)**

- Enumeration values order by their definition, as the runtime now does: a `ValueSet` or a `ValueMap` keyed by an enumeration iterates and encodes in declaration order; it ordered by case name.

**Changed**

- A default key of a concept names that concept: `Value.create(new TypeKey(c))` and an unset key field answer `typeConcept()` c, with no instance id. A key of a club or of any concept names none.
- `ValueXArray.append` returns the position of the element it appended, which `at` reads and `remove` removes; it returned END.

**Added**

- A remote attachment function that only reads also takes an `AttachmentGetting`, a database's or a commit state's; one that mutates still requires an `AttachmentMutating`.
- `new ValueMat(type, null, true)` builds the identity; with no value and no flag, a mat is all zeros.
- `Attachment.equals()`, `compare()` and `hashKey()`, by its `runtimeId`, which its definition determines: a `Map` or a `Set` can hold an attachment by value, and attachments sort.

**Fixed (breaking)**

- A structure is built from a plain object only: a `Map`, a `Set`, a class instance or a Value of another type, taken as a structure of defaults, is refused, as in Python.
- A wrapped Value of another type is refused, as in Python: a structure, key or container Value given to `Value.create` or as an argument is checked against the type expected.
- An xarray argument is the list of its elements, as in Python: `set`, `update` and `Value.create` take `[e1, e2, …]`, and `[]` is the empty xarray. A caller passing the `dumps` form breaks; `Value.loads` still reads it.

**Fixed**

- An xarray compares its elements by position: `equals` and `compare` ignored where each element sat, so an array with an element removed equalled the array before the removal.
- `Attachment.createKey` refuses an instance id that is not a `ValueUUId`, as Python does: a uuid string, or any other value, minted a fresh instance, so a document filed under a saved id read back as absent.
- `ValueVariant.wrap(value)` without a type stores the alternative the value fits, as `Value.create` and Python do: `wrap(3)` on a `string|uint8` is a uint8, where it was refused as a double.
- A value constructor given a value of its type builds a deep copy, as every other already did: a vector shared its elements, a map its values. The constructors' documentation now says so.
- `hashKey()` follows `equals()`. Equal values got different keys (a key and its parent view, two nil optionals) and distinct values the same key (`Int8(1)` and `Int64(1)` inside an `any`). It is now the runtime's, a 64-bit bigint; `Value.hashKey(value)` returns it.
- `index.d.ts` compiles for a TypeScript consumer who lists no types: it references `@types/node`, which TypeScript 6 and later no longer load on their own. 1.2.13 declared the dependency only, and a consumer met 19 errors on `Buffer` and `Symbol.dispose`.
- The aggregate mutations take a native, as `index.d.ts` declares: `unionInSet`, `subtractInSet`, `unionInMap`, `subtractInMap`, `updateInMap`, `insertInXarray` and `updateInXarray` convert their value from the type the path names; they took a Value only.
- `TypeStructureField.defaultValue()` says it is undefined when the declared default is the type's zero (0, "", false, an enumeration's first case): such a default is not kept.
- The README no longer says only `dispatch*` is undoable: the store's own `commitMutations` is too; a commit made on the `CommitDatabase` directly is not.
- `ValueBlobId` says it names a blob and stores nothing: a document holding one is written only once the blob is stored, otherwise the write fails with Missing blob.
- `ValueXArray.positions()` says what it lists: every position created, a removed one included, and END last, so a fresh array gives `[END]`; `items()` pairs only those holding an element.
- `AttachmentMutating` no longer says every write creates a missing key: `set` and `diff` create the document; `update` and the in-set, in-map and in-xarray writes have no effect on a key holding none, and throw nothing.

### 1.2.13 — 2026-09-27

*Ships runtime 1.2.27.*

**Changed (breaking)**

- A stream array read answers a `ValueVec`, as in Python: `readUint8s(n)` and its nine siblings return a `vec<T, n>`; `toArray()` gives the native array.
- `BlobArray` reads binary. `at()` answers one datum as a native number (a bigint for the 64-bit types) and iteration walks the data; `blobView()` is the element reading, and `toTypedArray()` still hands out the whole run.
- `new BlobArray(blobLayout, blob)` replaces `BlobArray.fromBlob`.

**Changed**

- An array write takes a `ValueVec`, as declared, and refuses a sequence that does not hold `size` elements; it ignored `size`.
- A native that does not fit its type throws `ViperError`, stream writers included, naming the type expected, what was given and the path, as Python does. A signature argument still throws `TypeError`.
- Every optional parameter declares `| null`. The binding has always taken null as absent — each optional argument is read through a type guard — and the declarations now say so, which matters because JSON has no `undefined`.
- A transfer runs once. `convert()` and `flatten()` throw on a second call, so `commitId()` is never ambiguous.
- The third-party notices list what the package embeds, and nothing else.

**Added**

- `Semaphore`, the named semaphore the wheel already had: `create`, `open`, `exists`, `unlink`, `tryWait`, `wait` and `post`. `wait` blocks the event loop; `tryWait` polled between `setImmediate` turns waits without blocking it.
- `ViperError` is a class, exported: a runtime refusal is `instanceof ViperError` and carries `code`, `component` and `domain`. `name` stays `'ViperError'`; an index past the end stays a `RangeError`. It names the three layers a call crosses.
- A method taking ids takes a `ValueSet` as well as an array — `blobInfos`, `blobDatas`, `commitDatas`, `syncData`, `unknownBlobIds` — so what a query answers can be handed back.
- `new TypeName(nameSpace, name)` builds one, and `representation()` / `representationIn()` render it qualified or short.
- `DefinitionsInspector.isAmbiguous(attachment)` says whether a short name still names one thing.
- `BlobGetting.readBlob(blobId, size, offset)` reads a blob in pieces, including past 2 GB where `blob()` refuses.
- `FunctionPrototype.name()` answers the name of the function it describes.
- `DatabaseToCommitDatabaseConverter.commitId()` and `CommitDatabaseFlattener.commitId()` answer the commit the transfer made, or undefined before it ran.
- `BlobArrayBuilder.dataCount()` answers the length `copy()` requires: `count()` times `blobLayout.components()`.
- `Codec.query` and `Codec.check` name the three stream codecs, say what each keeps, and which transport each belongs to. Mixing `STREAM_RAW` and `STREAM_BINARY` cannot be reported: on a little-endian host they write the same bytes.
- The twelve constants the declarations promised now exist, and the README names the entry points a reader could not find.

**Fixed**

- `CommitData.data()` is declared to return a `ValueBlob`, which it always returned; the declaration said `CommitData`.
- A thrown `TypeError` names parameters a JS caller can type: `blob(blobId)`, not `blob(blob_id)`. The messages printed Python's snake_case, and two printed `seed=None`.
- `Value` states the runtime's total order: across types by kind, then type; a vector, a set or a map by size first, so `[3, 1, 2]` sorts after `[4]`.
- `keys()` and `CommitStore.state()` are snapshots: a later write or dispatch does not reach them. A blob copies its bytes in, and `encoded()` returns a copy.
- `ServiceRemote.connect` extends the definitions it is given, so an empty `new Definitions()` suffices; the port has no default. The README names the client half.
- `runtimeId` is computed, not assigned: `Definitions` says from what for each kind, and `NameSpace` that its uuid is the model's lasting identity, the invalid one being `GLOBAL`'s.
- A name is an identifier and not a C++, Python or TypeScript keyword; `inject()` spells names in upper snake case; `KeyNamer` says which attachment carries a display name.
- The `CommitStore` texts say what `close()` releases, that an undo after `useCommit` opens a second head, that `timestamp` orders nothing, and that a merge keeps the later side unsignalled, `CommitMergeAnalyzer` reconstructing it.
- `reconcileState` says where it applies: over a materialized merge. Committing it over a virtual merge state adds a third head; `materializeMerge` is the route.
- A transfer states its target and its failure: it writes into a freshly created database, a run that throws part-way keeps what it wrote, and a throwing progress callback is ignored.
- The database texts say what they answer: `path()` of a database in memory, that transactions do not nest, that `'Deferred'` is the default, and that a file locked by another process waits 10 s, then throws.
- The codecs say what each keeps: XML carries every value, `toJsonString` writes a uint64 bare and an enumeration as `.case`, and `decode` needs the type, the definitions and the codec from elsewhere.
- Both READMEs run as written: a `Database` sample, the path from `parse()` to an `Attachment`, a pinned namespace uuid, and `definitions.const().toDsmDefinitions()`, which threw without `const()`.
- `ValueStructure.set` and `setIn` with an undeclared field throw the runtime's `ViperError`, as `at` does; they threw a plain `Error` that `Error.parse` could not read. A field name that is not a string throws `TypeError`.
- `CommitStore.dispatch` is declared to return `T | undefined`: a callable that throws commits nothing and answers undefined, its error going to the notifier. The class says what a dispatch throws and what it notifies.
- An any or a variant compares with a native decoded to the type of the value it holds: `equals(5)` on an any holding int32 5 answered false. null against an any is the empty any.
- A blob size or offset is checked: `readBlob`, `blobStreamCreate` and the other blob sizes, and `SharedMemory.create`/`open`, throw on NaN, a negative or a fraction. A negative or NaN offset read from offset 0; a NaN size opened an empty stream.
- A bigint beyond int64 decodes to the double it names; it became 0.
- A boolean flag of another type throws `TypeError`: `readonly` of `open`, `json` of `dumps`, `packSized`, `recursive` of `dispatchDiff`, `showType` of `documentsDetails` and `enabled` of `dispatchEnableCommit` coerced any value, so `open(path, 'yes')` opened read-only.
- Null as an input is read by the type it is decoded to: empty in an optional or an any, void in a void slot, no default where the type cannot hold it.
- `ValueMap.get`/`pop` honour a null default, and a void slot accepts null, as its class says.
- `ValueVoid.encoded()` returns null, as `Value.dumps` does; it returned `undefined`, the one primitive whose `encoded()` disagreed with `dumps`.
- A call on a closed `ServiceRemote` throws `ViperError`; it threw a plain `Error` naming the client's own, empty, address.
- `ServiceRemoteAttachmentFunction.call` declares the `AttachmentMutating` it takes first: a type-checked caller could not write the call its class text describes.
- `PathConst.equals` takes a `Path`, as `Path.equals` took a `PathConst`: the two with the same components are equal both ways. It answered false one way and true the other.
- `SharedMemory.fd()` returns the file descriptor; it returned the region's size.
- `DocumentNode` states the fifteen kinds `type()` answers, what `stringValue()`, `stringComponent()` and `stringValueTooltip()` show for each, and that a uuid or a blob id is primitive. `ValueKey.detailTypeRepresentation()`, `new BlobPack(descriptor)`, `Attachment.description()` and the passive `Socket` factories say what they do.
- `collectBlobIds` / `collectCommitIds` take a Path, CommitState, CommitMutableState or ValueProgram, as documented; they refused all but a Value.
- `TypeKey.compare` takes any Type, as declared; it refused a type that is not a key.
- `ValueVectorIter`, `ValueSetIter` and `ValueTupleIter` are exported, as declared.
- `isCompact`, `isSized` and `packSized` say what they are; a pack-sized vector hands out copies.
- `conceptMembers` says what it answers: the concept and its descendants, not its clubs; the source-map span docs say where each span starts and stops.
- The `CommitStore` operations say what they do to the undo stack; `dispatchDiff` says what `recursive` walks; `isClosed` and the `*Speed` measures say what they measure.
- `CommitData.blobIds` answers the empty set for a commit without mutations; it threw.
- `needTransmit` and `sync` say they read `dataVersion()`, which a write through the synchronized connection does not move.
- `CommitStoreNotifying.create` refuses an object missing a notify method with a `TypeError`, as the declaration says and Python does; it accepted any object.
- `SQLite.compileOptions()` answers `[name, value]` pairs, as its declaration states; it answered a plain object.
- `NameSpace` refuses an invalid name or uuid with `TypeError`, as the other signature checks do; it threw a plain `Error`.
- An enumeration case is read one way everywhere: `case`, `.case` or `Enum.case`, the enumeration named. A string that is not base64 names its path.
- `syncData` no longer promises the blobs its commits reference; they travel through `blobDatas`.
- `blob()` and `createZeroBlob` say that a reserved blob throws until `freezeBlob` seals it; `blob()` promised undefined.
- An optional argument of another type throws instead of being dropped. `undefined` and `null` still mean the default; `createConcept(ns, name, parent)` no longer creates a parentless concept.
- `keys()` is declared a `ValueSet<ValueKey>`, and a structure's field map takes `undefined` as the runtime does, like `null`: a typed caller no longer casts either.
- A second copy of the package in one process is refused, naming both. Two copies of the native binary do not recognise each other's objects; loading both failed with an unrelated message.
- Five declarations refused code that runs: a `ValueSet` built from ids, `createBlobFromBuffer` given a typed array or `ArrayBuffer`, a `bigint` seed or pack size, and a progress callback.
- `ValueOpcodeKey` compares by value and `BlobPackRegion` reads a datum, as Python's `==`, `hash()` and `region[i]` do: `equals`, `compare`, `hashKey()` and `at(index)`.
- `ValueMat` iterates its columns, each a native array of its rows, as Python's does. Spreading one threw.
- `ValueXArray.size()` and `BlobArray.dataCount()` count what `len()` counts in Python. Neither array could be counted: `positions()` includes END, and `BlobArray` had to be iterated.
- An index, a size or a count is an integer, or the call throws. NaN was read as 0 and 1.5 as 1, so `set(NaN, v)` overwrote element 0. `position()` and `Path.fromIndex()` refuse a negative index.
- `SQLite.getPragma` takes a string, as the runtime always did: it was declared taking a `ValueKey`, which refused the one call that works. `runtimeId()` on an attachment and on an opcode key no longer calls it a type.
- `TypeName` and `NameSpace` have a `hashKey()` that follows `equals`. Keyed by their text, a native Map or Set merged two namespaces sharing a name and split a renamed one.
- A set of ids comes back as a `ValueSet`, not an array — `blobIds()`, `commitIds()`, `headCommitIds()` and 33 others. An array had no membership by value: `includes()` compares identity, and `some()` scanned. A spread gives the array back.
- Iterating a `ValueSet` is linear. It walked the set from the start at every step.
- A stray property on a value is refused instead of shadowing the field: `s.name = 'Alice'` answered on read while the field stayed empty. Every wrapper is sealed; strict code throws `TypeError`, a sloppy script drops the write.
- `PathConst.encode` named the wrong codec. It documented `STREAM_TOKEN_BINARY` where it and `Path.decode` both use `STREAM_BINARY`, so the round trip it describes would not have worked as written.
- `StreamCodecInstancing.name()` said the name travels in the stream. It does not: a stream carries no record of which codec wrote it.
- `chunked()` said a chunked blob reads like any other. Past 2 GB it is written with `blobStreamCreate` / `Write` / `Close` and read with `readBlob`; `blob()` refuses it.
- `DSMSourceSpan` offsets are characters, start 0-based and stop inclusive, as `DSMSourcePosition` counts them; and `DSMAttachment.identifier` cited two calls that class does not have.
- `get()` and `enumerate()` hand back a copy, which only the write side stated, on all four classes that expose them.
- `ValueString` declared `hash()` twice, and `Cancelation` now says the flag latches and that `cancel()` is safe from a signal handler.
- A bad stream-codec argument segfaulted the process. It is now refused with a `TypeError`, and an absent one takes the default.
- `DatabaseTransferInfo.blobs()` was declared `bigint` and returns `number`, and `TypeVector.cast` declared the wrong class.
- 47 docstrings said "the set of" and returned an array, and four classes carried the same false promises as their Python twins.
- `index.d.ts` did not compile for a consumer without `@types/node`, and cited names Node does not have.
- `nodes()` is keyed by `ValueCommitId`, not a uuid, and holds one entry more than there are commits: the root the layout starts from.
- `get()` throws on a key of another concept, which `isNil()` does not report; `create()`, `open()` and `set()` now state their preconditions.
- `isEqual` compares content, so two registries built apart from the same model are equal, and `hexdigest()` answers the same question on a string.
- `Value.create` wraps and the constructor copies shallowly, `Definitions.const()` is a live view where a store's `definitions()` is a snapshot, and crossing a store copies.
- An out-of-range integer names the type you asked for, and the undo label is `Undo [...]` where `commitType()` is what answers `Disable`.
- The transaction rule is stated on `Databasing`, the class a caller meets, and the README samples type-check under `tsc` and still run.
- `toDsm()` says how its output is arranged — types sorted, then the mapping, per attachment — and the package says what a `.dsm` looks like.
- `ServiceRemoteFunctionPoolFunctions` documented a path this binding does not have, and `ServiceRemoteAttachmentFunctionPool.definitions` is gone from the declarations.
- `Definitions.createConcept`, `createClub` and `createAttachment` say where the documentation they take ends up.
- `PathConst.patch` says which two shapes address a key, an element of a set and a map entry's key, where it described an entry of a set and sent a reader into a throw.
- `TypeMat` refuses a dimension of zero, and a negative one, which it read as unsigned and built into a matrix of 18446744073709551615 columns. `TypeVec` and `TypeMat` now state their bound.

### 1.2.12 — 2026-09-20

**Changed**

- The blob readers no longer write. `BlobPackRegion` lost `copy()`: writing into a sealed value would change what its `BlobId` names.
- `AttachmentMutating` is an `AttachmentGetting`, which the binding always built and the declarations did not say.
- A remote database holds a blob twice at most while it crosses the wire, not three times, and a blob read from a store is copied once less.

**Removed (breaking)**

- `new BlobArray(blobLayout, size)` — it handed out a blob of zeros to be written into, and on this side nothing could reach those bytes. Use `BlobArrayBuilder`.
- `BlobPackRegion.copy(buffer)` — it wrote into a blob shared with whoever held the value.

**Added**

- A set-typed input takes a JS `Set`, alongside the array it already took.
- `new BlobArrayBuilder(blobLayout, count)` fills the bytes of a blob, then seals them.
- `AttachmentMutating.attachmentGetting()` reads back what a mutable state holds.
- `encoded` on the reads that projected to a native with no way back.

**Fixed**

- Nothing writes into a `ValueBlob` any more, and a host class can no longer derive from a bound one.
- `index.d.ts` says what Node answers: a subclass inherits its base's statics, a read that can answer `undefined` says so, `value.compare(other)` declares the native it takes, and `new ValueBlob(value)` declares what it takes.
- A 64-bit integer never takes a rounded value in silence, and a Value passed where a type is in scope is checked against it.
- `AttachmentMutating.set` and `diff` refuse a document of another type, and a merge resolution keeps the type of its locus.
- A namespace cycle closed through an attachment or a key is rejected.
- A remote database no longer reserves the memory a peer announces but never sends, and `CommitDatabaseRemote.uploadSpeed` / `downloadSpeed` report the direction they measure.
- `new ValueSet` and `new ValueMap` take what `Value.create` takes, and `CommitSynchronizer.sync(logging)` passes the logging on.

### 1.2.11 — 2026-09-05

*Ships runtime 1.2.25.*

**Changed**

- Node 24 is the floor (`engines: ">=24"`, was `>=18`); `[Symbol.dispose]` is installed on the thirteen resource handles unconditionally.
- The JSDoc describes JavaScript: it had been copied from the Python docstrings, `True`, `None`, snake_case names and "seamless with a Python int" included.
- The JSDoc states the decided behaviours: `ValueSet` and `ValueMap` iterate sorted, NaN equals itself and sorts below `-Infinity`, and `Value.dumps`' `json` flag changes two things.

**Fixed**

- `index.d.ts` declares ten members the binding has: the surface of `DatabaseTransferInfo`, and `equals` / `compare` on `NameSpace`, `TypeName`, `BlobLayout`, `Path` and `PathConst`.
- 69 JSDoc said `null` where the method answers `undefined`. Ships runtime 1.2.25.

### 1.2.10 — 2026-08-27

*Ships runtime 1.2.25.*

**Fixed**

- `type.representation()` of a tuple or a variant no longer depends on call order, nor races between the client threads of a `CommitDatabaseServer`. Ships runtime 1.2.25.

### 1.2.9 — 2026-08-04

*Ships runtime 1.2.24.*

**Added**

- `CommitDatabaseServer`, `Socket` and `Cancelation`: a Node host can serve a commit database. `step(timeoutInSec)` is a bounded wait, and `finishBefore(sec)` answers how many client threads are still running.
- `Socket.close()`, `Socket.isClosed()` and `[Symbol.dispose]`: a passive local socket is a file, which a host can now release. Ships runtime 1.2.24.

### 1.2.8 — 2026-07-23

*Ships runtime 1.2.23.*

**Fixed**

- `AttachmentGetting.get` on a `CommitState` returns a document its cache does not share: mutating a first read changed every later read of that key. Ships runtime 1.2.23.

### 1.2.7 — 2026-07-22

*Ships runtime 1.2.22.*

**Changed (breaking)**

- `ValueMap.items()` returns an array of `[key, value]` pairs of handles, and `keys()` / `values()` the wrapped elements; `items` returned a `ValueVector` of tuples, so `items(false)` gave natives.

**Added**

- `DSMSourceMap`: `DSMBuilder.parse(sourceMap)` records the source span of every declaration, field, case, namespace, type and resolved reference.

**Fixed**

- A set element, a map key and `CommitMergeResolution.chosen` are handed out as copies: a caller could change them inside their container. Ships runtime 1.2.22.

### 1.2.6 — 2026-07-19

*Ships runtime 1.2.21.*

**Changed**

- A `ValueString` must be valid UTF-8, and documentation cannot contain `"""`; both were accepted before.

**Added**

- `ValueVector.concat` and `ValueMap.merge` return a new container and leave their operands untouched; `extend` and `update` still work in place.
- `index.d.ts` declares `ValueSet.contains` and `ValueXArray.contains`, which the binding had.

**Fixed**

- The HTML renderer escapes names, strings and documentation. Ships runtime 1.2.21.

### 1.2.5 — 2026-07-13

*Ships runtime 1.2.20.*

**Added**

- `Value.collectCommitIds(value, type, definitions)` and `Type.useCommitId(type)`, the commit-id twins of `collectBlobIds` and `useBlobId`.
- `ValueXArray.items(encoded?)`, as in Python: `items(false)` yields the typed elements.
- `ValueXArray.rebuildFrom(source, ...)` copies a source xarray's positions and tombstones and installs new elements in one step.

**Fixed**

- A `ValueVariant` handle placed in a structure field keeps its value; it was re-read as an arm and reset (`x: 9` became `0`).
- `extendDefinitions` with a type redefined under a new `runtimeId` is refused before any write; it left a database that no longer opened. Ships runtime 1.2.20.

### 1.2.4 — 2026-07-06

*Ships runtime 1.2.19.*

**Added**

- `Value.toXmlString(value, indent?)`, `Value.fromXmlString(string, type, definitions)`, `DSMDefinitions.toXmlString(indent?)` and `DSMDefinitions.fromXmlString(string)`. Ships runtime 1.2.19.

### 1.2.3 — 2026-07-02

*Ships runtime 1.2.18.*

**Removed (breaking)**

- `jsonEncode`, `jsonDecode`, `bsonEncode` and `bsonDecode`, renamed `toJsonString`, `fromJsonString`, `toBsonBlob` and `fromBsonBlob`, on `Value` and `DSMDefinitions`.
- `ValueVec.toTuple()` and `ValueMat.toTuple()`: use `toArray()`.
- `ValueOpcode.encode`, `decode`, `read` and `write`.
- `Logging.create(object)`, which only ever threw. Ships runtime 1.2.18.

**Added**

- `.at(-1)` and `.set(-1, …)` on the indexed sequences: `ValueVector`, `ValueVec`, `ValueTuple`, `ValueSet`, `BlobView`, `BlobArray`, and `ValueMat` per axis. Out of range still throws `RangeError`.
- `ValueVec` is iterable, and `ValueVec` / `ValueMat` have `toArray()`.
- A blob converts to and from a TypedArray: `BlobView.toTypedArray()`, `BlobArray.toTypedArray()`, `BlobArray.fromTypedArray(layout, ta)`, and `BlobLayout.glAttribParams()` for `gl.vertexAttribPointer`.
- `toJSON()` on every value: a 64-bit integer becomes a number when it fits exactly, else throws `RangeError`; a blob becomes base64.
- `Value.toBsonBlob` / `fromBsonBlob`, `DefinitionsConst.toDsmDefinitions`, `DefinitionsConst.write`, `Definitions.read`, `Definitions.extendConcepts`, `Path.read` and `PathConst.write` work; they threw "not yet usable".
- `getIn` / `setIn` descend through an optional, an any or a variant.
- `Symbol.toStringTag` on every class, and `Path` is iterable.

**Fixed**

- An argument error crosses as a real `TypeError` or `RangeError`, not a generic `Error` prefixed `"exception "`.
- `index.d.ts` declares the constructors as they are: `CommitDatabase` has none public; `TypeAny`, `TypeAnyConcept`, `BlobPackDescriptor` and `StreamWriterBlob` have one. `ServiceRemoteFunction.call` returns its result.
- `Value.fromJsonString` reads an integer literal into a `float` or `double` field.

### 1.2.2 — 2026-06-30

*Ships runtime 1.2.17.*

**Added**

- `value.hashKey()`, a `bigint` folding the type into the value's hash, to key a JS `Map` or `Set` by value; `hash()` alone hashes `Int8(1)` and `Int64(1)` alike.
- `[Symbol.dispose]` on the resource handles, so `using` releases a database, a store or a stream at scope exit.
- `Value.deduce` descends into nested natives: an array, a `Set`, a `Map` or an object becomes the matching container.

**Fixed**

- `.compare()` and `.equals()` accept any value and never throw: two values compare in the runtime's total order. An any or a variant compares the operand as its own type. Ships runtime 1.2.17.

### 1.2.1 — 2026-06-29

*Ships runtime 1.2.17.*

**Added**

- `ServiceRemote.functionPoolFunc(pool, name)` and `attachmentFunctionPoolFunc(pool, name)` reach one remote function by name.
- A prebuilt binary for macOS Intel.

**Fixed**

- `Definitions.decode` and `DefinitionsConst.encode` take a `streamCodecInstancing` and default to `StreamTokenBinaryCodec`, as Python does; a definitions blob encoded by default did not decode. Ships runtime 1.2.17.

### 1.2.0 — 2026-06-27
First release — the in-process Node.js binding over the Viper runtime, bound
roughly 1:1 with the Python surface via N-API.

- **Added** — the Type/Value system, Commit Database, Definitions & DSM,
  Key/Path/Attachment, Blob, codecs, and the blocking remote-service client, with
  a structured exception bridge.
- **Added** — native JS idioms: `number` / `bigint` numerics, prototype
  inheritance (`instanceof`), `util.inspect` rendering, object-literal structs
  (`assign` / `toObject`), Immutable.js-style `getIn` / `setIn`, strict
  non-negative `.at()`.
- **Added** — two-axis versioning: `version()` reports the binding, `viperVersion()`
  the embedded runtime.
- **Added** — prebuilt binaries for Linux (x64/arm64), macOS (Apple Silicon), and
  Windows (x64/arm64); N-API ABI-stable, no toolchain required at install.
- **Note** — the remote-service *server* tier, transport, and IPC/threading
  primitives are intentionally not bound (incompatible with Node's event loop).
- *Ships runtime 1.2.*

