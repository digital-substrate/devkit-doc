Remote Services
===============

The client-side surface for consuming a Viper **Service** over the network.
Every class here is a ``ServiceRemote*`` type: the dynamic, metadata-driven
handle returned by :meth:`ServiceRemote.connect` and the introspected pool /
function objects hanging off it.

The single entry point is :meth:`ServiceRemote.connect` — everything else is
discovered at runtime from the service's embedded DSM. The same handle connects
to *any* Viper service with no per-service codegen; the Kibo-generated typed
proxies (``function_pool_remotes``, ``attachment_function_pool_remotes``) are a
comfort layer that wraps this same surface. For *what* a service is, the two
pool kinds, and the server side, see :doc:`/services/index`.

.. note::

   The server side (``Viper::Service``, ``Viper::ServiceServer``) is C++ only —
   it is not part of the ``dsviper`` Python module. Python is a **client** of
   Viper services.

Quick Start
-----------

The universal dynamic client — connect, then dispatch by pool and function
name through a runtime dictionary. No service-specific import:

.. code-block:: python

   from dsviper import Definitions, ServiceRemote

   defs = Definitions()
   s = ServiceRemote.connect("localhost", "54328", defs)

   # Dispatch by pool name → function name → call.
   result = s.function_pool_funcs("Tools")["add"](32, 10)   # 42

   s.close()

The five-line connection scaffold ships with ``dsviper-tools`` as
``service_client.py``; any REPL session or schema-agnostic adapter extends from
there.

.. seealso::

   For the typed-proxy path (Kibo-generated, per-pool, IDE-friendly) and the
   Remote-Local protocol behind stateful calls, see :doc:`/services/services`
   and :doc:`/services/remote_local`.

Introspecting a live service
----------------------------

Because the service ships its DSM inside the binary, a connected client can
enumerate the whole typed surface — pools, functions, prototypes, and the
documentation authored in the DSM — without any prior knowledge of the schema.

**List the pools.** Stateless and stateful pools are reported separately, each
carrying its name and embedded documentation:

.. code-block:: python

   for pool in s.function_pools():              # ServiceRemoteFunctionPool
       print("function_pool", pool.name(), "—", pool.documentation())

   for pool in s.attachment_function_pools():   # ServiceRemoteAttachmentFunctionPool
       print("attachment_function_pool", pool.name(), "—", pool.documentation())

**Walk the functions, with prototypes and docs.** Each function exposes its
:class:`FunctionPrototype` (return type and named parameters) and its embedded
documentation; stateful functions additionally report whether they mutate:

.. code-block:: python

   pool = s.function_pools()[0]
   funcs = s.function_pool_funcs(pool.name())   # names via dir()

   for name in dir(funcs):
       fn = pool.check(name)                     # ServiceRemoteFunctionPoolFunction
       proto = fn.prototype()                    # FunctionPrototype
       args = ", ".join(f"{ty} {nm}" for nm, ty in proto.parameters())
       print(f"  {proto.return_type()} {name}({args})  # {fn.documentation()}")

   # For attachment pools, the per-function `.is_mutable()` reflects the
   # DSM `mutable` marker.

**Re-emit the service as DSM.** The most direct view is to reconstruct the DSM
source of the live service — pools, function signatures, and the embedded
documentation, exactly as written in the ``.dsm`` — from the connection alone:

.. code-block:: python

   dsm = s.to_dsm_definitions()                  # DSMDefinitions
   print(dsm.to_dsm())                           # DSM language text (docs included)

``to_dsm()`` includes documentation by default; pass ``html=True`` for a marked-up
rendering, or use :meth:`Html.dsm_definitions` to render the same model as a
styled HTML fragment.

Choosing the Right Entry Point
------------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - Need
     - Class / Method
     - Example
   * - Connect to a service
     - :meth:`ServiceRemote.connect`
     - ``s = ServiceRemote.connect(host, port, defs)``
   * - Call a stateless function
     - :class:`ServiceRemoteFunctionPoolFunctions`
     - ``s.function_pool_funcs("Tools")["add"](1, 2)``
   * - Call a stateful function
     - :class:`ServiceRemoteAttachmentFunctionPoolFunctions`
     - ``s.attachment_function_pool_funcs("PlayerModel")["create"](m, ...)``
   * - List exposed pools
     - :meth:`ServiceRemote.function_pools`
     - ``[p.name() for p in s.function_pools()]``
   * - Inspect a function signature
     - :class:`ServiceRemoteFunctionPoolFunction`
     - ``pool.check("add").prototype().parameters()``
   * - Re-emit the service schema
     - :meth:`ServiceRemote.to_dsm_definitions`
     - ``s.to_dsm_definitions().to_dsm()``

Connection
----------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ServiceRemote

Stateless Pools
---------------

The ``function_pool`` surface — pure functions, executed on the server,
returned immediately.

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ServiceRemoteFunctionPools
   dsviper.ServiceRemoteFunctionPool
   dsviper.ServiceRemoteFunctionPoolFunctions
   dsviper.ServiceRemoteFunctionPoolFunction
   dsviper.ServiceRemoteFunction

Stateful Pools
--------------

The ``attachment_function_pool`` surface — functions that execute on the server
but read and mutate the **client's** ``AttachmentMutating`` through the
Remote-Local protocol (see :doc:`/services/remote_local`).

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ServiceRemoteAttachmentFunctionPools
   dsviper.ServiceRemoteAttachmentFunctionPool
   dsviper.ServiceRemoteAttachmentFunctionPoolFunctions
   dsviper.ServiceRemoteAttachmentFunctionPoolFunction
   dsviper.ServiceRemoteAttachmentFunction

.. seealso::

   ``FunctionPrototype`` and the in-process pool classes (``FunctionPool``,
   ``Function``) live in :doc:`core`. The DSM model types returned by
   ``to_dsm_definitions`` (``DSMDefinitions``, ``DSMFunctionPool``) are in
   :doc:`dsm`.
