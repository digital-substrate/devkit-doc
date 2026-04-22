Concepts
========

This section explores the architecture, philosophy, and design patterns that make Viper
a powerful metadata-driven runtime.

Viper Runtime (Core)
--------------------

The Viper Runtime provides Type/Value system, serialization, database, and RPC.

.. toctree::
   :maxdepth: 2

   viper_philosophy
   viper_architecture
   viper_type_system
   viper_value_system
   viper_patterns
   viper_glossary

Commit Engine
-------------

The Commit Engine provides DAG versioning with immutable history, built on top of the Viper Runtime.

.. toctree::
   :maxdepth: 2

   commit_overview
   commit_contract
   commit_patterns
   commit_glossary
   industry_context

Transversal Topics
------------------

Topics spanning both Viper Runtime and Commit Engine.

.. toctree::
   :maxdepth: 2

   code_generation
   services
