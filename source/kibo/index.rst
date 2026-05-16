Kibo
====

**Kibo** is the code generator. It reads a :term:`DSM` model plus a
:term:`Kibo template` and emits source code — typed Python and C++ surfaces
wired for the Viper C++ runtime when used with ``kibo-template-viper``.

Kibo is the second step of the :doc:`code-generation pipeline
<../ecosystem/pipeline>`: ``DSM → Kibo → kibo-template-viper``. Kibo itself
is template-agnostic — change the template and you change the target
language and runtime. This section covers Kibo's CLI usage. The catalogue
of templated features it produces in the dsviper / Viper C++ world lives in
:doc:`../kibo-template-viper/index`.


Place in the ecosystem
----------------------

* **Depends on** — :term:`DSM` models (``.dsm.json`` files), a Kibo template pack.
* **Consumed by** — developers, directly (running the JAR) or through the ``dsm_util.py`` wrapper in ``dsviper-tools``.
* **Source repository** —
  `digital-substrate/kibo <https://github.com/digital-substrate/kibo>`_.
  Implemented as a Java tool bridging DSM and StringTemplate.
* **Distribution** — bundled in the DevKit ZIP as a single JAR
  (e.g. ``tools/kibo-1.2.7.jar``).


Quickstart
----------

The common Python case (DSM → typed Python package) is wrapped by
``dsm_util.py``:

.. code-block:: bash

   python3 tools/dsm_util.py create_python_package model.dsm

Direct Kibo invocation, for finer control or for the C++ surface:

.. code-block:: bash

   # Python package — consumed by dsviper
   java -jar tools/kibo-1.2.7.jar \
       -c python -n MyApp \
       -d model.dsm.json \
       -t templates/python/package \
       -o ./generated

   # C++ surface — consumed by Viper C++
   java -jar tools/kibo-1.2.7.jar \
       -c cpp -n MyApp \
       -d model.dsm.json \
       -t templates/cpp/Data \
       -o ./generated

The Python result is a typed package importable as
``import MyApp.attachments`` (or whatever namespace your DSM model
declares), ready to be used through :term:`dsviper`. The C++ result is
headers and ``.cpp`` files designed to link against the :term:`Viper C++`
runtime.


Topics
------

.. toctree::
   :maxdepth: 2

   templates
   usage
   template_model


Status
------

Part of DevKit 1.2.x (LTS, feature-locked).
