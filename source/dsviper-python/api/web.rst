HTML Rendering
==============

Classes for rendering Viper C++ data as HTML in web and desktop applications.

**When to use**: Use ``DocumentNode`` to traverse nested Viper C++ documents with
full metadata. Use ``Html`` to generate styled HTML output for Flask web apps
or Qt desktop apps (via ``QTextEdit.setHtml()``).

Quick Start
-----------

.. code-block:: python

   from flask import Flask, render_template
   from dsviper import CommitDatabase, CommitStateBuilder, DocumentNode, Html, ValueKey

   app = Flask(__name__)

   @app.get("/document/<uuid:instance_id>")
   def document_view(instance_id):
       db = CommitDatabase.open("model.cdb")
       db.definitions().inject()

       # Create key and get document accessor
       key = ValueKey.create(MYAPP_C_Entity, str(instance_id))
       attachment_getting = CommitStateBuilder.state(db, db.last_commit_id()).attachment_getting()

       # Build document tree for all attachments
       nodes = DocumentNode.create_documents(key, attachment_getting)

       # Render as collapsible HTML details
       content = Html.documents_details(nodes, show_type=True)
       return render_template("document.html", content=content)

DocumentNode Tree
-----------------

``DocumentNode`` provides a recursive tree structure for navigating Viper C++ documents:

.. code-block:: python

   from dsviper import DocumentNode

   # Create tree from a key
   nodes = DocumentNode.create_documents(key, attachment_getting)

   for node in nodes:
       print(f"{node.string_component()}: {node.string_value()}")

       # Type introspection for conditional rendering
       if node.is_editable():
           if node.is_boolean():
               render_checkbox(node)
           elif node.is_string():
               render_text_input(node)
           elif node.is_enumeration():
               render_select(node)

       # Recursive traversal
       if node.is_expandable():
           for child in node.children():
               render_node(child)

Custom HTML Rendering
---------------------

Build custom renderers using ``DocumentNode`` metadata:

.. code-block:: python

   from dsviper import DocumentNode, ValueKey, ValueEnumeration

   def render_node(node: DocumentNode, level: int = 0) -> str:
       indent = "  " * level
       html = ""

       if node.is_expandable():
           # Collapsible container
           html += f'{indent}<details open>'
           html += f'<summary>{node.string_component()}</summary>'
           for child in node.children():
               html += render_node(child, level + 1)
           html += f'{indent}</details>'
       else:
           # Leaf value
           html += f'{indent}<div>{node.string_component()} = '

           if node.is_editable():
               # Editable field with form input
               html += f'<input name="{node.uuid().encoded()}" '
               html += f'value="{node.string_value()}"/>'
           else:
               html += node.string_value()

           html += '</div>'

       return html

Node metadata available:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Method
     - Description
   * - ``path()``
     - Path to this node (for ``update()`` mutations)
   * - ``key()``
     - Document key (for identifying the document)
   * - ``attachment()``
     - Attachment containing this document
   * - ``uuid()``
     - Unique ID for this node (useful for HTML element IDs)
   * - ``is_editable()``
     - Whether this field can be modified
   * - ``is_expandable()``
     - Whether this node has children
   * - ``children()``
     - Child nodes for containers/structures

Html Helpers
------------

The ``Html`` class provides ready-to-use rendering:

.. code-block:: python

   from dsviper import Html, DocumentNode

   # Render documents as collapsible details
   nodes = DocumentNode.create_documents(key, attachment_getting)
   content = Html.documents_details(nodes, show_type=True)

   # Render a single value with syntax highlighting
   html = Html.value(my_structure)

   # Pretty-print with indentation
   html = Html.value_pretty(my_structure, show_type=True)

   # Render DSM schema as HTML
   html = Html.dsm_definitions(dsm_defs, show_documentation=True)

   # Build complete HTML document
   page = Html.document(
       title="My Document",
       style=Html.style(),
       body=Html.body(content)
   )

Qt Desktop Integration
----------------------

The same ``Html`` helpers work in Qt/PySide6 applications: build an
``Html.document(...)`` and pass it to ``QTextEdit.setHtml()``. Used by both
``cdbe.py`` and ``dbe.py`` to display definitions and values with syntax
highlighting.

Choosing the Right Approach
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - Use Case
     - API
     - Note
   * - Quick document display
     - ``Html.documents_details()``
     - Ready-to-use collapsible view
   * - Custom form builder
     - ``DocumentNode`` traversal
     - Full control over rendering
   * - Value debugging
     - ``Html.value_pretty()``
     - Syntax-highlighted output
   * - Schema documentation
     - ``Html.dsm_definitions()``
     - Display DSM structure
   * - Qt desktop display
     - ``Html.document()`` + ``setHtml()``
     - Works with QTextEdit

DocumentNode
------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.DocumentNode

Html
----

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Html
