DSM & Definitions
=================

DSM classes provide parsing and introspection of Digital Substrate Model files.

**When to use**: Use ``DSMBuilder`` to parse ``.dsm`` files and introspect
the resulting definitions (structures, enumerations, attachments, functions).

Quick Start
-----------

.. code-block:: python

   from dsviper import DSMBuilder

   # Parse DSM file
   builder = DSMBuilder.assemble("model.dsm")
   report, dsm_defs, defs = builder.parse()

   # Check for parse errors
   if report.has_error():
       for err in report.errors():
           print(f"Line {err.line()}: {err.message()}")
       raise RuntimeError("DSM parse failed")

   # Introspect structures
   for struct in dsm_defs.structures():
       print(f"Struct: {struct.type_name()}")
       for field in struct.fields():
           print(f"  {field.name()}: {field.type_reference()}")

   # Introspect attachments
   for att in dsm_defs.attachments():
       print(f"Attachment: {att.type_name()}")
       print(f"  Key: {att.key_type()}, Doc: {att.document_type()}")

   # Inject constants for runtime use
   defs.inject()  # Creates MYAPP_A_*, MYAPP_S_*, etc.

Parsing
-------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.DSMBuilder
   dsviper.DSMBuilderPart
   dsviper.DSMDefinitions
   dsviper.DSMDefinitionsInspector
   dsviper.DSMParseReport
   dsviper.DSMParseError

Model Elements
--------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.DSMConcept
   dsviper.DSMClub
   dsviper.DSMStructure
   dsviper.DSMStructureField
   dsviper.DSMEnumeration
   dsviper.DSMEnumerationCase
   dsviper.DSMAttachment

DSM Types
---------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.DSMTypeKey
   dsviper.DSMTypeVector
   dsviper.DSMTypeSet
   dsviper.DSMTypeMap
   dsviper.DSMTypeXArray
   dsviper.DSMTypeOptional
   dsviper.DSMTypeTuple
   dsviper.DSMTypeVec
   dsviper.DSMTypeMat
   dsviper.DSMTypeVariant
   dsviper.DSMTypeReference

Functions
---------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.DSMFunction
   dsviper.DSMFunctionPool
   dsviper.DSMFunctionPrototype
   dsviper.DSMAttachmentFunction
   dsviper.DSMAttachmentFunctionPool

Literals
--------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.DSMLiteralValue
   dsviper.DSMLiteralList

Definitions
-----------

``Definitions`` is the registry a DSM model is loaded into: the concepts, clubs,
attachments and types an application declares. Everything else on this page
describes the model; these classes hold it at runtime.

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Definitions
   dsviper.DefinitionsConst
   dsviper.DefinitionsCollector
   dsviper.DefinitionsInspector
   dsviper.DefinitionsExtendInfo

Source Map
----------

Pass a ``DSMSourceMap`` to ``DSMBuilder.parse(source_map=…)`` and the parser
records, as a by-product, the exact source span of every declaration, field,
case, namespace, type sub-expression and *resolved* type-reference. This is what
makes a span-precise codemod possible: patch a hand-authored ``.dsm`` in place
under a transformation — file split, comments and ordering preserved — instead
of regenerating it. Opt-in; a ``parse`` without a source map is unchanged.

.. code-block:: python

   from dsviper import DSMBuilder, DSMSourceMap

   source_map = DSMSourceMap()
   report, dsm_defs, defs = DSMBuilder.assemble("model.dsm").parse(source_map=source_map)

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.DSMSourceMap
   dsviper.DSMSourceSpan
   dsviper.DSMSourceDeclaration
   dsviper.DSMSourceField
   dsviper.DSMSourceCase
   dsviper.DSMSourceNameSpace
   dsviper.DSMSourceReference
   dsviper.DSMSourceType
