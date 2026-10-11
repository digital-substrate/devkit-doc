Migrating from kibo 1.2
=======================

A project generated with kibo 1.2 and the kibo-template-viper 1.2 pack moves to
kibo 2 and kibo-template-viper 2.0 in up to three steps. The DSM model, the
runtime and the databases do not move: only the generator, the code it
generates, and the code written against that code.

1. :doc:`project` — the generation script (``generate.py``, or ``dsm_util.py
   create_python_package`` / ``create_node_package``) becomes a ``kibo.toml``
   run by kibo-project. Every project takes this step.
2. :doc:`template-pack` — templates of your own, written for Template Model 1,
   are rewritten for Template Model 2. Only a project with templates of its own
   takes this step; the first-party pack is already migrated.
3. :doc:`application` — the code that calls the generated packages moves to
   their 2.0 surface, in Python, TypeScript and C++.

Do them in this order, each as a change of its own: the generation first, since
the other two are checked against what it generates. One exception: a project
with templates of its own renders their *before* with kibo 1.2 first, while
kibo 1.2 and its outputs are still in place (see :doc:`project`).

.. toctree::
   :maxdepth: 2

   project
   template-pack
   application
