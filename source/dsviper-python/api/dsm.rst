DSM & Definitions
=================

DSM classes provide parsing and introspection of Digital Substrate Model files.

**When to use**: Use ``DSMBuilder`` to parse ``.dsm`` files and introspect
the resulting definitions (structures, enumerations, attachments, functions).

Quick Start
-----------

>>> from dsviper import *
>>> MODEL = """
... namespace MyApp {8f14e45f-ceea-467a-9575-1c14b48f0b7e} {
...     concept User;
...     struct Profile { string city; uint16 age; };
...     attachment<User, Profile> profile;
... };
... """
>>> builder = DSMBuilder()
>>> builder.append("model.dsm", MODEL)
>>> report, dsm_defs, defs = builder.parse()
>>> report.has_error()
False
>>> defs.inject(globals())             # MY_APP_T_USER, MY_APP_A_USER_PROFILE, …

The declarations are reachable from ``dsm_defs``:

>>> for struct in sorted(dsm_defs.structures(), key=str):
...     print(struct.type_name())
...     for field in struct.fields():
...         print(" ", field.name(), ":", field.type())
MyApp::Profile
  city : string
  age : uint16

>>> for att in dsm_defs.attachments():
...     print(att.type_name(), "-- key:", att.key_type(), "doc:", att.document_type())
MyApp::profile -- key: MyApp::User doc: MyApp::Profile

``inject()`` fills the namespace with one constant per definition. The
prefix is derived from the DSM namespace, split on camel case — ``MyApp``
gives ``MY_APP_``, not ``MYAPP_``:

>>> ns = {}
>>> defs.inject(ns)
>>> sorted(ns)
['MY_APP_A_USER_PROFILE', 'MY_APP_K_USER', 'MY_APP_P_PROFILE_AGE',
 'MY_APP_P_PROFILE_CITY', 'MY_APP_S_PROFILE', 'MY_APP_T_USER']

A parse that failed reports why, and hands back ``None`` for both
definitions:

>>> bad = DSMBuilder()
>>> bad.append("broken.dsm", "namespace Oops { struct S { string };")
>>> bad_report, bad_dsm, bad_defs = bad.parse()
>>> bad_report.has_error()
True
>>> (bad_dsm, bad_defs)
(None, None)
>>> for err in bad_report.errors()[:1]:
...     print(err.line(), err.message())
1 expected a UUID before `{`.

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
