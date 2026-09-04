Core Utilities
==============

Core classes for namespaces, paths, and cross-cutting utilities.
``Definitions`` itself is documented with the DSM surface it registers, in
:doc:`dsm`.

**When to use**: Use ``Definitions`` to register custom types, ``Path`` to
navigate nested structures, and ``Logging`` for debug output.

Quick Start
-----------

>>> from dsviper import (DSMBuilder, Value, Path, NameSpace, ValueUUId,
...                      LoggerConsole, Logging)

A namespace pairs a UUID with a name:

>>> ns = NameSpace(ValueUUId("f529bc42-0618-4f54-a3fb-d55f95c5ad03"), "MyApp")
>>> ns.name()
'MyApp'

A ``Path`` navigates nested structures. Build it, freeze it with
``const()``, then read and write through it:

>>> builder = DSMBuilder()
>>> builder.append("model.dsm", """
... namespace MyApp {8f14e45f-ceea-467a-9575-1c14b48f0b7e} {
...     struct Address { string city; };
...     struct Profile { Address address; uint16 age; };
... };
... """)
>>> report, dsm_defs, defs = builder.parse()
>>> defs.inject(globals())
>>> document = Value.create(MY_APP_S_PROFILE, {"address": {"city": "Lyon"}, "age": 30})

>>> path = Path.from_field("address").field("city").const()
>>> path.representation()
'.address.city'
>>> path.at(document)
'Lyon'
>>> path.set(document, "Paris")
>>> Value.dumps(document)
{'address': {'city': 'Paris'}, 'age': 30}

``inject()`` also emits a constant per path, so the one above is already
available as ``MY_APP_P_PROFILE_ADDRESS``.

A logger writes to stderr through its ``Logging`` interface:

>>> log = LoggerConsole(Logging.LEVEL_DEBUG).logging()
>>> log.info("Application started")
>>> log.error("Something went wrong")

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
   dsviper.KeyHelper
   dsviper.KeyNamer
