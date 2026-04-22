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
│  TIER 2: LOGIC (Bridges + Store + Components)              │
│  Generated pools, hand-written business code               │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────┐
│  TIER 3: DATA (Viper Runtime)                              │
│  CommitDatabase, persistence, dsviper binding              │
└────────────────────────────────────────────────────────────┘
```

### Tier Responsibilities

| Tier             | Responsibility                      | Platform-Specific? |
|------------------|-------------------------------------|--------------------|
| **Presentation** | UI framework, windows, dialogs      | Yes                |
| **Logic**        | Bridges, Store, business components | Partially          |
| **Data**         | Viper runtime, persistence          | No (shared)        |

## The Full Application Stack

For business applications with domain logic, the stack expands:

```text
┌────────────────────────────────────────────────────────────┐
│  1. UI Layer                                               │
│  Platform-specific windows, views, controllers             │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────┐
│  2. Store Layer                                            │
│  Application store + generated pools                       │
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
│  Core C++ engine, dsviper Python binding                   │
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

### Layer 2: Store

The **Store** orchestrates the application:

- Holds the database reference
- Manages application state
- Provides undo/redo
- Dispatches notifications to UI

```cpp
// Store pattern (C++)
class Store {
public:
    void createGraph(string label);
    void newVertex(Position position);
    void deleteSelection();

    CommitDatabase* database();
    bool canUndo();
    void undo();
};
```

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

| Layer          | C++ Application | Python Application |
|----------------|-----------------|--------------------|
| UI             | AppKit/Qt C++   | PySide/Qt Python   |
| Store          | C++ singleton   | dsviper            |
| Business       | C++             | Python or dsviper  |
| Infrastructure | C++ generated   | Python generated   |
| Runtime        | Viper C++       | dsviper            |

### Python Integration

The `dsviper` module exposes the entire Viper runtime:

```python
from dsviper import CommitStore, CommitDatabase

# Open database
database = CommitDatabase.open("path/to/data.cdb")
store = CommitStore.instance()
store.use(database)

# Undo/Redo operations
if store.can_undo():
    store.undo()
```

## Design Principles

### Separation of Concerns

Each layer has a single responsibility:

- **UI**: Only presentation, no business logic
- **Store**: Orchestration, not implementation
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

- [Python Guide](../python/index.rst) - Use the dsviper Python API
- [Toolchain](../tools/index.rst) - Master the development tools
