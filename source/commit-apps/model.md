# Commit Application Model

The **Commit Application Model** is the architectural pattern shared
by every application built on the Commit Engine. It defines how an
application composes a `CommitStore` (provided by the Viper runtime)
with its own domain state, dispatch surface, and platform
notifications, so that all state changes flow through the
[commit DAG](../commit/commit.md) with built-in undo/redo, multi-author
convergence, and audit trail.

The walkthroughs that follow this page — `cdbe.py`, [ge-py](ge-py.md),
[ge-qml](ge-qml.md), [web-cdbe](web-cdbe.md) — are concrete
**instances** of this single Model, in different languages and on
different presentation tiers. The Model is what they have in common.

> `dbe.py` is **not** an instance of this model. It is a plain CRUD
> inspector for the non-versioned `Database` backend — it does not use
> a `CommitStore` and does not flow through a commit DAG. Outside the
> pattern.


## The Application Context

The pattern is centred on an **Application Context** — a
singleton (or per-document object) that owns the `CommitStore` and
exposes the application's surface to the UI and to scripts.

Composition, not subclassing. The Context **owns** a `CommitStore`
provided by the runtime; it does not extend it.

The Context is responsible for four things:

1. **Owning** the `CommitStore` (which itself holds the
   `CommitDatabase` and the current `CommitState`).
2. **Holding** application-level domain state — the keys, selections,
   or session-level data not committed to the DAG.
3. **Dispatching** user actions through the store, so every mutation
   becomes a commit.
4. **Notifying** the UI through a platform-agnostic interface, so the
   same Context can drive Qt Widgets, QML, AppKit, or a web view
   without changing the core code.

In C++, the Context additionally holds the generated **function
pools** (see below). In Python, function pools are unnecessary and
the Context holds direct references to the business-logic modules.


## Two language profiles

The same Model takes two slightly different shapes depending on the
language of the business logic. The difference is **whether function
pools are needed to cross a language boundary**.


### C++ profile — six layers, with function pools

When business logic is written in C++ and needs to be reachable from
Python scripting, the Application Context exposes generated
**function pools** that bridge the two languages.

```text
┌─────────────────────────────────────────────────────────────┐
│  1. UI Layer (AppKit / Qt Widgets / QML / …)                │
│     ViewControllers + components + notifications            │
├─────────────────────────────────────────────────────────────┤
│  2. Application Context (CommitStore Layer)                 │
│     Singleton: store + state + notifier + pools             │
├─────────────────────────────────────────────────────────────┤
│  3. Bridge Layer (hand-written)                             │
│     Pool bridges (FunctionPool + AttachmentFunctionPool)    │
│     dispatch generated pool calls into business logic       │
├─────────────────────────────────────────────────────────────┤
│  4. Business Logic Layer (hand-written, in C++)             │
│     Domain functions: Vertex, Edge, Graph, …                │
├─────────────────────────────────────────────────────────────┤
│  5. Generated Infrastructure (Kibo)                         │
│     Data, Database, ValueEncoder, FunctionPools             │
├─────────────────────────────────────────────────────────────┤
│  6. Viper Runtime (C++)                                     │
│     Type, Value, Commit, Database, RPC                      │
└─────────────────────────────────────────────────────────────┘
```

Function pools (and their bridges) exist for **two reasons**:

* They expose C++ business logic to the **Viper runtime** through a
  typed surface — typed methods registered with Viper's type system,
  whose implementations are routed to hand-written C++ code through
  the generated pool bridges.
* They give the dispatch layer a uniform handle on actions —
  `store->dispatch("label", pool.function, args...)` — without
  knowing where the implementation lives.

Once a pool is registered with Viper, **its Python availability is
free**. Viper's "Metadata Everywhere" principle means every value
and every function carries its type metadata at runtime; `dsviper`
(the hand-maintained Python wrapper of Viper, shipped as a wheel on
PyPI) introspects registered pools and calls them with automatic
marshalling between Python values and Viper values. No per-pool
Python binding is generated, none is written by hand — the same
mechanism that lets `dsviper` expose any Viper type to Python
exposes the pools too.

#### How pools reach Python — Context injection + Viper introspection

The application embeds CPython, imports `dsviper` and a thin `app`
extension module that publishes the Python wrapper of the Context, and
injects the Context singleton as a Python global (typically `ctx`). From
there, every pool held by the Context is callable directly:
`ctx.modelGraph.new_vertex(...)` reaches the hand-written C++
implementation through the generated pool bridge, with Python ↔ Viper
marshalling handled automatically by `dsviper` from the runtime metadata.
No per-pool binding code is written or generated.

This mirrors what `PythonEditorModel(..., namespace_vars={...})` does for
the Python profile. The two profiles converge on the same scripting
surface — `ctx.dispatch("label", ...)` against the store — and differ only
in whether the business functions are Python (Python profile) or C++
fronted by typed pools (C++ profile).

A real Application Context, abridged from the Graph Editor C++
reference (`GE::Context`):

```cpp
namespace GE {

class Context final {
public:
    static std::shared_ptr<Context> Instance();

    // Database lifecycle
    void use(std::shared_ptr<Viper::CommitDatabase> const & database);
    void close();
    void load();
    void reset();

    // Domain actions
    void newGraph();
    void useNewGraph(std::string const & label);
    void dispatchAction(std::string const & label,
                        std::shared_ptr<ContextAction> const & action);

    // Composed runtime
    std::shared_ptr<Viper::CommitStore> store;

    // Generated function pools
    std::shared_ptr<Viper::FunctionPool>            tools;
    std::shared_ptr<Viper::AttachmentFunctionPool>  modelGraph;
    std::shared_ptr<Viper::AttachmentFunctionPool>  modelSelection;
    std::shared_ptr<Viper::AttachmentFunctionPool>  modelIntegrity;
    std::shared_ptr<Viper::AttachmentFunctionPool>  attachments;

    // Domain state (not committed to the DAG)
    GE::Graph::GraphKey graphKey;

private:
    Context();
};

} // namespace GE
```

Note the four ingredients of the pattern in plain sight: the
`Instance()` singleton, the `store` (composed, not inherited), the
typed function pools, and the domain state (`graphKey`). The
notification adapter is held by the store itself.


### Python profile — five layers, no function pools

When business logic is **already in Python**, there is no language
boundary to cross. Function pools become redundant: the dispatch
lambda calls the model functions directly.

```text
┌─────────────────────────────────────────────────────────────┐
│  1. UI Layer (Qt Widgets, QML, HTML/CSS, …)                 │
│     Framework-specific presentation                         │
├─────────────────────────────────────────────────────────────┤
│  2. Application Context (CommitStore facade)                │
│     Owns the store, exposes domain state and dispatch       │
├─────────────────────────────────────────────────────────────┤
│  3. Business Logic (hand-written Python)                    │
│     model/*.py — direct calls, no pool indirection          │
├─────────────────────────────────────────────────────────────┤
│  4. Generated Data (Kibo output)                            │
│     Data classes, attachments, definitions                  │
├─────────────────────────────────────────────────────────────┤
│  5. dsviper Runtime (C++ binding)                           │
│     CommitStore, CommitDatabase, CommitMutableState, Value  │
└─────────────────────────────────────────────────────────────┘
```

A real Python Application Context, abridged from `ge-py`
(`model/context.py`):

```python
class Context:
    @classmethod
    def instance(cls) -> "Context":
        if not hasattr(cls, "_instance"):
            setattr(cls, "_instance", cls())
        return getattr(cls, "_instance")

    def __init__(self):
        self.store = CommitStore()
        self.graph_key = Graph_GraphKey.create()

    # Database lifecycle
    def use(self, database: CommitDatabase): ...
    def close(self): ...
    def load(self): ...
    def reset(self): ...

    # Domain actions
    def new_graph(self): ...
    def use_new_graph(self, label: str): ...

    # Dispatch — direct, no pool indirection
    def dispatch(self, label: str, func, *args):
        self.store.dispatch(label, func, *args)
```

Same three ingredients as the C++ Context: singleton, composed
`store`, domain state (`graph_key`). The function-pool block is
absent — Python business logic in `model/*.py` is called directly
from the dispatch lambda.

This profile applies to all four Commit Applications shipped or
walked through in the DevKit:

| Application                | Domain                | UI tier                  |
|----------------------------|-----------------------|--------------------------|
| `cdbe.py`                  | Generic (no domain)   | Qt Widgets (PySide6)     |
| [ge-py](ge-py.md)          | Graph                 | Qt Widgets (PySide6)     |
| [ge-qml](ge-qml.md)        | Graph                 | Qt Quick / QML (PySide6) |
| [web-cdbe](web-cdbe.md)    | Generic (no domain)   | Server-rendered HTML/CSS |

`cdbe.py` and `web-cdbe` are **generic** — they have no DSM model
of their own and no Kibo-generated infrastructure. They open any
`CommitDatabase` through the dynamic introspection API, which means
their layer 3 (business logic) and layer 4 (generated data) collapse
to a thin glue layer over the runtime. The pattern still applies, but
with three layers in practice instead of five.

`ge-py` and `ge-qml` are **domain-specific** — they have a DSM model
(`Graph`, `Vertex`, `Edge`), Kibo-generated typed accessors, and
hand-written Python business logic. They are the full five-layer
instances of the Model.


## The dispatch pattern

All state mutations go through `dispatch`. The store creates a
mutable snapshot, runs the function, persists the resulting commit,
and notifies observers — atomically.

In C++, dispatch takes a pool function:

```cpp
store->dispatch("Create Vertex",
    [&](auto const & attachmentMutating) {
        Model::Vertex::add(attachmentMutating, graphKey, value, position);
    });
```

In Python, dispatch takes a lambda calling business logic directly
(no pool indirection):

```python
store.dispatch("Create Vertex",
    lambda m: model.vertex.add(m, graph_key, value, position))
```

After the lambda returns, the store has:

* Created an immutable `CommitState` snapshot from the mutations.
* Persisted the commit into the DAG.
* Notified observers via the notification contract (below).


## The notification contract

The store communicates with the UI through a small, framework-agnostic
interface (`CommitStoreNotifying`). Each platform adapts it to the
local notification mechanism (Adapter pattern):

| Signal                    | Purpose                             |
|---------------------------|-------------------------------------|
| `notifyDatabaseDidOpen`   | Database opened successfully        |
| `notifyDatabaseDidClose`  | Database closed                     |
| `notifyDatabaseWillReset` | Reset is about to occur             |
| `notifyStateDidChange`    | State changed (undo/redo available) |
| `notifyDispatchError`     | Error occurred during dispatch      |

The bridges are platform-specific: `NSNotificationCenter` (AppKit),
Qt signals (Qt C++ and PySide), or any other observer mechanism.
The Application Context never imports a UI framework — it speaks
`CommitStoreNotifying` and lets a per-platform adapter publish.


## The dual-layer contract

The Commit Engine guarantees **structural integrity** — typed
mutations land cleanly in the DAG, the commit graph stays
consistent, undo/redo behaves deterministically. It does **not**
guarantee **semantic integrity** — that the application's domain
invariants are upheld.

That responsibility belongs to the Application Context. The pattern
asks the application to validate its own domain rules **at
consumption time**, not at write time, because a commit may have been
authored elsewhere (different version, different author) and only
discovered locally on sync.

See [The Dual-Layer Contract](../commit/commit_contract.md) for the
full rationale and the where-to-validate decision tree.


## Generic versus domain-specific instances

The same Model produces two distinct kinds of application:

* **Generic instances** — `cdbe.py` and `web-cdbe`. No DSM model, no
  Kibo output, no business logic. They open any `CommitDatabase` and
  drive its commit DAG through the dynamic introspection API of the
  runtime. Their value is universality.

* **Domain-specific instances** — `ge-py`, `ge-qml`, and any
  third-party Commit Application. They have a DSM model that defines
  the domain (graphs, materials, schedules, …), Kibo-generated typed
  accessors, and hand-written business logic that encodes the domain
  rules. Their value is fidelity to a specific use case.

Both instantiate the same Model. The difference is what fills layers
3 and 4: glue over the dynamic API, or generated typed code over the
domain.


## Pattern lineage

The Commit Application Model is a disciplined synthesis of three
established application patterns:

| Pattern                | What it contributes                            |
|------------------------|------------------------------------------------|
| **Redux / Flux**       | Single store, dispatch, unidirectional flow   |
| **CQRS** (CQS-leaning) | Read interface and mutation interface separated |
| **Observer (Adapter)** | Notifier bridge to the platform UI            |

What's specific is the integration with the Commit Engine: persistence,
history, branching, and multi-author convergence are intrinsic rather than
bolted on.


## Implementing your own

To build a new Commit Application:

1. Define your domain in [DSM](../dsm/index.rst).
2. Generate the typed infrastructure with
   [Kibo](../kibo/index.rst) and the
   [kibo-template-viper](../kibo-template-viper/index.rst) pack.
3. Write your Application Context: own a `CommitStore`, expose your
   domain state and dispatch surface, hold your business logic.
4. Adapt `CommitStoreNotifying` to your UI framework.
5. Build your UI on top of the notifications.

The walkthroughs that follow this page show this in real code, on
three different presentation tiers.
