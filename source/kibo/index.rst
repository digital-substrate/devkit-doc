Kibo
====

**Kibo** is the code generator. It reads a :term:`DSM` model plus a
:term:`Kibo template` and emits source code — typed C++, Python and TypeScript
surfaces wired for the Viper runtime when used with ``kibo-template-viper``.

Kibo is the second step of the :doc:`code-generation pipeline
<../ecosystem/pipeline>`: ``DSM → Kibo → kibo-template-viper``. Kibo itself
is template-agnostic — change the template and you change the target
language and runtime. This section covers Kibo's command line, the
Template Model a template reads, and kibo-project, which drives the
generation of a whole project. The catalogue of templated features it
produces in the Viper world lives in :doc:`../kibo-template-viper/index`.

This is kibo 2, which exposes **Template Model 2** and generates over the
same 1.2 runtime as kibo 1.2. A template pack written for kibo 1.2 moves
with :doc:`migrating`.


Place in the ecosystem
----------------------

* **Depends on** — :term:`DSM` models (``.dsm.json`` files), a Kibo template pack.
* **Consumed by** — developers, through :doc:`kibo-project` and a project's
  ``kibo.toml``, or directly by running the JAR.
* **Source repositories** —
  `digital-substrate/kibo <https://github.com/digital-substrate/kibo>`_,
  a Java tool bridging DSM and StringTemplate, and
  `digital-substrate/kibo-project <https://github.com/digital-substrate/kibo-project>`_.
* **Distribution** — a single JAR (``kibo-2.0.0.jar``) and the
  ``kibo_project.py`` script.


Quickstart
----------

A project states its generation once, in a ``kibo.toml``:

.. code-block:: toml

   [project]
   definitions = "definitions"
   infrastructure = "myapp"

   [generator]
   templates = "2"

   [target.python]
   features = ["Base", "Wheel"]
   output = "python/generated"

   [target.cpp]
   features = ["Base", "Attachments"]
   output = "cpp/generated"

.. code-block:: bash

   python3 kibo_project.py generate kibo.toml

The Python result is a typed package, ``import myapp``, ready to be used
through :term:`dsviper`; the C++ result is headers and ``.cpp`` files that
link against the :term:`Viper C++` runtime. Calling the JAR directly is
covered in :doc:`usage`.


Topics
------

.. toctree::
   :maxdepth: 2

   templates
   usage
   kibo-project
   template_model
   migrating


Status
------

Kibo 2 — Template Model 2, over the 1.2 runtime. Kibo 1.2 and Template
Model 1 are documented in the :doc:`Kibo 1 section <../kibo-1/index>`.
