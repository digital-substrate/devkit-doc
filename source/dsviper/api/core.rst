Core Utilities
==============

Core classes for definitions, namespaces, paths, and utilities.

**When to use**: Use ``Definitions`` to register custom types, ``Path`` to
navigate nested structures, and ``Logging`` for debug output.

Quick Start
-----------

.. code-block:: python

   from dsviper import Definitions, NameSpace, ValueUUId, Path, LoggerConsole, Logging

   # Create namespace for your types
   ns = NameSpace(ValueUUId("f529bc42-0618-4f54-a3fb-d55f95c5ad03"), "MyApp")

   # Create and register definitions
   defs = Definitions()

   # Paths navigate nested structures
   path = Path.from_field("user").field("address").field("city").const()
   city = path.at(document)  # Get value at path
   path.set(document, "Paris")  # Set value at path

   # Logging for debugging
   logger = LoggerConsole(Logging.LEVEL_DEBUG)
   log = logger.logging()
   log.info("Application started")
   log.error("Something went wrong")

Key Classes
-----------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Class
     - Purpose
     - Example
   * - :class:`Definitions`
     - Register custom types
     - ``defs = Definitions()``
   * - :class:`NameSpace`
     - Group types by namespace
     - ``ns = NameSpace(uuid, "App")``
   * - :class:`Path`
     - Navigate nested data
     - ``Path.from_field("x").field("y")``
   * - :class:`Logging`
     - Debug output
     - ``logger.logging().info(msg)``
   * - :class:`Error`
     - Parse error messages
     - ``Error.parse(str(e))``

Definitions
-----------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Definitions
   dsviper.DefinitionsConst
   dsviper.DefinitionsCollector
   dsviper.DefinitionsInspector
   dsviper.DefinitionsMapper
   dsviper.DefinitionsExtendInfo

Namespace
---------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.NameSpace

Paths
-----

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Path
   dsviper.PathConst
   dsviper.PathComponent
   dsviper.PathElementInfo
   dsviper.PathEntryKeyInfo

Function Pools
--------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Function
   dsviper.FunctionPool
   dsviper.FunctionPoolFunctions
   dsviper.FunctionPrototype

Hashing
-------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Hashing
   dsviper.HashCRC32
   dsviper.HashMD5
   dsviper.HashSHA1
   dsviper.HashSHA256
   dsviper.HashSHA3

Logging
-------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Logging
   dsviper.LoggerConsole
   dsviper.LoggerPrint
   dsviper.LoggerReport
   dsviper.LoggerNull

Utilities
---------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ViperError
   dsviper.Error
   dsviper.Cancelation
   dsviper.Semaphore
   dsviper.SharedMemory
   dsviper.Socket
   dsviper.Float16
   dsviper.Fuzzer
   dsviper.KeyHelper
   dsviper.KeyNamer
