Python Guide
============

This manual covers the **dsviper** Python API — the Python binding of the Viper
runtime. You will learn how to use the type and value system, work with databases,
and leverage the full power of Viper from Python.

The Metadata Everywhere Principle
---------------------------------

Viper carries its type information as runtime metadata, and every subsystem
draws on the same source: types, values, functions, serialization, database
persistence, and RPC. You describe your data once — either through the
static API generated from a DSM model, or directly through the dynamic
API — and the runtime handles conversion, validation, and cross-language
interoperability for you. This is why Python natives (``list``, ``dict``,
``tuple``) can be passed directly to typed ``dsviper`` functions: the
metadata drives the bridge, so there is nothing to register and nothing to
glue by hand.

.. toctree::
   :maxdepth: 2

   installation
   tutorial
   types_values
   collections
   structures
   errors
   dsm
   database
   commit
   commit_contract
   blobs
   serialization
