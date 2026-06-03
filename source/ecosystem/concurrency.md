# Concurrency posture

Viper assumes the **caller owns synchronization**. The core runtime
carries no internal locking — concurrency control is provided *around*
it (at the server layer, and for Python at the GIL), never *inside* it.
Same delegation stance as the {doc}`security` posture, on memory rather
than the network.

## The C++ runtime

The core — type and value system, {term}`definitions`, codecs, and the
commit machinery — contains no synchronization primitives by design.

| Object class | Built-in guarantee | Caller responsibility |
|---|---|---|
| **Immutable** — scalar / leaf values (primitives, `Enumeration`, `Key`, `Void`), content-addressed {term}`commits <commit>`, `Type` / codec flyweights | freely shareable across threads, read-only | none |
| **`Definitions`** | concurrent reads are safe once fully built | build on one thread; afterwards hold and share as `shared_ptr<Definitions const>`, never mutate it while shared (see below) |
| **Mutable values** — every non-scalar value: `Vector` / `Map` / `Set`, `Tuple` / `XArray` / `Vec` / `Mat` / `Structure`, `Optional` / `Variant` / `Any` | none | serialize all access yourself, or hand off a `copy()` snapshot. `Optional` / `Variant` / `Any` are mutable too (`wrap` / `clear`) — do not treat them as constant when shared |
| **{term}`CommitStore`** | none | own one per context; never share an instance across threads |
| **Server layer** — {term}`Services <Service>`, `commit_database_server` | provides its own concurrency: per-connection isolation, or read-only sharing behind a single-writer mutex | — |

## The `Definitions` const handle

`Definitions` has no enforced freeze — no `freeze()`, no flag. Its
read-safety rests on a convention: after building, only ever hold it as
`shared_ptr<Definitions const>`. The `const` is a property of the
**handle**, not the object — a single non-`const` handle leaking to
another thread silently re-opens the write path, with no compile error
and no runtime guard. The runtime's own server respects this (it
serializes its lone writer); an embedder must too.

## The GIL and dsviper

The Python binding changes the picture, because CPython's Global
Interpreter Lock is the de-facto concurrency boundary for the wheel.

**Today the GIL serializes everything.** The binding never releases the
GIL: a dsviper call holds it for its whole duration, so two Python
threads can never run Viper C++ code at the same time. The core's lack of
internal locking is therefore invisible and harmless through the wheel —
none of the C++ hazards above can manifest from Python threads, because
there is no true concurrency to expose them.

> dsviper's thread-safety through the wheel is the GIL's doing, not the
> runtime's.

**What the GIL does not cover:**

- **C++ threads.** The server front-ends spawn real OS threads that run
  outside the GIL; their safety comes from the server layer's own
  concurrency, not the GIL. An embedder running its own C++ threads gets
  no protection from it.
- **A future GIL-release boundary.** If a later binding releases the GIL
  around blocking work (RPC, SQLite, a heavy decode), the
  caller-synchronization rules above immediately apply to Python code
  too.

**Performance.** Because the GIL is held for the whole call, multiple
Python threads doing dsviper work get no parallelism — they serialize —
and a long C++ operation blocks all Python threads for its duration. Real
parallelism today means `multiprocessing`, or the C++ server layer (real
OS threads, outside the GIL).

**Free-threaded interpreters (PEP 703).** dsviper declares no
free-threading support, so importing it on a free-threaded build
re-enables the GIL (CPython's compatibility fallback) — safe by
forfeiting parallelism rather than racing. Without the GIL, every
"caller-synchronized" hazard above would be a live Python data race.

## Guidance by consumer

- **Python / wheel (today):** dsviper is safe to call from multiple
  threads — the GIL serializes them — but you get no parallelism from it.
  Do not assume free-threading; the current wheel falls back to the GIL
  there.
- **C++ direct:** share immutables freely; synchronize mutables yourself;
  keep `Definitions` `const` after building; one `CommitStore` per
  context.
- **Server embedders:** rely on the server layer's own concurrency
  (per-connection isolation, the Definitions-extend mutex); do not add a
  second sharing layer over the same objects.
