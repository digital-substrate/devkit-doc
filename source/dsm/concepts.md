# Concepts and Hierarchies

Concepts are the abstract building blocks of your data model. They represent
entities that exist only through their instances (keys).

## Basic Concepts

A concept declares an abstract entity from your domain:

```dsm
// Three independent concepts
concept Graph;
concept Vertex;
concept Edge;
```

These concepts have no concrete implementation—only their keys exist at runtime:

```python
# Python: Creating concept instances
vertex_key = Graph_VertexKey.create()
print(vertex_key.instance_id())  # fc472756-8f9e-42aa-a06f-051d330d0108
```

## Concept Inheritance

Concepts can form hierarchies using `is a`:

```dsm
// Material hierarchy
concept Material;
concept MaterialStandard is a Material;
concept MaterialMultilayer is a Material;
concept MaterialMirror is a Material;
concept MaterialMatte is a Material;
concept MaterialEnvironment is a Material;
concept MaterialSeam is a Material;
concept MaterialAxfCpa2 is a Material;
```

This hierarchy enables **polymorphism**: a `key<Material>` can reference any
material subtype.

## Key Polymorphism

Keys respect the inheritance hierarchy:

```dsm
// A structure that accepts any material
struct MaterialAssignment {
    key<Material> materialKey;  // Can hold any material subtype
    Transform transform;
    int8 uvSet;
};
```

At runtime, the generated code provides type-safe conversions between parent
and child keys (parent→child returns `None` if the instance is not that
subtype; child→parent always succeeds).

## Clubs: Grouping Unrelated Concepts

Sometimes you need to reference concepts that share no inheritance relationship.
A `club` groups unrelated concepts:

```dsm
// Configuration target sources
// These concepts are unrelated but can all be configuration sources
club ConfigurationTargetSource;
membership ConfigurationTargetSource Model;
membership ConfigurationTargetSource Product;
membership ConfigurationTargetSource Overlay;

// Configuration target elements
club ConfigurationTargetElement;
membership ConfigurationTargetElement GeometryLayer;
membership ConfigurationTargetElement AspectLayer;
membership ConfigurationTargetElement PositionLayer;
membership ConfigurationTargetElement EnvironmentLayer;
membership ConfigurationTargetElement LightingLayer;
membership ConfigurationTargetElement LightingLayerColorLayer;
membership ConfigurationTargetElement OverlayLayer;
```

Use club keys to reference any member:

```dsm
// Configuration target
struct ConfigurationTarget {
    string name = "ConfigurationTarget";
    bool enabled;
    key<ConfigurationTargetSource> sourceKey;   // Model, Product, or Overlay
    key<ConfigurationTargetElement> elementKey; // Any layer type
};
```

## Concept vs Club

| Aspect           | Concept Hierarchy                   | Club                                         |
|------------------|-------------------------------------|----------------------------------------------|
| **Relationship** | "is a" (inheritance)                | "member of" (grouping)                       |
| **Use case**     | Related types with shared semantics | Unrelated types with shared usage            |
| **Example**      | `MaterialMirror is a Material`      | `membership ConfigurationTargetSource Model` |
| **Membership**   | Single parent                       | Multiple clubs allowed                       |

A concept can be a member of multiple clubs.

## RuntimeId Generation

Each concept receives a unique **RuntimeId** computed deterministically from its
definition within its namespace. This means:

- The same concept definition always produces the same RuntimeId
- Different namespaces produce different RuntimeIds even for identically-named concepts
- RuntimeIds enable type-safe serialization and persistence

```dsm
namespace Graph {27c49329-a399-415c-baf0-db42949d2ba2} {
concept Vertex;  // RuntimeId computed from namespace UUID + "Vertex"
};

namespace Other {12345678-1234-1234-1234-123456789abc} {
concept Vertex;  // Different RuntimeId (different namespace)
};
```

