Graph Editor
============

.. rubric:: Files: 5 | Namespace: Graph | Pattern: Recommended (multiple attachments, function pools)

Graph topology editor demonstrating best practices.

----

Graph.dsm
---------

**Domain:** Graph, Vertex, Edge

This file defines the core data model for a graph editor application. It demonstrates the
**recommended DSM pattern** with multiple attachments per concept, separating concerns
cleanly.

Data Model Design
^^^^^^^^^^^^^^^^^

- **Three concepts** (Graph, Vertex, Edge) represent the topological entities
- **Attachments separate concerns**: topology (structure), selection (UI state),
  description (metadata), render2DAttributes (visualization), visualAttributes (appearance)
- **Key insight**: A Vertex can exist without render attributes (topology-only) or without
  visual attributes (invisible vertex). Each attachment is optional and independent.

Why Multiple Attachments Matter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``topology`` attachment stores which vertices/edges exist in the graph
- ``selection`` attachment tracks UI selection state separately from topology
- ``visualAttributes`` and ``render2DAttributes`` handle rendering independently
- Adding a new concern (e.g., ``physicsAttributes``) requires zero migration - just add a
  new attachment

This is the **anti-monolithic pattern**: instead of one giant ``VertexProperties`` struct,
each concern lives in its own attachment.

.. code-block:: dsm

   // Types definitions
   namespace Graph {27c49329-a399-415c-baf0-db42949d2ba2} {

   """A graph."""
   concept Graph;

   """A vertex in a graph."""
   concept Vertex;

   """An edge in a graph."""
   concept Edge;

   """The selected vertices and edges."""
   struct GraphSelection {
       set<key<Vertex>> vertexKeys;
       set<key<Edge>> edgeKeys;
   };

   """An edge in the graph topology."""
   struct EdgeTopology {
       key<Vertex> vaKey;
       key<Vertex> vbKey;
   };

   """The vertices and edges of the graph topology."""
   struct GraphTopology {
       set<key<Vertex>> vertexKeys;
       set<key<Edge>> edgeKeys;
   };

   """A Rectangle."""
   struct Rectangle {
       """the x origin."""
       float x;
       """the y origin."""
       float y;
       """the width."""
       float w;
       """the height."""
       float h;
   };

   """The descriptive information."""
   struct GraphDescription {
       string name;
       string author;
       string createDate;
   };

   """A Position."""
   struct Position {
       float x;
       float y;
   };

   """The attributes used to render a topological vertex in 2D."""
   struct Vertex2DAttributes {
       Position position;
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
       Color color;
   };

   };

   // Attachments definitions
   namespace Graph {27c49329-a399-415c-baf0-db42949d2ba2} {
   """The topology of a graph."""
   attachment<Graph, GraphTopology> topology;

   """A collection of tags for a graph."""
   attachment<Graph, map<string, string>> tags;

   """A collection of comments for a Graph."""
   attachment<Graph, xarray<string>> comments;

   """The selected vertices of a graph."""
   attachment<Graph, GraphSelection> selection;

   """The descriptive information of a graph."""
   attachment<Graph, GraphDescription> description;

   """The render attributes used to render a vertex of a graph in 2D."""
   attachment<Vertex, Vertex2DAttributes> render2DAttributes;

   """The visual attributes used to render a vertex of a graph."""
   attachment<Vertex, VertexVisualAttributes> visualAttributes;

   """An Edge in the graph topology."""
   attachment<Edge, EdgeTopology> topology;

   };

----

Pool_ModelGraph.dsm
-------------------

**Domain:** Pool: ModelGraph

This is an **attachment_function_pool** - functions that declare an intent to mutate state.

Function Categories
^^^^^^^^^^^^^^^^^^^

- **Topology operations**: ``newVertex``, ``newEdge``, ``clearGraph`` - basic graph manipulation
- **Property setters**: ``setVertexColor``, ``setVertexPosition``, ``setVertexValue`` - modify
  vertex attachments
- **Batch operations**: ``moveVertices``, ``randomGraph`` - operate on multiple elements
- **Metadata**: ``setGraphLabel``, ``setGraphTag``, ``appendGraphComment`` - graph-level
  annotations
- **XArray operations**: ``insertGraphComment``, ``removeGraphComment``,
  ``updateGraphComment`` - demonstrate ordered collection with UUID-based positions (not
  indices)

Testing/Demo Functions
^^^^^^^^^^^^^^^^^^^^^^

These functions are intentionally broken for demonstrations:

- ``graphWithError`` - throws during commit to test error handling
- ``graphWithMissingVertex`` - creates dangling edge references
- ``deleteSelectionBugged`` - deletes vertices without cleaning edges
- ``killer`` - stress test that creates many mutations

.. note::

   All ``mutable`` functions declare an intent to modify state.
   Non-mutable functions (queries) declare read-only access.

.. code-block:: dsm

   """This pool provides access to functions used to edit the graph topology."""
   attachment_function_pool ModelGraph {9bdcbb5b-76e9-426f-b8a6-a10ed2d949e6} {

   """Append a new comment."""
   mutable void appendGraphComment(key<Graph> graphKey, string comment);

   """Clear the graph."""
   mutable void clearGraph(key<Graph> graphKey);

   """Delete a vertex without deleting connected edges."""
   mutable void deleteSelectionBugged(key<Graph> graphKey);

   """Throw an error while creating a graph."""
   mutable void graphWithError(key<Graph> graphKey);

   """Create a graph with missing vertices to illustrate graph integrity."""
   mutable void graphWithMissingVertex(key<Graph> graphKey);

   """Create a graph with missing vertex property to illustrate graph integrity."""
   mutable void graphWithMissingVertexProperties(key<Graph> graphKey);

   """Insert a new comment at a specific xarray position (not an index)."""
   mutable void insertGraphComment(key<Graph> graphKey, uuid position, string comment);

   """Create mutations that destroy the usability of the Commit."""
   mutable void killer(key<Graph> graphKey, uint64 vertexCount);

   """Move the vertices by the offset."""
   mutable void moveVertices(set<key<Vertex>> vertexKeys, Position offset);

   """Create a new edge."""
   mutable key<Edge> newEdge(key<Graph> graphKey, key<Vertex> vaKey, key<Vertex> vbKey);

   """Create a vertex with the specified attributes."""
   mutable key<Vertex> newVertex(key<Graph> graphKey, int64 value, Position position);

   """Append a random comment."""
   mutable void randomComment(key<Graph> graphKey);

   """Create a random edge or raise if the graph is complete."""
   mutable key<Edge> randomEdge(key<Graph> graphKey);

   """Create a new random graph in rect."""
   mutable void randomGraph(key<Graph> graphKey, uint64 vertexCount, uint64 edgeCount, Rectangle rect);

   """Insert a new random tag."""
   mutable void randomTag(key<Graph> graphKey);

   """Create a random vertex."""
   mutable key<Vertex> randomVertex(key<Graph> graphKey, Rectangle rect);

   """Remove a comment at a specific xarray position (not an index)."""
   mutable void removeGraphComment(key<Graph> graphKey, uuid position);

   """Set the label of the graph description."""
   mutable void setGraphLabel(key<Graph> graphKey, string label);

   """Replace or insert the tag."""
   mutable void setGraphTag(key<Graph> graphKey, string key, string value);

   """Set the vertex color."""
   mutable void setVertexColor(key<Vertex> vertexKey, Color color);

   """Set the vertex position."""
   mutable void setVertexPosition(key<Vertex> vertexKey, Position position);

   """Set the vertex value."""
   mutable void setVertexValue(key<Vertex> vertexKey, int64 value);

   """Remove the tag."""
   mutable void unsetGraphTags(key<Graph> graphKey, set<string> keys);

   """Update the comment at a specific xarray position (not an index)."""
   mutable void updateGraphComment(key<Graph> graphKey, uuid position, string comment);

   """Update a tag."""
   mutable void updateGraphTag(key<Graph> graphKey, string key, string value);

   """Test no args."""
   mutable void noArgs();

   };

----

Pool_ModelIntegrity.dsm
-----------------------

**Domain:** Pool: ModelIntegrity

This pool demonstrates **referential integrity repair** - what happens when the graph has
dangling references (edges pointing to deleted vertices).

Three Repair Strategies
^^^^^^^^^^^^^^^^^^^^^^^

- ``restoreIntegrityByCreating`` - recreate missing vertices (preserve topology)
- ``restoreIntegrityByDeleting`` - remove edges with dangling references (preserve
  consistency)
- ``restoreIntegrityByRestoring`` - respawn deleted elements from history

Why This Matters
^^^^^^^^^^^^^^^^

DSM concepts are identified by keys. If a ``delete`` function neglects
to update references that point to a deleted entity, those references
become "orphaned" — a defect of that specific function, not a property
of the engine. This pool demonstrates how a sample application detects
and repairs such inconsistencies when one of its own functions is
deliberately incomplete.

**Use case**: ``deleteSelectionBugged`` in ModelGraph is a deliberately
incomplete delete kept in the sample for teaching purposes — it leaves
orphans. The ModelIntegrity pool shows three repair strategies for that
specific situation.

.. code-block:: dsm

   """This pool provides access functions used to restore the integrity of the graph."""
   attachment_function_pool ModelIntegrity {95e0f859-65e0-419e-8b81-77547c73b759} {

   """Restore the graph integrity by creating missing elements."""
   mutable void restoreIntegrityByCreating(key<Graph> graphKey);

   """Restore the graph integrity by removing elements."""
   mutable void restoreIntegrityByDeleting(key<Graph> graphKey);

   """Restore the graph integrity by respawning elements."""
   mutable void restoreIntegrityByRestoring(key<Graph> graphKey);

   """Restore attributes of the selected vertices."""
   mutable void restoreVertexSelection(key<Graph> graphKey);

   };

----

Pool_ModelSelection.dsm
-----------------------

**Domain:** Pool: ModelSelection

This pool manages **UI selection state** - which vertices and edges are currently selected
by the user. Selection is stored in the ``Graph.selection`` attachment, separate from
topology.

Selection Operations
^^^^^^^^^^^^^^^^^^^^

- **Set operations**: ``selectAll``, ``deselectAll``, ``invertSelection`` - bulk selection
  changes
- **Element-specific**: ``setSelectionToVertex``, ``setSelectionToEdge`` - single element
  selection
- **Combine mode**: ``combineSelectionWithVertex/Edge`` - add/remove from current
  selection (shift-click behavior)
- **Queries**: ``selectedVertices``, ``selectedEdges`` - return current selection (non-mutable)

.. note::

   ``deleteSelection`` operates on selection then modifies topology -
   demonstrating how UI state drives data mutations.

.. code-block:: dsm

   """This pool provides access to functions used to edit the selection."""
   attachment_function_pool ModelSelection {5318ad8d-79d8-498e-b080-eccf15e4a74d} {

   """Combine the edge-selected state with the edge selection."""
   mutable void combineSelectionWithEdge(key<Graph> graphKey, key<Edge> edgeKey, bool selected);

   """Combine the vertex-selected state with the vertex selection."""
   mutable void combineSelectionWithVertex(key<Graph> graphKey, key<Vertex> vertexKey, bool selected);

   """Delete the selected elements."""
   mutable void deleteSelection(key<Graph> graphKey);

   """Deselect all edges and vertices."""
   mutable void deselectAll(key<Graph> graphKey);

   """Deselect all edges."""
   mutable void deselectAllEdges(key<Graph> graphKey);

   """Deselect all vertices."""
   mutable void deselectAllVertices(key<Graph> graphKey);

   """Increment the value of selected vertices."""
   mutable void incrementVertexValue(key<Graph> graphKey, int64 value);

   """Invert the edge selection."""
   mutable void invertEdgesSelection(key<Graph> graphKey);

   """Invert the selection for edges and vertices."""
   mutable void invertSelection(key<Graph> graphKey);

   """Invert the vertex selection."""
   mutable void invertVerticesSelection(key<Graph> graphKey);

   """Select all edges and vertices."""
   mutable void selectAll(key<Graph> graphKey);

   """Select all edges."""
   mutable void selectAllEdges(key<Graph> graphKey);

   """Select all vertices."""
   mutable void selectAllVertices(key<Graph> graphKey);

   """Return selected edges."""
   set<key<Edge>> selectedEdges(key<Graph> graphKey);

   """Return selected vertices."""
   set<key<Vertex>> selectedVertices(key<Graph> graphKey);

   """Reduce the selection to the specified edges and vertices."""
   mutable void setSelection(key<Graph> graphKey, set<key<Vertex>> vertexKeys, set<key<Edge>> edgeKeys);

   """Reduce the edge selection to the edge."""
   mutable void setSelectionToEdge(key<Graph> graphKey, key<Edge> edgeKey);

   """Reduce the selection to the vertex."""
   mutable void setSelectionToVertex(key<Graph> graphKey, key<Vertex> vertexKey);

   };

----

Pool_Tools.dsm
--------------

**Domain:** Pool: Tools

This is a **function_pool** (not attachment_function_pool) - pure utility

Difference from attachment_function_pool
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``function_pool``: Pure functions
- ``attachment_function_pool``: Functions that declare an intent to mutate state

Utility Functions
^^^^^^^^^^^^^^^^^

- ``add``, ``isEven``, ``isGreater`` - basic arithmetic/comparison (demonstration purposes)
- ``randomWord`` - generate random strings for testing

**Use case**: These functions are stateless and available in RPC context for client-side
computations or test data generation (no mutation context required).

.. code-block:: dsm

   """This pool provides access to the various utility functions."""
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
