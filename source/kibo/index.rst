Kibo
====

**Kibo** is the code generator. It reads a :term:`DSM` model plus a
:term:`Kibo template` and emits source code — typed Python and C++ surfaces
wired for the Viper runtime when used with ``kibo-template-viper``.

Kibo is the second step of the :doc:`code-generation pipeline
<../ecosystem/pipeline>`: ``DSM → Kibo → kibo-template-viper``. Kibo itself
is template-agnostic — change the template and you change the target
language and runtime. This section covers Kibo's CLI usage. The catalogue
of templated features it produces in the dsviper / Viper world lives in
:doc:`../kibo-template-viper/index`.


Place in the ecosystem
----------------------

* **Depends on** — :term:`DSM` (consumes ``.dsm`` and ``.dsmb`` files), a
  Kibo template directory.
* **Consumed by** — developer toolchains directly (Java CLI), and
  indirectly through ``dsm_util.py create_python_package``, which invokes
  Kibo with ``kibo-template-viper`` under the hood.
* **Source repository** —
  `digital-substrate/kibo <https://github.com/digital-substrate/kibo>`_.
  Implemented as a Java tool bridging DSM and StringTemplate.
* **Distribution** — bundled in the DevKit ZIP as a single JAR
  (e.g. ``tools/kibo-1.2.7.jar``).


Quickstart
----------

The common case (DSM → typed Python package) is wrapped by ``dsm_util.py``:

.. code-block:: bash

   python3 tools/dsm_util.py create_python_package model.dsm

Direct Kibo invocation, for finer control:

.. code-block:: bash

   java -jar tools/kibo-1.2.7.jar \
       -c python -n MyApp \
       -d model.dsmb \
       -t templates/python/package \
       -o ./generated

The result is a typed Python package importable as
``import MyApp.attachments`` (or whatever namespace your DSM model
declares), ready to be used through :term:`dsviper`.


Topics
------

.. toctree::
   :maxdepth: 2

   templates
   usage
   template_model


Status
------

Part of DevKit 1.2.x. Kibo itself is stable; new templated features are
added in :doc:`kibo-template-viper <../kibo-template-viper/index>` and
other templates as the ecosystem grows.
