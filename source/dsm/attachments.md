# Attachments

Attachments associate documents (data) with keys (concept instances). They are
the primary mechanism for storing information about your domain entities.

## Basic Attachments

An attachment declares that a concept can have associated data:

```dsm
concept User;

struct Login {
    string nickname;
    string password;
};

attachment<User, Login> login;
```

This creates a mapping: each `User` key can have a `Login` document attached.

## Recommended Pattern: Multiple Attachments

The **recommended design** uses multiple attachments per concept, each representing
a separate concern:

```dsm
// From Graph Editor: Vertex with separate concerns
concept Vertex;

// Rendering concern
struct Vertex2DAttributes {
    Position position;
};
attachment<Vertex, Vertex2DAttributes> render2DAttributes;

// Appearance concern
struct VertexVisualAttributes {
    int64 value;
    Color color;
};
attachment<Vertex, VertexVisualAttributes> visualAttributes;
```

### Graph Editor Example

The Graph Editor demonstrates this pattern with **5 attachments on Graph** and
**2 attachments on Vertex**:

```dsm
namespace Graph {27c49329-a399-415c-baf0-db42949d2ba2} {

concept Graph;
concept Vertex;
concept Edge;

// Graph attachments - each is independent
attachment<Graph, GraphTopology> topology;      // Structure
attachment<Graph, GraphSelection> selection;    // UI state
attachment<Graph, GraphDescription> description; // Metadata
attachment<Graph, map<string, string>> tags;    // User-defined tags
attachment<Graph, xarray<string>> comments;     // Ordered comments

// Vertex attachments - separate concerns
attachment<Vertex, Vertex2DAttributes> render2DAttributes;
attachment<Vertex, VertexVisualAttributes> visualAttributes;

// Edge attachment
attachment<Edge, EdgeTopology> topology;

};
```

### Benefits of Multiple Attachments

| Benefit                    | Explanation                                           |
|----------------------------|-------------------------------------------------------|
| **Independent evolution**  | Add new attachments without migrating existing data   |
| **Optional data**          | A Vertex can exist without visual attributes          |
| **Separation of concerns** | UI state (selection) is separate from data (topology) |
| **Partial loading**        | Load only the attachments you need                    |
| **Clean migrations**       | Old code ignores new attachments                      |

## Single-Attachment Pattern

When translating an existing C++ codebase to DSM, the natural result is a **single
attachment per concept** — mirroring the original C++ structures:

```dsm
// From Raptor Editor: Single attachment per concept (translated from C++)
concept Material;

struct MaterialStandardProperties {
    string name = "MaterialStandard";
    optional<key<Thumbnail>> thumbnailKey;
    MaterialStandardType materialType = .diffuseSpecular;
    Vector diffuseColor;
    Vector ambientColor;
    Vector illuminationColor;
    float diffuseIntensity;
    float illuminationIntensity;
    optional<key<Texture>> diffuseMapKey;
    bool diffuseMapEnabled;
    // ... 50+ more fields ...
};

attachment<MaterialStandard, MaterialStandardProperties> properties;
```

### Problems with Monolithic Structures

| Problem            | Impact                                        |
|--------------------|-----------------------------------------------|
| **All-or-nothing** | Must load entire structure even for one field |
| **Migration pain** | Adding a field requires data migration        |
| **Field bloat**    | Structures grow unwieldy over time            |
| **Tight coupling** | Changes affect all code using the structure   |

## Schema Evolution: Adding Features

### With Multiple Attachments (Recommended)

```dsm
// Original design
attachment<User, Login> login;

// V2: Add email separately - NO MIGRATION NEEDED
struct ContactInfo {
    string email;
    optional<string> phone;
};
attachment<User, ContactInfo> contact;

// V3: Add avatar - NO MIGRATION NEEDED
attachment<User, blob_id> avatar;
```

Existing data is untouched. Old code continues to work.

### With Single Attachment

```dsm
// Original
struct UserProperties {
    string username;
    string password_hash;
};

// V2: Must migrate ALL existing data to add email
struct UserProperties {
    string username;
    string password_hash;
    string email;           // New field - requires migration
    optional<blob_id> avatar;  // New field - requires migration
};
```

## Attachment Types

Attachments can use any DSM type as the document:

```dsm
// Structure
attachment<Graph, GraphTopology> topology;

// Map
attachment<Graph, map<string, string>> tags;

// Collection
attachment<Graph, xarray<string>> comments;

// Simple type
attachment<User, blob_id> avatar;

// Any type (dynamic)
attachment<User, any> metadata;
```

## Optional vs Required

Attachments are always **optional** at the storage level. Your code decides
whether an attachment is logically required:

```python
# Read an attachment
topology = commit.get(a_topology, graph_key)

if topology.is_nil():
    # Handle missing attachment
    topology = GraphTopology()
    mutating.set(a_topology, graph_key, topology)
```

## Real-World Comparison

### Graph Editor (Recommended)

```dsm
// Vertex can have:
// - render2DAttributes only (topology-only vertex)
// - visualAttributes only (invisible vertex with metadata)
// - Both (fully rendered vertex)
// - Neither (just a key reference)

attachment<Vertex, Vertex2DAttributes> render2DAttributes;
attachment<Vertex, VertexVisualAttributes> visualAttributes;
```

### Raptor Editor (Single-Attachment)

```dsm
// Surface MUST have all properties defined
// No way to have a "lightweight" surface

struct SurfaceProperties {
    string name = "Surface";
    map<key<LightingLayer>, key<Texture>> lightmaps;
    key<Mesh> meshKey;
    Vector color = {1.0, 1.0, 1.0};
    set<string> tags;
    SurfaceBillboardMode billboardMode;
    optional<key<MeshAnimation>> meshAnimationKey;
    SurfaceMirrorPlane mirrorPlane;
};

attachment<Surface, SurfaceProperties> properties;
```

## Design Guidelines

### Do

- **Separate concerns**: One attachment per logical domain
- **Use multiple attachments**: They're cheap and enable evolution
- **Name attachments clearly**: `topology`, `selection`, `visual` not `data`, `props`
- **Keep structures focused**: 5-10 fields per structure is ideal

### Don't

- **Create monolithic structures**: Avoid 50+ field `Properties` structures
- **Mix concerns**: Don't put UI state in data structures
- **Use single attachment**: Unless you have a specific reason

### Migration Path

If you inherit a single-attachment design:

1. Keep the existing `properties` attachment
2. Add new features as new attachments
3. Gradually migrate fields to new attachments
4. Deprecate unused fields (don't delete - maintains compatibility)

```dsm
// Existing single-attachment
attachment<Vertex, VertexProperties> properties;

// New features - separate attachments
attachment<Vertex, VertexPhysics> physics;      // New feature
attachment<Vertex, VertexAnnotation> annotation; // New feature
```

## What's Next

- [Function Pools](function_pools.md) - Define operations on your data model
- [Code Generation](code_generation.md) - Generate infrastructure from DSM
