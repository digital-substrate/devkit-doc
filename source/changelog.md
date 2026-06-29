# Release notes

User-facing release notes for the Viper runtime and the two `dsviper` bindings.

There is **one runtime contract** — Viper C++ on the `1.2` line (`MAJOR.MINOR`) —
delivered through **two installable packages**, each with its **own independent
`PATCH` stream**:

- **dsviper** — the Python wheel on PyPI (`pip install dsviper`)
- **@digitalsubstrate/dsviper** — the Node.js binding on npm

See {doc}`ecosystem/naming` for how these names relate. The Viper C++ runtime is
**not installed on its own** — it ships inside both packages; each binding entry
notes the runtime version it carries. Only released versions are listed, and
**breaking** changes are flagged inline.

## Viper C++ runtime

The engine shipped inside both bindings; `viperVersion()` reports this version.
Releases with no runtime change are omitted.

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

## dsviper (Python)

The PyPI wheel (`pip install dsviper`). Its `PATCH` stream is independent of the
runtime; each release notes the runtime version it ships.

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
- *Ships runtime 1.2.17.*

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
- **Changed** — the Python unit suite moved to the public, MIT-licensed
  [`dsviper-tests`](https://github.com/digital-substrate/dsviper-tests) repo; the
  publish pipeline self-gates on it. Added cross-codec round-trip equivalence
  tests (`DSMDefinitions`: binary ↔ JSON ↔ BSON).
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
