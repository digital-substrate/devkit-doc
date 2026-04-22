# Code Generation

This document explains how DSM and Kibo generate application infrastructure from
declarative definitions.

## DSM: Digital Substrate Model

DSM is the data definition language for Viper applications. It defines concepts,
structures, enumerations, clubs, attachments, and function pools.

### Complete Example: Graph.dsm

```dsm
// Namespace with UUID - ensures global uniqueness
namespace Graph {27c49329-a399-415c-baf0-db42949d2ba2} {

// Concepts - abstract entities identified by Key<Concept>
"""A graph."""
concept Graph;

"""A vertex in a graph."""
concept Vertex;

"""An edge in a graph."""
concept Edge;

// Structures - named fields with types, can nest other structures
"""The vertices and edges of the graph topology."""
struct GraphTopology {
    set<key<Vertex>> vertexKeys;   // set<> = ordered unique collection
    set<key<Edge>> edgeKeys;       // key<Concept> = typed reference
};

"""An edge in the graph topology."""
struct EdgeTopology {
    key<Vertex> vaKey;             // References to vertices
    key<Vertex> vbKey;
};

"""A Position."""
struct Position {
    float x;
    float y;
};

"""An RGB Color."""
struct Color {
    float red;
    float green;
    float blue;
};

"""The visual attributes of a vertex."""
struct VertexVisualAttributes {
    int64 value;
    Color color;                   // Nested structure
};

// Attachments - key-document associations for Database storage
// Syntax: attachment<ConceptType, DocumentType> name

"""The topology of a graph."""
attachment<Graph, GraphTopology> topology;

"""A collection of tags for a graph."""
attachment<Graph, map<string, string>> tags;  // [map<K,V> = dictionary]

"""A collection of comments for a Graph."""
attachment<Graph, xarray<string>> comments;   // [xarray = CRDT ordered list]

"""The render attributes used to render a vertex in 2D."""
attachment<Vertex, Position> position;

"""The visual attributes of a vertex."""
attachment<Vertex, VertexVisualAttributes> visualAttributes;

"""An Edge in the graph topology."""
attachment<Edge, EdgeTopology> topology;

};
```

---

## Enumeration Example

```dsm
// Enumerations - named cases
"""Horizontal alignment options."""
enum HorizontalAlignment {
    left,
    middle,
    right
};

"""Vertical alignment options."""
enum VerticalAlignment {
    top,
    middle,
    bottom
};

// Enum usage in struct with default value via .case syntax
"""Layer alignment properties."""
struct LayerAlignment {
    HorizontalAlignment horizontal = .middle;  // [Default: middle]
    VerticalAlignment vertical = .bottom;      // [Default: bottom]
};
```

---

## Attachment Function Pool Example

```dsm
// attachment_function_pool = functions that use un Attachment interface
// AttachmentMutating or AttachmentGetting
// Pool UUID ensures cross-language identity

"""This pool provides access to functions used to edit the graph topology."""
attachment_function_pool ModelGraph {9bdcbb5b-76e9-426f-b8a6-a10ed2d949e6} {

// [mutable = modifies commit state, returns new key]
"""Create a vertex with the specified attributes."""
mutable key<Vertex> newVertex(key<Graph> graphKey, int64 value, Position position);

"""Create a new edge."""
mutable key<Edge> newEdge(key<Graph> graphKey, key<Vertex> vaKey, key<Vertex> vbKey);

// [mutable void = modifies state, returns nothing]
"""Set the vertex position."""
mutable void setVertexPosition(key<Vertex> vertexKey, Position position);

"""Move the vertices by the offset."""
mutable void moveVertices(set<key<Vertex>> vertexKeys, Position offset);

"""Clear the graph."""
mutable void clearGraph(key<Graph> graphKey);

// [xarray operations via position UUID, not index]
"""Append a new comment."""
mutable void appendGraphComment(key<Graph> graphKey, string comment);

// [map operations]
"""Replace or insert the tag."""
mutable void setGraphTag(key<Graph> graphKey, string key, string value);

};
```

---

## Function Pool Example

```dsm
// function_pool = pure functions, no attachment 

"""This pool provides access to the various utility functions."""
function_pool Tools {dc9740c9-9d1d-4c1e-9caa-4c8843b91e82} {

"""Return a + b."""
int64 add(int64 a, int64 b);              // [Pure function, returns value]

"""Return true if a is even."""
bool isEven(int64 a);

"""Return true if a > b."""
bool isGreater(any a, any b);             // [any = accepts any Viper type]

"""Return a random word."""
string randomWord(uint64 size);

};
```

---

## Kibo: Code Generator

Kibo (`tools/kibo-*.jar`) reads DSM definitions and generates infrastructure code:

```
DSM Definition    ->    Kibo Generator    ->    C++/Python Infrastructure
   (273 lines)                                     (15,592 lines)
                                                      (57:1 ratio)
```

### What Kibo Generates

| Output               | Description                                |
|----------------------|--------------------------------------------|
| C++ Headers          | Typed accessors, structures, serialization |
| Python Classes       | Proxy classes with type hints              |
| Type Mappings        | DSM types to Viper types                   |
| Serialization        | Binary/JSON encoding for all defined types |
| Attachment Accessors | Type-safe get/set/keys for each attachment |

### What Kibo Does NOT Generate

| Not Generated   | Where It Lives                              |
|-----------------|---------------------------------------------|
| Viper Runtime   | Hand-written C++ (`src/Viper/`, ~600 files) |
| P_Viper Binding | Hand-written Python C/API (`src/P_Viper/`)  |
| Business Logic  | Your application code                       |

---

## The Dual Reality

Kibo-generated code operates in two realities:

```
                         DSM (declarative)
                               |
                               v
                    +----------------------+
                    |  Kibo Code Generator |
                    +----------------------+
                         |           |
          +--------------+           +--------------+
          v                                         v
+-----------------------------+     +-----------------------------+
|     C++ Static API          |     |    Python Proxy API         |
|  (compile-time checking)    |     |    (type hints + runtime)   |
+-----------------------------+     +-----------------------------+
          |                                         |
          +------------------+----------------------+
                             v
          +------------------------------------------+
          |   Viper Dynamic Runtime (strongly typed) |
          +------------------------------------------+
```

### Developer Reality (Static)

Generated code provides compile-time safety. It wraps the Viper runtime API:

```cpp
// Viper runtime API (hand-written in src/Viper/)
class AttachmentGetting {
    virtual std::shared_ptr<ValueSet> keys(
        std::shared_ptr<Attachment> const & attachment) const = 0;

    virtual std::shared_ptr<ValueOptional> get(
        std::shared_ptr<Attachment> const & attachment,
        std::shared_ptr<ValueKey> const & key) const = 0;
};

class AttachmentMutating : public AttachmentGetting {
    virtual void set(std::shared_ptr<Attachment> const & attachment,
                     std::shared_ptr<ValueKey> const & key,
                     std::shared_ptr<Value const> const & value) = 0;

    virtual void update(std::shared_ptr<Attachment> const & attachment,
                        std::shared_ptr<ValueKey> const & key,
                        std::shared_ptr<Path const> const & path,
                        std::shared_ptr<Value const> const & value) = 0;
};
```

### Runtime Reality (Dynamic)

Generated code consumes the Viper runtime:

```cpp
// Generated code uses Viper
#include "Viper_Value.hpp"
#include "Viper_AttachmentGetting.hpp"
```

```python
# Generated code uses dsviper
import dsviper
```

---

## Amplification Ratio

DSM provides significant code amplification:

| Project       | DSM Lines | Generated Lines | Ratio |
|---------------|-----------|-----------------|-------|
| Graph Editor  | 273       | 15,592          | 57:1  |
| Raptor Editor | ~2,000    | ~126,000        | 63:1  |

### 3-Tier Code Distribution

| Tier                     | Description          | Typical % |
|--------------------------|----------------------|-----------|
| **Infrastructure** (gen) | Kibo-generated code  | 66-69%    |
| **Business Logic** (man) | Domain-specific code | 10-25%    |
| **UI/Application** (man) | User interface       | 6-24%     |

---

## Workflow

### 1. Define DSM

Create `.dsm` files describing your data model:

```bash
myapp/
  model/
    Graph.dsm
    Pool_ModelGraph.dsm
```

### 2. Validate

Check DSM syntax and semantics:

```bash
python3 tools/dsm_util.py check model/Graph.dsm
```

### 3. Generate

Run Kibo to generate code:

```bash
python3 tools/dsm_util.py generate model/
```

### 4. Build

Build generated code with your application:

```bash
cmake --build build
```

---

## Key Distinction

| Component         | Nature        | Location                    |
|-------------------|---------------|-----------------------------|
| Viper Runtime     | Hand-written  | `src/Viper/` (~600 files)   |
| P_Viper Binding   | Hand-written  | `src/P_Viper/` (48K LOC)    |
| Kibo Templates    | Hand-written  | `templates/cpp/`, `python/` |
| Application Infra | **Generated** | Your project output         |
| Business Logic    | Hand-written  | Your application code       |

Kibo generates application INFRASTRUCTURE. Your business logic is written by hand. Viper
Runtime is built separately and used by both generated and manual code.

---

## See Also

- [Viper Architecture](viper_architecture.md) - Runtime layers
- [Type System](viper_type_system.md) - DSM types map to Viper types
- [Services](services.md) - RPC for function pools
