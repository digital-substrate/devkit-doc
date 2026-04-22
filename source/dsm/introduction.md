# Introduction to DSM

The **Digital Substrate Model (DSM)** is a domain-specific language (DSL) for defining
data models. DSM enables you to define aggregates of information linked by unique,
strongly-typed keys to construct complex structured data.

## The Five Fundamental Notions

To define a structured and flexible data model, DSM introduces five fundamental notions:

| Notion         | Description                                           | Example                          |
|----------------|-------------------------------------------------------|----------------------------------|
| **Namespace**  | A space where types are defined, identified by a UUID | `namespace Graph {27c49329-...}` |
| **Concept**    | An abstract thing (like an abstract type)             | `concept Vertex;`                |
| **Key**        | A way to identify an instance of a Concept            | `key<Vertex>`                    |
| **Document**   | A piece of information expressible in the type system | `struct Login { ... }`           |
| **Attachment** | A way to associate a Document with a Key              | `attachment<User, Login> login;` |

### Namespace

A namespace groups related definitions and provides isolation. Each namespace has a
unique UUID that serves as the seed to generate RuntimeIds for all types defined within.

```dsm
namespace Graph {27c49329-a399-415c-baf0-db42949d2ba2} {
    // All definitions here belong to the Graph namespace
};
```

### Concept

A **concept** is an abstract term from your data domain. It represents something that
exists only through its instances (keys). Concepts can form hierarchies using `is a`.

```dsm
// From Graph Editor: three independent concepts
concept Graph;
concept Vertex;
concept Edge;
```

Concepts can have inheritance relationships:

```dsm
// From Raptor Editor: Material hierarchy
concept Material;
concept MaterialStandard is a Material;
concept MaterialMirror is a Material;
concept MaterialMatte is a Material;
```

### Key

A **key** identifies a specific instance of a concept. Think of it as a typed UUID:
`key<Vertex>` can only reference a Vertex, not an Edge.

Keys are created at runtime and persist across sessions:

```python
# Python example
vertex_key = Graph_VertexKey.create()
print(vertex_key.instance_id())  # fc472756-8f9e-42aa-a06f-051d330d0108
```

### Document

A **document** is any data expressible in the DSM type system. The most common form is
a structure:

```dsm
struct Login {
    string nickname;
    string password;
};

struct Position {
    float x;
    float y;
};
```

### Attachment

An **attachment** associates a document type with a key type. It defines what data can
be stored for each instance of a concept.

```dsm
// Each User can have a Login document
attachment<User, Login> login;

// Each Vertex can have position data
attachment<Vertex, Vertex2DAttributes> render2DAttributes;
```

## Data Definitions Extracted from Code

DSM extracts data definitions from the programming language. Instead of scattering
struct definitions across C++ headers, DSM captures the data model in a single,
language-independent notation — enabling Kibo to generate infrastructure for
multiple targets from one source of truth.

This means DSM can adapt to an existing codebase: translating C++ data structures
into DSM is a straightforward extraction of what already exists. The
[Raptor Editor sample](samples/raptor_editor.rst) demonstrates this approach, where
an industrial C++ data model was translated directly into DSM.

## The Data Model is a Set of Sealed Definitions

Unlike traditional databases where schemas have versions, DSM takes a different approach:

- Each definition is **sealed by its definition** in a namespace
- The **RuntimeId** is computed deterministically from the definition
- There is **no schema version** - the data model is a set of immutable definitions

This enables schema evolution through adding new attachments rather than migrating
existing data (see [Attachments](attachments.md) for details).

## Example: A Complete Data Model

Here is a complete data model from the Graph Editor, demonstrating the **recommended
pattern** with multiple attachments per concept:

```dsm
namespace Graph {27c49329-a399-415c-baf0-db42949d2ba2} {

// Concepts
concept Graph;
concept Vertex;
concept Edge;

// Documents for Graph
struct GraphTopology {
    set<key<Vertex>> vertexKeys;
    set<key<Edge>> edgeKeys;
};

struct GraphSelection {
    set<key<Vertex>> vertexKeys;
    set<key<Edge>> edgeKeys;
};

struct GraphDescription {
    string name;
    string author;
    string createDate;
};

// Documents for Vertex
struct Position {
    float x;
    float y;
};

struct Color {
    float red;
    float green;
    float blue;
};

struct Vertex2DAttributes {
    Position position;
};

struct VertexVisualAttributes {
    int64 value;
    Color color;
};

// Document for Edge
struct EdgeTopology {
    key<Vertex> vaKey;
    key<Vertex> vbKey;
};

// Graph attachments - each concern is separate
attachment<Graph, GraphTopology> topology;         // Structure
attachment<Graph, GraphSelection> selection;       // UI state
attachment<Graph, GraphDescription> description;   // Metadata
attachment<Graph, map<string, string>> tags;       // User-defined tags
attachment<Graph, xarray<string>> comments;        // Ordered comments

// Vertex attachments - rendering and appearance are separate
attachment<Vertex, Vertex2DAttributes> render2DAttributes;
attachment<Vertex, VertexVisualAttributes> visualAttributes;

// Edge attachment
attachment<Edge, EdgeTopology> topology;

};
```

**Why multiple attachments matter:**

- A Vertex can exist with only position data (no visual attributes)
- Selection state is separate from topology (UI concern vs data concern)
- Adding a new feature (e.g., `physicsAttributes`) requires **no migration**
- Each attachment is independent and optional

This model defines:
- Three concepts (Graph, Vertex, Edge)
- Eight document types (structures for different concerns)
- Eight attachments (five for Graph, two for Vertex, one for Edge)

## What's Next

- [Types and Structures](types.md) - Learn about all available types in DSM
- [Concepts and Hierarchies](concepts.md) - Understand concept inheritance with `is a`
- [Attachments](attachments.md) - Master the recommended patterns for schema design
