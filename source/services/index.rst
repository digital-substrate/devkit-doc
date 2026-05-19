Service
=======

A **Service** is a container that exposes typed business logic across
the network. It composes DSM definitions and one or more
:term:`function pools <function pool>` — stateless ``FunctionPool`` and/or
stateful ``AttachmentFunctionPool`` — into a single immutable bundle
served over a socket.

Services are a Viper C++ Runtime feature. The protocol communicates
through the ``AttachmentMutating`` interface: stateful pool
functions read and mutate whatever the client passes as their
``AttachmentMutating`` — a value, a structure, an in-memory
container, or any other backend that implements the interface. The
service mechanism itself does not persist anything and does not
assume any particular storage tier.


Place in the ecosystem
----------------------

* **Depends on** — :doc:`DSM <../dsm/index>` and the Viper C++ engine
  (the runtime that registers pools, marshals values, and runs the RPC protocol).
* **Consumed by** — any Python or C++ client that imports ``dsviper`` (Python) or links Viper C++ (C++).


Topics
------

.. toctree::
   :maxdepth: 2

   services
   remote_local
