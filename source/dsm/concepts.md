# Concepts and Hierarchies

Concepts are the abstract building blocks of your data model. They represent
entities that exist only through their instances (keys).

## Basic Concepts

A concept declares an abstract entity from your domain:

```dsm
// From Graph Editor: Three independent concepts
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
// From Raptor Editor: Material hierarchy
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

### Light Hierarchy Example

```dsm
// From Raptor Editor: Light types
concept Light;
concept LightSpot is a Light;
concept LightOmni is a Light;
concept LightSun is a Light;
concept LightSky is a Light;
concept LightAreaPlane is a Light;
concept LightAreaCylinder is a Light;
concept LightAreaMesh is a Light;
```

Each light type has its own properties structure:

```dsm
// Base properties (all lights have these)
struct LightProperties {
    string name;
    bool enabled = true;
    Vector color = {1.0, 1.0, 1.0};
    float intensity = 1.0;
    Vector position = {0.0, 0.1, 0.0};
    Vector orientation;
};

// Spot-specific properties
struct LightSpotProperties {
    float diameter = 0.05;
    Vector target = {0.0, 0.0, 1.0};
    float falloff = 45.0;  // Degrees
    float hotSpot = 43.0;  // Degrees
    LightShadow shadow;
    LightAttenuation attenuation;
};

// Area light properties
struct LightAreaPlaneProperties {
    float width = 1.0;   // Meters
    float height = 1.0;  // Meters
    LightShadow shadow;
    LightAttenuation attenuation;
};
```

### Multi-level Hierarchies

Hierarchies can have multiple levels:

```dsm
// From Raptor Editor: Environment generator hierarchy
concept EnvironmentGenerator;
concept EnvironmentGeneratorHdrls is a EnvironmentGenerator;
concept EnvironmentGeneratorLocal is a EnvironmentGenerator;

// From Raptor Editor: Kinematics node hierarchy
concept KinematicsNode;
concept KinematicsNodeAxis is a KinematicsNode;
concept KinematicsNodeNull is a KinematicsNode;
concept KinematicsNodeVector is a KinematicsNode;

// Kinematics constraint hierarchy
concept KinematicsConstraint;
concept KinematicsConstraintCopyOrientation is a KinematicsConstraint;
concept KinematicsConstraintCopyPosition is a KinematicsConstraint;
concept KinematicsConstraintFollowPath is a KinematicsConstraint;
concept KinematicsConstraintLookAt is a KinematicsConstraint;
```

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

At runtime, the generated code provides type-safe conversions between parent and
child keys:

```python
# Generated code from red/data.py

# Parent key can try to convert to a specific child (returns None if not that type)
light_key = Raptor_LightKey.create()
spot_key = light_key.to_raptor_light_spot_key()  # -> Raptor_LightSpotKey | None

# Child key can convert to parent key
spot_key = Raptor_LightSpotKey.create()
parent_key = spot_key.to_parent_key()  # -> Raptor_LightKey

# Parent key can be constructed from any child key
omni_key = Raptor_LightOmniKey.create()
light_key = Raptor_LightKey.from_raptor_light_omni_key(omni_key)  # -> Raptor_LightKey
```

## Clubs: Grouping Unrelated Concepts

Sometimes you need to reference concepts that share no inheritance relationship.
A `club` groups unrelated concepts:

```dsm
// From Raptor Editor: Configuration target sources
// These concepts are unrelated but can all be configuration sources
club ConfigurationTargetSource;
membership ConfigurationTargetSource Model;
membership ConfigurationTargetSource Product;
membership ConfigurationTargetSource Overlay;

// From Raptor Editor: Configuration target elements
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
// From Raptor Editor: Configuration target
struct ConfigurationTarget {
    string name = "ConfigurationTarget";
    bool enabled;
    key<ConfigurationTargetSource> sourceKey;   // Model, Product, or Overlay
    key<ConfigurationTargetElement> elementKey; // Any layer type
};
```

### Kinematics Club Example

```dsm
// From Raptor Editor: Elements that can be animated
club KinematicsElement;
membership KinematicsElement Surface;
membership KinematicsElement BezierPath;
membership KinematicsElement KinematicsNodeAxis;
membership KinematicsElement KinematicsNodeNull;
membership KinematicsElement KinematicsNodeVector;

// Kinematics uses this to track parent-child relationships
struct KinematicsProperties {
    vector<key<KinematicsNode>> nodeKeys;
    map<key<KinematicsElement>, vector<key<KinematicsConstraint>>> constraints;
    map<key<KinematicsElement>, key<KinematicsElement>> parents;
};
```

## Concept vs Club

| Aspect           | Concept Hierarchy                   | Club                                         |
|------------------|-------------------------------------|----------------------------------------------|
| **Relationship** | "is a" (inheritance)                | "member of" (grouping)                       |
| **Use case**     | Related types with shared semantics | Unrelated types with shared usage            |
| **Example**      | `MaterialMirror is a Material`      | `membership ConfigurationTargetSource Model` |
| **Membership**   | Single parent                       | Multiple clubs allowed                       |

A concept can be a member of multiple clubs:

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

## What's Next

- [Attachments](attachments.md) - Associate data with concept instances
- [Function Pools](function_pools.md) - Define operations on your data model
