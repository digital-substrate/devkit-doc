# Application Architecture

This chapter describes how to structure applications built with DSM and Viper. The
architecture separates concerns into layers, enabling code reuse across platforms and
languages.

## The 3-Tier Architecture

Applications built with Viper follow a 3-tier pattern:

```text
┌────────────────────────────────────────────────────────────┐
│  TIER 1: PRESENTATION (Platform-Specific UI)               │
│  AppKit (macOS) / Qt (cross-platform) / PySide (Python)    │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────┐
│  TIER 2: LOGIC (Context + Bridges + Components)            │
│  Application Context (orchestration), generated pools,     │
│  hand-written business code                                │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────┐
│  TIER 3: DATA (Viper Runtime)                              │
│  CommitDatabase, CommitStore, persistence, dsviper binding │
└────────────────────────────────────────────────────────────┘
```

### Tier Responsibilities

| Tier             | Responsibility                                                | Platform-Specific? |
|------------------|---------------------------------------------------------------|--------------------|
| **Presentation** | UI framework, windows, dialogs                                | Yes                |
| **Logic**        | Application Context, bridges, business components             | Partially          |
| **Data**         | Viper runtime (CommitDatabase, CommitStore), persistence      | No (shared)        |

## The Full Application Stack

For business applications with domain logic, the stack expands:

```text
┌────────────────────────────────────────────────────────────┐
│  1. UI Layer                                               │
│  Platform-specific windows, views, controllers             │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────┐
│  2. Application Context                                    │
│  Singleton orchestrator: owns the CommitStore, the         │
│  generated FunctionPools, and the application's domain     │
│  state (e.g. current GraphKey)                             │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────┐
│  3. Bridge Layer                                           │
│  Pool signatures → Business logic connection               │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────┐
│  4. Business Logic Layer                                   │
│  Hand-written domain code (Model_*)                        │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────┐
│  5. Generated Infrastructure                               │
│  Kibo output: Data, Commit, Serialization                  │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────┐
│  6. Viper Runtime                                          │
│  Core C++ engine (CommitStore, CommitDatabase),            │
│  dsviper Python binding                                    │
└────────────────────────────────────────────────────────────┘
```

## Layer Details

### Layer 1: UI

Platform-specific presentation code:

- Window management
- Menu and toolbar actions
- Dialog boxes
- Framework-native widgets

This layer changes for each target platform but follows the same logical structure.

### Layer 2: Application Context

The **Context** is the application-level singleton that orchestrates the runtime.
It is *not* a subclass of `Viper::CommitStore`: it **owns** a `CommitStore`
(provided by the Viper runtime) and adds the application-specific surface around
it — the generated `FunctionPool` / `AttachmentFunctionPool` instances, the
domain state (e.g. the current graph), and the action dispatch.

Responsibilities of the Context:

- Own the `CommitStore` (which itself holds the `CommitDatabase` and the
  current `CommitState`)
- Hold the generated tool / model / attachment `FunctionPools`
- Hold application-level domain state (e.g. `graphKey`)
- Open / close / load the database
- Dispatch user actions through `CommitMutableState`
- Expose framework-agnostic notifications via `CommitStoreNotifying`

```cpp
// Context pattern (C++) — illustrative excerpt
namespace GE {

class Context final {
public:
    static std::shared_ptr<Context> Instance();

    // Database lifecycle (owned via the store)
    void use(std::shared_ptr<Viper::CommitDatabase> const & database);
    void close();
    void load();
    static std::shared_ptr<Viper::CommitDatabase> createDatabase(
        std::filesystem::path const & filePath);

    // Domain operations
    void newGraph();
    void useNewGraph(std::string const & label);
    void dispatchAction(std::string const & label,
                        std::shared_ptr<ContextAction> const & action);

    // Owned components
    std::shared_ptr<Viper::CommitStore> store;

    std::shared_ptr<Viper::FunctionPool>           tools;
    std::shared_ptr<Viper::AttachmentFunctionPool> modelGraph;
    std::shared_ptr<Viper::AttachmentFunctionPool> modelSelection;
    std::shared_ptr<Viper::AttachmentFunctionPool> modelIntegrity;
    std::shared_ptr<Viper::AttachmentFunctionPool> attachments;

    // Domain state
    GE::Graph::GraphKey graphKey;
};

} // namespace GE
```

Action dispatch always goes through the store's `CommitMutableState`, so undo/redo
and notifications stay coherent:

```cpp
void Context::dispatchAction(std::string const & label,
                             std::shared_ptr<ContextAction> const & action) {
    auto const ms{store->mutableState()};
    action->run(ms);
    store->commitMutations(label, ms);
}
```

The previous "Store-as-application-singleton" pattern is superseded: the
generic store concerns (database, state, undo/redo, notifications) live in
`Viper::CommitStore`, and the application-specific concerns (which pools,
which domain state, which actions) live in the application's `Context`.

### Layer 3: Bridges

Bridges connect generated pool signatures to your business logic:

```cpp
// GE_AttachmentFunctionPoolBridges.hpp (GENERATED)
namespace GE::AttachmentFunctionPoolBridges {
namespace ModelGraph {

Graph::VertexKey new_vertex(std::shared_ptr<Viper::AttachmentMutating> const & attachmentMutating,
                            Graph::GraphKey const & graphKey,
                            std::int64_t value,
                            Graph::Position const & position);

}
}

// GE_AttachmentFunctionPoolBridges.cpp (HAND-WRITTEN)
Graph::VertexKey new_vertex(std::shared_ptr<Viper::AttachmentMutating> const & attachmentMutating,
                            Graph::GraphKey const & graphKey,
                            std::int64_t value,
                            Graph::Position const & position) {
    return Model::Vertex::add(attachmentMutating, graphKey, value, position,
                              Model::Random::makeColor());
}
```

### Layer 4: Business Logic

Your domain-specific code:

```cpp
// GE_Model_Vertex.cpp
VertexKey add(std::shared_ptr<AttachmentMutating> const & attachmentMutating,
              GraphKey const & graphKey,
              std::int64_t const & value,
              Position const & position,
              Color const & color) {

    auto const vertexKey{create(attachmentMutating, value, position, color)};
    Attachments::Graph_Topology::unionVertexKeys(attachmentMutating, graphKey, {vertexKey});

    return vertexKey;
}
```

### Layer 5: Generated Infrastructure

Kibo generates this layer from your DSM:

- Data types (`*_Data.cpp`)
- Commit accessors (`*_Commit.cpp`)
- Serialization (`*_Reader.cpp`, `*_Writer.cpp`)
- Database persistence (`*_Database.cpp`)
- Python proxy

### Layer 6: Viper Runtime

The core C++ engine providing:

- Type and value system
- CommitDatabase persistence
- Stateful commits
- Python binding (dsviper)

## The Notifier Pattern

UI frameworks have different notification mechanisms. The **Notifier** pattern bridges
this gap:

```{seealso}
For the Python / Qt incarnation of this pattern (the actual
`DSCommitStoreNotifier` class shipped by `dsviper-components`,
with its full Qt Signal surface), see
[dsviper-components — The Notifier Bridge](../dsviper-components/architecture.md#the-notifier-bridge).
```


```text
CommitStore (C++ core)
        │
        ▼
CommitStoreNotifying (interface)
        │
        ▼
DSCommitStoreNotifier (framework adapter)
        │
        ▼
Framework-specific notifications
```

### Common Notifications

All implementations expose the same signals:

| Signal                   | Purpose                             |
|--------------------------|-------------------------------------|
| `database_did_open`      | Database opened successfully        |
| `database_did_close`     | Database closed                     |
| `state_did_change`       | State changed (undo/redo available) |
| `definitions_did_change` | Schema updated                      |
| `dispatch_error`         | Error occurred                      |

## Multi-Language Support

The architecture supports multiple languages:

| Layer          | C++ Application                  | Python Application       |
|----------------|----------------------------------|--------------------------|
| UI             | AppKit/Qt C++                    | PySide/Qt Python         |
| Context        | C++ singleton (owns CommitStore) | Python class (owns store)|
| Business       | C++                              | Python or dsviper        |
| Infrastructure | C++ generated                    | Python generated         |
| Runtime        | Viper C++ (CommitStore, ...)     | dsviper                  |

### Python Integration

The `dsviper` module exposes the entire Viper runtime, including
`CommitStore` and `CommitDatabase`. A Python application's `Context` follows
the same pattern as the C++ one — it instantiates a `CommitStore` and wires
the generated pools around it:

```python
import dsviper

database = dsviper.CommitDatabase.create("path/to/data.cdb",
                                         "An Application Database")
store = dsviper.CommitStore.make()
store.set_database(database)

# Undo/Redo operations
if store.can_undo():
    store.undo()
```

## Design Principles

### Separation of Concerns

Each layer has a single responsibility:

- **UI**: Only presentation, no business logic
- **Context**: Orchestration only — owns the `CommitStore` and the pools, does
  not reimplement them
- **Bridges**: Connection, not logic
- **Business**: Domain rules, not infrastructure
- **Generated**: Infrastructure, not business

### Platform Isolation

Platform-specific code lives only in Layer 1. The other layers are shared or generated.

### Generated vs Hand-Written

| Generated (Kibo) | Hand-Written        |
|------------------|---------------------|
| Data types       | Business logic      |
| Serialization    | Bridges             |
| Persistence      | Store orchestration |
| Pool marshalling | UI layer            |

### Minimal Porting Effort

To port to a new platform:

1. Implement the Notifier adapter (~50 lines)
2. Create UI components matching existing patterns
3. Wire up the main window

The business logic and infrastructure remain unchanged.

## Summary

| Principle              | Implementation                                |
|------------------------|-----------------------------------------------|
| **Separation**         | 6 distinct layers with clear responsibilities |
| **Reuse**              | Layers 3-6 shared across platforms            |
| **Generation**         | Kibo generates infrastructure (Layer 5)       |
| **Multi-language**     | Same architecture for C++ and Python          |
| **Platform isolation** | Only Layer 1 is platform-specific             |

This architecture enables building complex applications that work across platforms while
minimizing duplicated code.

## What's Next

- [dsviper](../dsviper/index.rst) - Use the dsviper Python API
- [dsviper-tools](../dsviper-tools/index.rst) - Master the development tools
