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

DSM captures the data model in a single, language-independent notation — Kibo
then generates infrastructure for multiple targets from it. The
[Raptor Editor sample](samples/raptor_editor.rst) shows the approach applied
to an industrial C++ codebase.

## The Data Model is a Set of Sealed Definitions

Unlike traditional databases where schemas have versions, DSM takes a different approach:

- Each definition is **sealed by its definition** in a namespace
- The **RuntimeId** is computed deterministically from the definition
- There is **no schema version** - the data model is a set of immutable definitions

This enables schema evolution through adding new attachments rather than migrating
existing data (see [Attachments](attachments.md) for details).

## A Complete Data Model

For a complete model that exercises these notions, see the Graph Editor
example in [Attachments](attachments.md#graph-editor-example).
