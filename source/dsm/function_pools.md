# Function Pools

Function pools define operations on your data model. They expose business logic as
callable functions accessible from C++, Python, or RPC.

## Two Types of Function Pools

DSM provides two function pool types:

| Type                       | Purpose                |
|----------------------------|------------------------|
| `function_pool`            | Pure utility functions |
| `attachment_function_pool` | Stateful mutations     |

## Function Pool (Pure Functions)

A `function_pool` contains stateless functions.

```dsm
// From Graph Editor: Pure utility functions
function_pool Tools {dc9740c9-9d1d-4c1e-9caa-4c8843b91e82} {

"""Return a + b."""
int64 add(int64 a, int64 b);

"""Return true if a is even."""
bool isEven(int64 a);

"""Return true if a > b."""
bool isGreater(any a, any b);

"""Return a random word."""
string randomWord(uint64 size);

};
```

Use cases:

- Mathematical computations
- String formatting
- Random data generation for testing
- Validation logic

## Attachment Function Pool

An `attachment_function_pool` contains functions that mutate attachment state.

```dsm
// From Graph Editor: Graph editing operations
attachment_function_pool ModelGraph {9bdcbb5b-76e9-426f-b8a6-a10ed2d949e6} {

"""Create a vertex with the specified attributes."""
mutable key<Vertex> newVertex(key<Graph> graphKey, int64 value, Position position);

"""Create a new edge."""
mutable key<Edge> newEdge(key<Graph> graphKey, key<Vertex> vaKey, key<Vertex> vbKey);

"""Set the vertex color."""
mutable void setVertexColor(key<Vertex> vertexKey, Color color);

"""Set the vertex position."""
mutable void setVertexPosition(key<Vertex> vertexKey, Position position);

"""Clear the graph."""
mutable void clearGraph(key<Graph> graphKey);

};
```

### The `mutable` Keyword

Functions that modify the state are marked `mutable`:

```dsm
// Mutable: declares an intent to modify state
mutable key<Vertex> newVertex(key<Graph> graphKey, int64 value, Position position);

// Non-mutable: declares read-only access
set<key<Vertex>> selectedVertices(key<Graph> graphKey);
```

## Graph Editor Pool Examples

### Selection Pool

Manages UI selection state separately from topology:

```dsm
// From Graph Editor: Selection management
attachment_function_pool ModelSelection {5318ad8d-79d8-498e-b080-eccf15e4a74d} {

"""Select all edges and vertices."""
mutable void selectAll(key<Graph> graphKey);

"""Deselect all edges and vertices."""
mutable void deselectAll(key<Graph> graphKey);

"""Invert the selection for edges and vertices."""
mutable void invertSelection(key<Graph> graphKey);

"""Reduce the selection to the vertex."""
mutable void setSelectionToVertex(key<Graph> graphKey, key<Vertex> vertexKey);

"""Combine the vertex-selected state with the vertex selection."""
mutable void combineSelectionWithVertex(key<Graph> graphKey, key<Vertex> vertexKey, bool selected);

"""Delete the selected elements."""
mutable void deleteSelection(key<Graph> graphKey);

"""Return selected vertices."""
set<key<Vertex>> selectedVertices(key<Graph> graphKey);

"""Return selected edges."""
set<key<Edge>> selectedEdges(key<Graph> graphKey);

};
```

## Raptor Editor Pool Example

### Material Assignment Pool

A focused pool for a single operation:

```dsm
// From Raptor Editor: Material assignment to surfaces
attachment_function_pool ModelSurface {fd61d936-d350-4a18-a2ca-cc7d7d3a9dc6} {

"""Assign a material to a surface."""
mutable void assign_material(
    key<AspectLayer> layerKey,
    key<Surface> surfaceKey,
    key<Material> materialKey
);

};
```

## Function Documentation

Use triple-quoted strings for function documentation:

```dsm
attachment_function_pool ModelGraph {9bdcbb5b-76e9-426f-b8a6-a10ed2d949e6} {

"""
Create a vertex with the specified attributes.

The vertex is added to the graph topology and receives
the specified position and value.

Returns the key of the newly created vertex.
"""
mutable key<Vertex> newVertex(key<Graph> graphKey, int64 value, Position position);

};
```

## Parameter Types

Functions can use any DSM type as parameters or return values:

```dsm
attachment_function_pool Example {9bdcbb5b-76e9-426f-b8a6-a10ed2d949e7} {

// Keys as parameters
mutable void linkItems(key<Item> a, key<Item> b);

// Structures as parameters
mutable void setTransform(key<Object> obj, Transform t);

// Collections as parameters
mutable void moveVertices(set<key<Vertex>> vertices, Position offset);

// Collections as return values
set<key<Vertex>> findConnected(key<Vertex> start);

// Optional return values
optional<key<Vertex>> findByName(key<Graph> graph, string name);

};
```

## XArray Operations

XArray uses UUID positions instead of indices, so concurrent insertions and removals never collide:

```dsm
// From Graph Editor: XArray comment operations
attachment_function_pool ModelGraph {9bdcbb5b-76e9-426f-b8a6-a10ed2d949e6} {

"""Append a new comment."""
mutable void appendGraphComment(key<Graph> graphKey, string comment);

"""Insert a new comment at a specific xarray position (not an index)."""
mutable void insertGraphComment(key<Graph> graphKey, uuid position, string comment);

"""Remove a comment at a specific xarray position (not an index)."""
mutable void removeGraphComment(key<Graph> graphKey, uuid position);

"""Update the comment at a specific xarray position (not an index)."""
mutable void updateGraphComment(key<Graph> graphKey, uuid position, string comment);

};
```

## Pool Namespacing

Each pool has a UUID that identifies it uniquely:

```dsm
attachment_function_pool ModelGraph {9bdcbb5b-76e9-426f-b8a6-a10ed2d949e6} { ... };
function_pool             Tools      {dc9740c9-9d1d-4c1e-9caa-4c8843b91e82} { ... };
```

## Design Guidelines

### Organize by Domain

Group related functions into pools by concern:

- `ModelGraph`: Operations on graph topology
- `ModelSelection`: UI selection state management
- `ModelIntegrity`: Validation and repair operations
- `Tools`: Pure utility functions

### Keep Functions Focused

Each function should do one thing:

```dsm
// Good: Focused functions
mutable void setVertexColor(key<Vertex> vertexKey, Color color);
mutable void setVertexPosition(key<Vertex> vertexKey, Position position);

// Avoid: Multi-purpose functions
mutable void updateVertex(key<Vertex> vertexKey, optional<Color> color,
optional<Position> position, optional<int64> value);
```

### Use Queries for Read-Only Operations

Non-mutable functions are plain queries against current state:

```dsm
// Query: returns a snapshot, no state change
set<key<Vertex>> selectedVertices(key<Graph> graphKey);

// Mutation: declares an intent to modify state
mutable void selectAll(key<Graph> graphKey);
```

