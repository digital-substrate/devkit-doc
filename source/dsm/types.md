# Types and Structures

DSM provides a rich type system for modeling data. This chapter covers all available
types, from primitives to complex generic containers.

## Primitive Types

### Boolean

The `bool` type represents true/false values.

```dsm
struct CameraDepthOfField {
    bool enabled;
    float aperture;
    int32 sampleCount = 32;
};
```

### Integers

DSM supports both signed and unsigned integers of various sizes:

| Type     | Range                   | C++ Mapping     |
|----------|-------------------------|-----------------|
| `uint8`  | 0 to 255                | `std::uint8_t`  |
| `uint16` | 0 to 65,535             | `std::uint16_t` |
| `uint32` | 0 to 4 billion          | `std::uint32_t` |
| `uint64` | 0 to 18 quintillion     | `std::uint64_t` |
| `int8`   | -128 to 127             | `std::int8_t`   |
| `int16`  | -32,768 to 32,767       | `std::int16_t`  |
| `int32`  | -2 billion to 2 billion | `std::int32_t`  |
| `int64`  | ±9 quintillion          | `std::int64_t`  |

```dsm
// From Raptor Editor: Iray rendering settings
struct IraySettingsProperties {
    uint32 maxSamples = 512;
    uint32 maxPathLength = 12;
    float maxRenderTime = 3600.0;  // In seconds
};
```

### Real Numbers

The `float` and `double` types represent floating-point numbers.

```dsm
// From Raptor Editor: Camera optical properties
struct CameraOpticalProperties {
    float fov = 0.785398;  // Field of view in radians
    CameraDepthOfField depthOfField;
    CameraMotionBlur motionBlur;
};
```

### String

The `string` type stores UTF-8 encoded text.

```dsm
struct Login {
    string nickname;
    string password;
};
```

### UUID

The `uuid` type stores universally unique identifiers (UUID4).

```dsm
struct S {
    uuid identifier;
    uuid reference = {8f2586fc-735b-48ca-8d32-3b7545f65cd6};
};
```

### Blob and BlobId

DSM provides two types for binary data:

- `blob`: Inline binary data (for small payloads like thumbnails)
- `blob_id`: Reference to external binary data (for large payloads like textures)

```dsm
// From Raptor Editor: Mesh geometry data
struct MeshProperties {
    Aabb aabb;
    int32 triangleCount;
    int32 vertexCount;
    blob_id blob_indices;
    blob_id blob_positions;
    blob_id blob_normals;
    blob_id blob_tangents;
};

// Small data inline, large data by reference
struct Image {
    uint16 width;
    uint16 height;
    blob thumbnail;     // Small: 32x32 preview
    blob_id pixels;     // Large: full resolution
};
```

## Enumerations

The `enum` type defines a fixed set of named values. Enumerations are limited to
256 cases.

```dsm
// From Raptor Editor: Material types
enum MaterialStandardType {
    diffuse,
    diffuseSpecular,
    transparent
};

// From Raptor Editor: Light attenuation models
enum LightAttenuationType {
    none,
    linearSlow,
    linearFast,
    quadraticSlow,
    quadraticFast,
    physical
};
```

Use the dot prefix to reference enum values in field initializers:

```dsm
struct MaterialStandardProperties {
    string name = "MaterialStandard";
    MaterialStandardType materialType = .diffuseSpecular;
    // ...
};
```

## Structures

Structures aggregate fields into composite types. Fields can have default values.

```dsm
// From Raptor Editor: Basic 3D vector
struct Vector {
    float x;
    float y;
    float z;
};

// From Raptor Editor: Axis-aligned bounding box
struct Aabb {
    Vector min;
    Vector max;
};

// From Raptor Editor: 3D transformation
struct Transform {
    Vector translation;
    Vector orientation;
    Vector scaling = {1.0, 1.0, 1.0};  // Default: no scaling
};
```

Structures can be nested but **cannot be recursive**. For recursive relationships,
use `optional<key<T>>`:

```dsm
// From Raptor Editor: Configuration expression tree
struct ConfigurationExpressionProperties {
    ConfigurationExpressionOperationType operationType = .defined;
    optional<key<ConfigurationExpression>> leftExpressionKey;   // Recursive via key
    optional<key<ConfigurationExpression>> rightExpressionKey;  // Recursive via key
    string symbol;
};
```

## Mathematical Types

### Vec

The `vec<T, n>` type creates fixed-size numeric arrays, useful for graphics:

```dsm
struct Mesh {
    vector<vec<float, 3>> positions;  // XYZ coordinates
    vector<vec<float, 2>> uvs;        // UV texture coordinates
};
```

### Mat

The `mat<T, columns, rows>` type creates matrices:

```dsm
struct S {
    mat<float, 4, 4> transform;  // 4x4 transformation matrix
};
```

## Generic Types

### Vector

The `vector<T>` type is a dynamic array.

```dsm
// From Raptor Editor: Camera groups contain cameras
struct CameraGroupProperties {
    string name = "Camera Group";
    vector<key<CameraGroup>> groupKeys;  // Child groups
    vector<key<Camera>> cameraKeys;      // Cameras in this group
};

// From Raptor Editor: Bezier path with control points
struct BezierPathProperties {
    string name = "BezierPath";
    Vector color = {1.0, 1.0, 1.0};
    vector<BezierPathVertex> vertices;
};
```

### Set

The `set<T>` type is an ordered collection of unique values.

```dsm
// From Raptor Editor: Surface tags for filtering
struct SurfaceProperties {
    string name = "Surface";
    set<string> tags;
    // ...
};

// From Raptor Editor: Configuration defines
struct ProductProperties {
    // ...
    set<string> configurationDefines;
    map<string, set<string>> configurationBookmarks;
};
```

### Map

The `map<K, V>` type associates keys with values.

```dsm
// From Raptor Editor: Material assignments per surface
struct AspectLayerProperties {
    string name = "AspectLayer";
    bool enabled;
    map<key<Surface>, MaterialAssignment> materialAssignments;
    map<key<Surface>, vector<LabelAssignment>> labelAssignments;
};

// From Raptor Editor: Environment assignments
struct EnvironmentLayerProperties {
    string name = "EnvironmentLayer";
    bool enabled = true;
    map<key<Surface>, key<Environment>> environmentAssignments;
    map<key<Surface>, Transform> orientationAssignments;
};
```

### Optional

The `optional<T>` type represents a value that may or may not be present.

```dsm
// From Raptor Editor: Optional references
struct CameraProperties {
    string name = "Camera";
    PointOfView pointOfView;
    CameraOpticalProperties opticalProperties;
    optional<key<Sensor>> sensorKey;  // May not have a sensor
};

struct MaterialStandardProperties {
    // ...
    optional<key<Texture>> diffuseMapKey;
    optional<key<BumpMap>> bumpMapKey;
    // ...
};
```

### Tuple

The `tuple<T0, ...>` type groups heterogeneous values.

```dsm
struct S {
    tuple<float, float> location;
    tuple<string, int32, bool> metadata;
};
```

### Variant

The `variant<T0, ...>` type holds one of several possible types.

```dsm
// Multi-layer material with different layer types
struct MaterialMultilayer {
    vector<variant<LayerIllumination, LayerDiffuse, LayerSpecular>> layers;
};
```

### XArray

The `xarray<T>` type is like a vector but preserves element order during
concurrent mutations. Designed for multiplayer editing scenarios.

```dsm
struct Document {
    xarray<string> comments;  // Order preserved across concurrent edits
};
```

## Special Types

### Key

The `key<T>` type references an instance of a concept. It acts like a strongly-typed
UUID:

```dsm
// From Raptor Editor: Model references various concepts
struct ModelProperties {
    string name = "Model";
    vector<key<LightingLayer>> lightingLayerKeys;
    key<GeometryLayer> rootGeometryLayerKey;
    key<Kinematics> kinematicsKey;
    vector<key<PositionLayer>> positionLayerKeys;
};
```

Keys enable:
- **Type safety**: `key<Vertex>` cannot accidentally reference an `Edge`
- **Polymorphism**: `key<Material>` can reference any material subtype

### Any

The `any` type holds any value, requiring runtime type checking:

```dsm
// Store arbitrary documents for a user
attachment<User, any> documents;
```

Use `any` sparingly—prefer strongly-typed alternatives when possible.

## Default Values

Fields can specify default values. If not specified, fields are initialized
to the type's "zero":

| Type              | Zero Value          |
|-------------------|---------------------|
| `bool`            | `false`             |
| integers          | `0`                 |
| `float`, `double` | `0.0`               |
| `string`          | `""` (empty string) |
| `uuid`            | nil UUID            |
| containers        | empty               |
| `optional`        | empty (nil)         |
| struct            | all fields at zero  |

```dsm
// From Raptor Editor: Transform with sensible defaults
struct Transform {
    Vector translation;              // {0, 0, 0}
    Vector orientation;              // {0, 0, 0}
    Vector scaling = {1.0, 1.0, 1.0}; // Identity scale
};

// From Raptor Editor: Camera view defaults
struct PointOfView {
    Vector target;                    // {0, 0, 0}
    Vector eye = {2.0, 2.0, 2.0};    // Offset from origin
    Vector up = {0.0, 1.0, 0.0};     // Y-up convention
};
```

## What's Next

- [Concepts and Hierarchies](concepts.md) - Learn about concept inheritance
- [Attachments](attachments.md) - Associate documents with keys
