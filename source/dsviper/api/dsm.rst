DSM Introspection
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
