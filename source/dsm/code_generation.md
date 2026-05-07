# Code Generation

Kibo generates application infrastructure from DSM definitions. The developer
focuses on business logic while Kibo handles repetitive plumbing.

## Why Generate Code?

### The Amplification Effect

For every line of DSM, Kibo generates approximately 57 lines of C++ and Python:

| Project                    | DSM Lines | Generated Lines | Ratio |
|----------------------------|-----------|-----------------|-------|
| Graph Editor (Pilot)       | 273       | 15,592          | 57x   |
| Raptor Editor (Industrial) | 2,003     | 126,182         | 63x   |

### What Gets Generated vs What You Write

| Category            | Who Writes It | Examples                              |
|---------------------|---------------|---------------------------------------|
| **DSM definitions** | Developer     | `Graph.dsm`, `Pool_ModelGraph.dsm`    |
| **Infrastructure**  | Kibo          | Serialization, persistence, accessors |
| **Business logic**  | Developer     | Domain rules, algorithms, UI          |

The generated infrastructure handles:

- Type-safe data structures
- Attachment accessors (get/set/keys via abstract interfaces)
- Database persistence layer
- Binary and JSON serialization
- Python bindings
- RPC marshalling

## The Double Reality

Kibo creates two coexisting realities that are bridged transparently:

### Developer Reality

What you see and code:

- Static C++ types with IDE support
- STL containers (`std::vector`, `std::map`)
- Compile-time type errors
- Idiomatic, readable code

```cpp
// Developer writes natural C++
MyStruct data{"hello", {1, 2, 3}};
data.items.push_back(42);
```

### Runtime Reality

What happens behind the scenes:

- Metadata-driven operations
- Reference semantics with `shared_ptr`
- Automatic serialization
- Python interoperability
- RPC without manual marshalling

```text
┌─────────────────────────────────┐
│  Developer Reality              │
│  Static C++ types, Python types │
│  MyStruct data{"hello", ...};   │
└─────────────────────────────────┘
═══════════════════════════════════
┌─────────────────────────────────┐
│  Runtime Reality                │
│  Dynamic metadata, shared_ptr   │
│  Serialization, RPC             │
└─────────────────────────────────┘
```

The developer writes idiomatic C++ and never sees the runtime reality—Kibo
generates the bridge code.

## Generated Layers

### 1. Data Layer

Generates type-safe business types:

- Concept keys (`VertexKey`, `EdgeKey`)
- Structures as C++ classes
- Enumerations
- Hash functions for containers

```dsm
// DSM input
concept Vertex;
struct Position { float x; float y; };
```

```cpp
// Generated output
class VertexKey { ... };
struct Position { float x; float y; };
```

### 2. Attachments Layer

Generates stateful accessors for attachments:

```cpp
// Generated accessor API
auto topology = Attachments::Graph_Topology::get(attachmentGetting, graphKey);
Attachments::Graph_Topology::set(attachmentMutating, graphKey, newTopology);
Attachments::Graph_Topology::unionVertexKeys(attachmentMutating, graphKey, {key});
```

### 3. Database Layer

Generates persistence without writing SQL:

- SQLite backend for local storage
- Remote database client for RPC
- CRUD operations for all attachments

### 4. Serialization Layer

Generates two-way converters:

- Binary serialization (efficient, compact)
- JSON serialization (human-readable)
- C++ ↔ Viper Value bridge

### 5. Function Pool Layer

Generates function exposure:

- Marshalling between C++ and Viper
- Marshalling Python and Viper
- RPC server and client stubs

### 6. Python Package Layer

Generates a complete Python package:

```python
# Generated Python package
import ge.data as ged
import ge.attachments as gea

# Use generated types
vertex_key = ged.Graph_VertexKey.create()
position = ged.Position()
position.x = 10.0
position.y = 20.0

# Use generated accessors
gea.graph_vertex_render2d_attributes_set(
    attachment_mutating, vertex_key, position
)
```

## The Bridge Pattern

The **Bridge** connects your business logic to DSM-declared functions:

```text
┌────────────────────────────────────────────┐
│  DSM (Pool_ModelGraph.dsm)                 │
│  mutable key<Vertex> newVertex(...)        │
└─────────────────────┬──────────────────────┘
                      │ generates
┌─────────────────────▼──────────────────────┐
│  Bridge.hpp (GENERATED - contract)         │
│  VertexKey new_vertex(...);                │
└─────────────────────┬──────────────────────┘
                      │ implements
┌─────────────────────▼──────────────────────┐
│  Bridge.cpp (BUSINESS - hand-written)      │
│  return Model::Vertex::add(...);           │
└─────────────────────┬──────────────────────┘
                      │ exposes via
┌─────────────────────▼──────────────────────┐
│  FunctionPools.cpp (GENERATED)             │
│  Value ↔ C++ marshalling                   │
└─────────────────────┬──────────────────────┘
          ┌───────────┴───────────┐
          ▼                       ▼
   Python Local            Remote RPC
```

### Example Workflow

**1. DSM Declaration:**

```dsm
attachment_function_pool ModelGraph {9bdcbb5b-76e9-426f-b8a6-a10ed2d949e6} {
    mutable key<Vertex> newVertex(key<Graph> graphKey, int64 value, Position position);
};
```

**2. Bridge Header (Generated):**

```cpp
// GE_AttachmentFunctionPoolBridges.hpp - GENERATED by Kibo
namespace GE::AttachmentFunctionPoolBridges {
namespace ModelGraph {

Graph::VertexKey new_vertex(std::shared_ptr<Viper::AttachmentMutating> const & attachmentMutating,
                            Graph::GraphKey const & graphKey,
                            std::int64_t value,
                            Graph::Position const & position);

}
}
```

**3. Bridge Implementation (Business):**

```cpp
// GE_AttachmentFunctionPoolBridges.cpp - HAND-WRITTEN
Graph::VertexKey new_vertex(std::shared_ptr<Viper::AttachmentMutating> const & attachmentMutating,
                            Graph::GraphKey const & graphKey,
                            std::int64_t value,
                            Graph::Position const & position) {
    return Model::Vertex::add(attachmentMutating, graphKey, value, position,
                              Model::Random::makeColor());
}
```

**4. Call from Python:**

```python
# Automatically available in Python
vertex_key = pool.new_vertex(commit, graph_key, 42, position)
```

## Workflow Summary

```text
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Write DSM       │     │  Run Kibo        │     │  Write Business  │
│  definitions     │ ──► │  code generator  │ ──► │  logic in        │
│  (273 lines)     │     │                  │     │  Bridge.cpp      │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  Generated Infrastructure │
                    │  - Data types             │
                    │  - Serialization          │
                    │  - Persistence            │
                    │  - Python proxy           │
                    │  (15,592 lines)           │
                    └───────────────────────────┘
```

## Benefits

| Benefit                | Explanation                                                      |
|------------------------|------------------------------------------------------------------|
| **Less code to write** | 57x amplification means 57x less code to maintain                |
| **Type safety**        | Generated code is type-safe, reducing runtime errors             |
| **Consistency**        | All serialization and persistence follows the same patterns      |
| **Multi-language**     | Same DSM generates C++ and Python code                           |
| **Evolution**          | Change DSM, regenerate, and infrastructure updates automatically |

## What's Next

- [Architecture](architecture.md) - Application structure with generated code
- [Kibo](../kibo/usage.md) - Using the Kibo code generator
