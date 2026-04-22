DSM Samples
===========

This section presents two real-world applications that demonstrate DSM modeling
patterns at different scales and design philosophies.

.. list-table::
   :header-rows: 1
   :widths: 20 25 55

   * - Application
     - Pattern
     - Description
   * - :doc:`graph_editor`
     - **Recommended** (multi-attachment)
     - Graph topology editor with 5 DSM files. Demonstrates best practices
       with multiple attachments per concept, separating concerns cleanly.
   * - :doc:`raptor_editor`
     - Single-attachment (translated from C++)
     - Professional 3D visualization with 20 DSM files. Production-scale
       example showing materials, lighting, cameras, and animation.

Pattern Comparison
------------------

**Recommended Pattern (Graph Editor)**

Each concept uses multiple attachments to separate concerns:

.. code-block:: dsm

   // Topology is separate from selection, which is separate from rendering
   attachment<Graph, GraphTopology> topology;
   attachment<Graph, GraphSelection> selection;
   attachment<Vertex, Vertex2DAttributes> render2DAttributes;
   attachment<Vertex, VertexVisualAttributes> visualAttributes;

Benefits:

- Adding a new concern (e.g., ``physicsAttributes``) requires zero migration
- Each attachment is optional and independent
- A Vertex can exist without render attributes (topology-only)

**Single-Attachment Pattern (Raptor Editor)**

Each concept has a single monolithic ``properties`` attachment:

.. code-block:: dsm

   attachment<Camera, CameraProperties> properties;
   attachment<Material, MaterialProperties> properties;

Trade-offs:

- Simpler initial design
- Harder to evolve: adding optional features requires struct changes
- All properties bundled together even when some are unused

.. note::

   New projects should follow the **recommended pattern**. The single-attachment
   pattern is documented here because it demonstrates how DSM can adapt to an
   existing C++ codebase.

.. toctree::
   :maxdepth: 2

   graph_editor
   raptor_editor
