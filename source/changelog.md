# Release notes

User-facing release notes for the Viper runtime and the two `dsviper` bindings.

There is **one runtime contract** — Viper C++ on the `1.2` line (`MAJOR.MINOR`) —
delivered through **two installable packages**, each with its **own independent
`PATCH` stream**:

- **dsviper for Python** — the wheel on PyPI (`pip install dsviper`)
- **@digitalsubstrate/dsviper** — the Node.js binding on npm

See {doc}`ecosystem/naming` for how these names relate. The Viper C++ runtime is
**not installed on its own** — it ships inside both packages; each binding entry
notes the runtime version it carries. Only released versions are listed, and
**breaking** changes are flagged inline.

## Viper C++ runtime

The engine shipped inside both bindings; `viperVersion()` reports this version.
Binding- or packaging-only releases are omitted — except a *phantom* version (a runtime
number minted with no runtime change, from a lockstep bump), listed to explain the gap.

### 1.2.23 — 2026-07-23
- **Fixed** — commit-read cache isolation: `CommitState::get` memoizes each `(attachment, key)`
  lookup, but the cache-miss path returned the very `ValueOptional` it had just cached. A
  document value is mutable, so mutating a first (cache-miss) result — `wrap`/`clear`, or
  mutating the unwrapped container — poisoned the cache, and every later read of that key
  then returned the corrupted value. The miss path now copies too (matching the hit path), so
  the memoized snapshot stays immutable from the caller's side. Reachable from both bindings
  via `AttachmentGetting.get`. The type/value system and on-disk format are unchanged.

### 1.2.22 — 2026-07-22
- **Added** — DSM parser source map: passing a `DSMSourceMap` to `DSMBuilder::parse` records the
  exact source span of every declaration, field, case, namespace, type sub-expression and
  *resolved* type-reference. This is the primitive behind a span-precise `.dsm` codemod — patch a
  hand-authored schema source in place under a transformation (file split, comments and ordering
  preserved) instead of regenerating it. Opt-in: `parse` without a source map is unchanged.
- **Fixed** — a merge decree is frozen at arbitration: `CommitMergeResolution` now copies its
  `chosen` value instead of storing the caller's handle, so the resolution owns an immutable
  snapshot; mutating the passed value after building the resolution can no longer alter the
  decree. The reconciled state is unchanged (reconcile already copied at consumption). The
  ambiguous-reference type-resolution diagnostic is also spelled correctly. The type/value system
  and on-disk format are unchanged.

### 1.2.21 — 2026-07-19
- **Fixed** — HTML-output escaping (XSS / attribute injection): the HTML renderer emitted
  names, strings, docstrings, keys and type references verbatim, so content carrying
  `& < > " '` (reachable through unvalidated JSON/XML import) could inject markup or
  attributes. Every content leaf is now escaped at the sink.
- **Fixed** — byte-exact XML value codec: no longer truncates on `U+0000`, normalises
  CR/CRLF, or drops whitespace-only text; XML-forbidden C0 controls are rejected, a carriage
  return survives as `&#13;`, and whitespace-only text survives. Containers round-trip
  unchanged.
- **Fixed** — symmetric string escaping across DSM string literals, `repr`, and docstrings
  (a value carrying `"`, `'` or `\` no longer produces unparseable text); imported
  identifiers are validated against the identifier policy; DSM parse errors at end-of-input
  carry their source file and a 1-based column; variant arms are de-duplicated by
  `runtimeId`, not description.
- **Added** — DSM-vocabulary parse diagnostics: the offending token is quoted and the
  expected concept is named (`a value` / `a type` / `a definition`).
- **Changed** — a `ValueString` must now be valid UTF-8, and a documentation string must be
  DSM-expressible (no `"""`); both reject input previously accepted. The type/value system
  and on-disk format are unchanged.

### 1.2.20 — 2026-07-12
- **Added** — CommitId collection: `CommitIdCollector`, the commit-id twin of `BlobIdCollector`
  — `useCommitId(type)` prunes any subtree whose type cannot hold a `CommitId`, then a typed
  value walk gathers every `CommitId` a value references. A `CommitId` content-addresses a DAG
  commit, so a schema-change rebuild can discover intra-DAG references. Additive — no change to
  the type/value system or on-disk format.
- **Fixed** — a conflicting schema upgrade no longer corrupts a database: `extendDefinitions`
  against a store whose schema redefined an existing type under a **new** `runtimeId` (e.g. a
  regenerated `.dsm`) used to commit a second, same-named definition, leaving the base unopenable
  (`AlreadyDefinedName` on every `open()`). The type-name governance check now runs first and
  raises before any write, so the transaction rolls back and the base stays openable. Preventive
  only — a database already poisoned by an older runtime must still be restored from backup.
- **Fixed** — DSM governance: a `Definitions` built through the construction API can no longer
  escape DSM-expressibility. DSM grammar keywords, forked/cyclic namespaces, non-literal field
  defaults, and duplicate parameter names are now rejected at construction. Safe against existing
  DSM — any `.dsm` that parses already cleared these gates.

### 1.2.19 — 2026-07-06
- **Added** — XML wire format: a third dialect (after JSON and BSON) of the type-driven
  serializer, round-tripping both values and DSM definitions on the vendored pugixml parser.
  Purely additive — the existing JSON/BSON surface is unchanged.

### 1.2.18 — 2026-07-03
- **Fixed** — JSON codec: the value decoder accepts a bare integer literal for a
  `float`/`double` field (`5` is read as `5.0`; JSON has a single number type), instead of
  rejecting it. Encoder output is unchanged. Fixes interop with third-party JSON producers
  that drop the decimal point of a whole-number double.

### 1.2.17 — 2026-06-28 (phantom)
- *No runtime change. The runtime number was bumped in lockstep with the dsviper Python
  wheel 1.2.17 (a binding bug-fix release) — the last lockstep bump before `viper_version()`
  decoupled the wheel and runtime streams. Shipped unchanged by dsviper for Node.js 1.2.1
  and 1.2.2.*

### 1.2.16 — 2026-06-13
- **Added** — Commit engine: pre-merge (virtual) reconciliation on
  `CommitStateBuilder` (`mergeState`, `analyzeVirtualMerge`, `reconcileState`,
  `materializeMerge`, `mergeEnabledByCommitId`) — additive analysis over the
  public commit API.
- **Fixed** — Path serialization: non-regular paths (`Entry` / `Element` steps)
  round-trip losslessly.

### 1.2.15 — 2026-06-11
- **Changed (breaking)** — head navigation and commit-state construction move out
  of `CommitDatabase` into `CommitDatabaseHelper` (`reduceHeads` / `forward` /
  `fastForward`) and `CommitStateBuilder` (`initialState` / `state` /
  `enabledByCommitId`); callers now pass the database explicitly.
- **Added** — `reduceHeads` selectable merge anchor; a non-head anchor raises a
  structured "not a head" error.
- **Removed (breaking)** — the global `CommitStore` singleton; construct and own a
  store explicitly.
- **Fixed** — `XArray` `contains` / `positionOf` over key element types.

### 1.2.14 — 2026-06-10
- **Added** — `Fuzzer` is now deterministic and seedable: a seed reproduces the
  generated keys and blob ids.

### 1.2.13 — 2026-06-04
- **Fixed** — malformed JSON/BSON now yields a structured error (previously
  undefined behavior) on both the generic and DSM-typed decode paths; value and
  id hashing made thread-safe.
- **Added** — stream-read interface: `remaining()` / `size()`.

### 1.2.11 — 2026-05-29
- **Added** — post-merge supervised reconciliation (`CommitMergeAnalyzer`):
  `analyzeMerge` reconstructs, per document, the points where a branch's intent
  did not survive a target-wins merge; `reconcile` composes per-locus decisions
  into a single child of the merge. New `CommitMergeAnalysis` /
  `CommitMergeDocument` / `CommitMergeConflict` / `CommitMergeResolution`.
- **Fixed** — unified key-decode conformance (null / concept / club keys); JSON
  decoder path-tracking diagnostics; restored the `runtimeId` mismatch guard in
  the binary Definitions decoder.

### 1.2.10 — 2026-05-11
- **Changed (breaking)** — `CommitId` is now derived only from
  `(parentCommitId, type, targetCommitId, opcodesBlob)`; `timestamp` / `label`
  are no longer hashed, giving intrinsic idempotence. **All prior `CommitId`
  values change.**
- **Fixed** — `reduceHeads` wrapped in an exclusive transaction (atomic against a
  concurrent writer); deterministic `lastCommitId` tie-break.

### 1.2.9 — 2026-05-08
- **Fixed** — JSON `DSMDefinitions` decoder preserves `isMutable`; corrected
  decode error context.
- **Changed** — JSON decoder errors carry a runtime JSON path instead of a static
  label.

### 1.2.7 — 2026-04-16
- **Fixed** — defined behavior for ±Inf / NaN in floats and doubles (total order
  over NaN; `INF` / `NEG_INF` / `NAN` constants; codec round-trip), plus a broad
  pass of value-semantics, blob, stream I/O, definitions/DSM, SQLite, and
  path/`XArray` correctness fixes and cross-platform cleanups (Windows shared
  memory, environment lookups).

### 1.2.5 — 2026-03-24
- **Fixed** — SQLite extend-definitions argument; nested `Entry` / `Element` path
  decomposition.

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

### 1.2.23 — 2026-07-23
- **Fixed** — `AttachmentGetting.get` returns a document isolated from the commit state's
  cache: on a cache miss the runtime handed back the cached `ValueOptional` itself, so mutating
  a read result (`wrap` / `clear`, or mutating the unwrapped container) poisoned the state's
  cache and corrupted every later read of that key. The frozen-snapshot contract that
  read/query layers rely on is restored.
- *Ships runtime 1.2.23 (commit-read cache isolation — see the runtime section).*

### 1.2.22 — 2026-07-22
- **Added** — `DSMSourceMap` exposed to Python: a `DSMSourceMap()` passed to
  `DSMBuilder.parse(source_map=…)` collects, as a parse by-product, the source span of every
  declaration, field, case, namespace, type sub-expression and *resolved* type-reference (with
  `.pyi` typings for the whole surface) — enabling an in-place patch of a `.dsm` tree under a
  schema change instead of regenerating it.
- **Fixed** — `CommitMergeResolution.chosen` no longer leaks a mutable alias into the immutable
  stored decree; the accessor now returns a copy, matching every other `Value const` accessor in
  the binding.
- *Ships runtime 1.2.22 (DSM parser source map; merge-decree value-semantics fix — see the
  runtime section).*

### 1.2.21 — 2026-07-20
- **Fixed** — interior NUL preserved across the Python string frontier: `str` decode/encode
  used the null-terminated `PyUnicode_AsUTF8` / `PyUnicode_FromString`, so a `ValueString`
  carrying an interior `\0` was silently truncated at the first null; the frontier is now
  size-aware (`PyUnicode_AsUTF8AndSize` / `PyUnicode_FromStringAndSize`) and such a string
  round-trips faithfully. (The Node binding was already size-correct.)
- *Ships runtime 1.2.21 (HTML-output escaping fix; byte-exact XML codec; UTF-8 `ValueString`;
  DSM-expressible docstrings — see the runtime section).*

### 1.2.20 — 2026-07-13
- **Added** — `Value.collect_commit_ids(value, type, definitions)` and `Type.use_commit_id(type)`
  — gather every `CommitId` a value references (the commit-id twin of `collect_blob_ids`);
  `use_commit_id` is the pruning predicate over a type, so a schema-change rebuild can discover
  intra-DAG references.
- **Added** — `ValueXArray.items(encoded=…)` keyword now matches `ValueMap.items` (default
  `True`); `encoded=False` yields typed `Value` elements, so an xarray of scalar elements can be
  walked and rebuilt faithfully. New `ValueXArray.rebuild_from(source, …)` performs an atomic
  trans-definitions rewrite (positions + tombstones copied, re-mapped elements swapped in a
  single memento, no partial state exposed).
- **Fixed** — a conflicting schema upgrade no longer corrupts a database: `extend_definitions`
  against a schema that redefined an existing type under a new `runtimeId` used to commit a
  second, same-named definition and leave the base unopenable; it now fails cleanly before any
  write.
- **Changed** — construction-time DSM governance: a `DSMDefinitions` built through the binding
  can no longer escape DSM-expressibility — DSM keywords, forked/cyclic namespaces, non-literal
  field defaults, and duplicate parameter names are rejected at construction.
- *Ships runtime 1.2.20.*

### 1.2.19 — 2026-07-06
- **Added** — XML wire format: `Value.to_xml_string(value, indent=…)` /
  `Value.from_xml_string(string, type, definitions)` and `DSMDefinitions.to_xml_string(indent=…)` /
  `DSMDefinitions.from_xml_string(string)` — the XML dialect of the type-driven serializer,
  alongside the existing JSON/BSON codecs. Additive — no change to the existing surface.
- *Ships runtime 1.2.19.*

### 1.2.18 — 2026-07-03
- **Fixed** — the binding's `TypeAnyConcept` comparison (`==` / `!=`) delegated to the
  `TypeAny` singleton, so `Type.ANY_CONCEPT == Type.ANY_CONCEPT` was `False` and
  `Type.ANY_CONCEPT == Type.ANY` was `True`; the runtime was already correct.
- **Changed** — packaging: the documentation URL now points at the `dsviper-python` landing
  page (`docs.digitalsubstrate.io/dsviper-python/`), following the documentation chapter rename.
- *Ships runtime 1.2.18.*

### 1.2.17 — 2026-06-28
- **Added** — `viper_version()` reports the embedded Viper runtime version,
  distinct from `version()` (the wheel version); the wheel's `PATCH` stream now
  moves independently of the runtime over the shared `1.2` contract.
- **Fixed** — `ValueBlobId.encoded()` now returns a `str` (previously returned a
  `ValueBlobId`).
- **Fixed** — `TypeMap.values_type()` now returns the value type (a `vector`)
  instead of the key type (a `set`).
- **Fixed** — bound `size()` / `hash()` methods that the runtime exposes but the
  binding was missing.
- **Fixed** — type stubs: `ValueOptional.unwrap()` / `get()` were annotated
  `encoded=False` but the binding defaults to `encoded=True` (hint-only
  correction); corrected the `dispatch` return annotation; removed phantom
  declarations bound nowhere (`CommitData.transcode`, `DSMParseError.part`).
- **Fixed** — packaging: the documentation URL now points at the dsviper landing
  page; the PyPI Quick Start routes through `CommitStateBuilder.initial_state(db)`
  / `state(db, commit_id)`.
- *Ships runtime 1.2.17 (phantom — see the runtime section).*

### 1.2.16 — 2026-06-13
- **Fixed** — memory-safety hardening in the binding (reference-count leaks across
  the encode and commit paths); `blob` / `del_blob` now type-check the blob id;
  exception boundaries around `DefinitionsConst` inject/discard and tuple/`XArray`
  operations.
- *Ships runtime 1.2.16.*

### 1.2.15 — 2026-06-11
- **Changed** — binding call sites moved to the runtime's new free-function
  namespaces (`CommitDatabaseHelper` / `CommitStateBuilder`); no other change.
- *Ships runtime 1.2.15.*

### 1.2.14 — 2026-06-10
- **Added** — `Fuzzer` gains an optional `seed` keyword and `seed()` method
  (deterministic, replayable runs).
- *Ships runtime 1.2.14.*

### 1.2.13 — 2026-06-04
- **Fixed** — use-after-free on the streaming read channel: the source
  `ValueBlob` is retained for the stream's lifetime.
- **Added** — `remaining()` / `size()` on the streaming reader types.
- *Ships runtime 1.2.13.*

### 1.2.12 — 2026-05-31
- **Added** — Database ↔ CommitDatabase transfer toolkit:
  `DatabaseToCommitDatabaseConverter`, `CommitDatabaseToDatabaseConverter`,
  `DatabaseCopier`, `CommitDatabaseFlattener`; a shared `DatabaseTransferInfo`; a
  subclassable `StepperDelegate`; pre-opened handles, 64 MiB blob streaming, and
  orphan/superseded blob dropping.
- **Changed (breaking)** — `Databasing.create_blob` is now
  `(BlobId, BlobLayout, Blob) -> bool` (the caller supplies the id), matching
  `CommitDatabasing`.

### 1.2.11 — 2026-05-29
- *Ships runtime 1.2.11* (`CommitMergeAnalyzer` post-merge reconciliation;
  key-decode conformance; JSON decoder diagnostics).

### 1.2.10 — 2026-05-11
- *Ships runtime 1.2.10* (content-addressed `CommitId` narrowed — **breaking**;
  `reduceHeads` atomicity; `lastCommitId` tie-break).

### 1.2.9 — 2026-05-08
- *Ships runtime 1.2.9.*

### 1.2.8 — 2026-05-03
- **Changed** — packaging moved to PEP 639 license metadata
  (`License-Expression: LicenseRef-DigitalSubstrate-Commercial-1.2`; `LICENSE`
  and third-party notices embedded under `dist-info/licenses/`).

### 1.2.7 — 2026-04-16
- **Fixed** — error-path safety in the binding; corrected several type-stub
  (`__init__.pyi`) return types.
- **Added** — multi-platform CI test matrix (Linux / macOS / Windows × 5 Python
  versions) and automated PyPI publication; robustness hardening with 270 new
  unit tests.
- *Ships runtime 1.2.7.*

### 1.2.5 — 2026-03-24
- **Fixed** — `CommitStore` dispatch error handling aligned with the C++
  semantics; inject/discard may target any namespace; complete wheel metadata.
- **Added** — semantic-version release tooling.
- *Ships runtime 1.2.5.*

### 1.2.0 — 2026-03-20
Initial release.

- Strong-typed Python C-API binding with seamless conversion; native Python
  collections accepted as input (metadata-driven). Published on PyPI
  (`pip install dsviper`).
- *Ships runtime 1.2.0.*

## dsviper for Node.js

The npm package `@digitalsubstrate/dsviper`. See {doc}`dsviper-node/index`.

### 1.2.8 — 2026-07-23
- **Fixed** — `AttachmentGetting.get` returns a document isolated from the commit state's
  cache: on a cache miss the runtime handed back the cached `ValueOptional` itself, so mutating
  a read result (`wrap` / `clear`, or mutating the unwrapped container) poisoned the state's
  cache and corrupted every later read of that key. The frozen-snapshot contract that
  read/query layers rely on is restored.
- *Ships runtime 1.2.23 (commit-read cache isolation — see the runtime section).*

### 1.2.7 — 2026-07-22
- **Added** — `DSMSourceMap` exposed to Node: a `new DSMSourceMap()` passed to
  `DSMBuilder.parse(sourceMap)` collects, as a parse by-product, the source span of every
  declaration, field, case, namespace, type sub-expression and *resolved* type-reference —
  enabling an in-place patch of a hand-authored `.dsm` tree under a schema change (file split,
  comments and ordering preserved) instead of regenerating it.
- **Fixed** — `ValueMap.items` / `keys` / `values` now hand out typed handles: `items` returned
  a single `ValueVector` of tuples that native-decodes on a JS destructure, so `items(false)`
  yielded native scalars instead of `Value` handles (breaking every `Map<_, scalar>` data
  migration). `items` now returns a JS array of `[key, value]` pairs (key copied, value carried);
  `keys` / `values` return the wrapped element.
- **Fixed** — immutable values are copied, never const-cast, across the JS frontier: every
  accessor that hands out an immutable value (set elements, map keys, the merge decree
  `CommitMergeResolution.chosen`) now returns a copy, so a caller can no longer reach in and
  corrupt the container or decree in place.
- *Ships runtime 1.2.22 (DSM parser source map; merge-decree value-semantics fix — see the
  runtime section).*

### 1.2.6 — 2026-07-19
- **Added** — non-mutating container combinators: `ValueVector.concat` (`v1 + v2`, also
  accepts a native array) returns a new vector and `ValueMap.merge` (`m1 | m2`, the other
  map wins on a shared key) returns a new map, both leaving the operands untouched (the
  in-place `extend` / `update` remain). `ValueSet.contains` / `ValueXArray.contains` are now
  declared in the typings (the runtime already exposed them).
- *Ships runtime 1.2.21 (HTML-output escaping fix; byte-exact XML codec; UTF-8 `ValueString`;
  DSM-expressible docstrings — see the runtime section).*

### 1.2.5 — 2026-07-13
- **Added** — `Value.collectCommitIds(value, type, definitions)` and `Type.useCommitId(type)`
  — gather every `CommitId` a value references (the commit-id twin of `collectBlobIds`);
  `useCommitId` is the pruning predicate over a type, so a schema-change rebuild can discover
  intra-DAG references.
- **Added** — `ValueXArray.items(encoded?)` gains the `encoded` argument (default `true`,
  matching prior behaviour); `items(false)` yields typed `Value` elements, so an xarray of
  scalar elements can be walked and rebuilt faithfully. New `ValueXArray.rebuildFrom(source, …)`
  performs an atomic trans-definitions rewrite (positions + tombstones copied, re-mapped
  elements swapped in a single memento, no partial state exposed).
- **Fixed** — a conflicting schema upgrade no longer corrupts a database: `extendDefinitions`
  against a schema that redefined an existing type under a new `runtimeId` used to commit a
  second, same-named definition and leave the base unopenable; it now fails cleanly before any
  write.
- **Fixed** — `decodeVariant` short-circuits an already-wrapped `ValueVariant`: placing a typed
  `ValueVariant` handle into a struct field re-elaborated it as an arm and dropped the inner
  value (`x: 9` → `0`); it now recognises the wrapped handle first, mirroring `decodeEnumeration`.
- **Changed** — construction-time DSM governance: a `DSMDefinitions` built through the binding
  can no longer escape DSM-expressibility — DSM keywords, forked/cyclic namespaces, non-literal
  field defaults, and duplicate parameter names are rejected at construction.
- *Ships runtime 1.2.20.*

### 1.2.4 — 2026-07-06
- **Added** — XML wire format: `Value.toXmlString(value, indent?)` /
  `Value.fromXmlString(string, type, definitions)` and `DSMDefinitions.toXmlString(indent?)` /
  `DSMDefinitions.fromXmlString(string)` — the XML dialect of the type-driven serializer,
  alongside the existing JSON/BSON codecs. Additive.
- *Ships runtime 1.2.19.*

### 1.2.3 — 2026-07-02
- **Stable** — 1.2.3 stabilises the Node binding surface. It is the last release to carry
  breaking renames/removals; the binding is stable from here.
- **Added** — ES2022 negative indexing (`.at(-1)`, with `.set(-1, …)`) on the indexed
  sequences — `ValueVector`, `ValueVec`, `ValueTuple`, ordered `ValueSet`, blob views, and
  `ValueMat` (per-axis); out-of-range still throws.
- **Added** — `toArray()` on `ValueVec` / `ValueMat`, and an iterable `ValueVec` (`for..of`,
  spread, `Array.from`) yielding `number` — or `bigint` for 64-bit ints.
- **Added** — Blob ⇆ TypedArray for GPU / WebGL — `BlobView`/`BlobArray.toTypedArray()`,
  `BlobLayout.glAttribParams()`, and `BlobArray.fromTypedArray(layout, ta)`.
- **Added** — `toJSON()` on every value (`JSON.stringify(value)` yields a JSON-ready POD;
  64-bit ints promote to a number when exact, else throw; Blob → base64). BSON
  (`toBsonBlob` / `fromBsonBlob`) and the streaming / DSM entry points that were
  not-yet-usable stubs are now bound.
- **Fixed** — argument errors cross the boundary as their real `TypeError` / `RangeError`; a
  sweep of `index.d.ts` corrected declared constructors against runtime reality; the shared
  JSON codec accepts a bare integer for a `float`/`double` field (`5` → `5.0`).
- **Breaking** — codec methods renamed to the `to…` / `from…` convention
  (`jsonEncode` → `toJsonString`, `bsonEncode` → `toBsonBlob`, …; old names removed);
  `toTuple()` → `toArray()`; the raw `ValueOpcode` codec and `Logging.create(object)` are
  removed.

### 1.2.2 — 2026-06-30
- **Added** — `hashKey()` on every value type: a 128-bit `bigint` value-identity key
  usable directly in a JS `Map` / `Set` / `Map.groupBy` (which key by identity and call
  no custom hash/equals). It folds the value's type into the hash, so width variants
  (`Int8(1)` / `Int16(1)` / `Int64(1)`) and empty typed containers stay distinct where the
  raw `hash()` is type-blind. It is a hash — collisions are possible.
- **Added** — `[Symbol.dispose]` / `using`: resource handles (`Database`, `CommitDatabase`,
  `CommitStore`, `ServiceRemote`, file streams) release deterministically at scope exit — the
  JS analogue of the Python binding's refcount finalization (guarded on engines without
  `Symbol.dispose`).
- **Added** — recursive `Value.deduce`: the `any` input bridge now deduces nested natives
  (Array → `Vector`, Set → `ValueSet`, Map → `ValueMap`, object → `Map<string, …>`, plus
  scalars / `Blob` / `Void`), inferring a heterogeneous element type as `Variant`.
- **Fixed** — `compare()` / `equals()` expose the runtime's total, trans-type order instead of
  pre-decoding the operand to the receiver's exact type and throwing on a mismatch:
  `compare(other)` orders any two values (a heterogeneous collection sorts deterministically),
  `equals(other)` is total (false across types, never raises).
- **Changed** — type declarations (`index.d.ts`) clarify `dumps` depth and the encoded vs.
  deep-projection regimes.
- *Ships runtime 1.2.17.*

### 1.2.1 — 2026-06-29
- **Added** — `ServiceRemote` by-name accessors `functionPoolFunc(poolIdOrName, name)`
  and `attachmentFunctionPoolFunc(...)` — fetch a single callable remote function
  directly, without iterating the whole pool.
- **Added** — restored the macOS Intel (x86_64) prebuilt binary; the package again
  ships a binary for every Linux / macOS / Windows × x64 / arm64 target.
- **Fixed** — `Definitions.decode` / `DefinitionsConst.encode` honor the optional
  `streamCodecInstancing` argument and default to the token-binary stream codec
  (previously pinned to the plain-binary codec), so a definitions blob round-trips at
  the default codec — consistent with the Python binding and with default-encoded
  embedded definitions.
- **Changed** — package homepage and README point at the dsviper-node documentation
  page.
- *Ships runtime 1.2.17.*

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
