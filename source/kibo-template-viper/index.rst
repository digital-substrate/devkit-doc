kibo-template-viper
===================

The first-party :term:`Kibo template` for the dsviper / Viper ecosystem.
Consumed by Kibo to emit C++ and Python surfaces from a DSM model.

This is the template that sits in the third slot of the
:doc:`code-generation pipeline <../ecosystem/pipeline>`: ``DSM → Kibo →
kibo-template-viper`` produces a typed Python package usable from
:term:`dsviper`, plus C++ surfaces for embedding in a Viper application.


Place in the ecosystem
----------------------

* **Depends on** — :term:`Kibo`, :term:`DSM`, the Viper runtime.
* **Consumed by** — ``kibo`` invocations targeting the dsviper / Viper
  runtime. Not used directly by end users — it is invoked through the
  ``kibo`` CLI (or via ``dsm_util.py create_python_package``, which calls
  Kibo with this template under the hood).
* **Source repository** —
  `digital-substrate/kibo-template-viper
  <https://github.com/digital-substrate/kibo-template-viper>`_.
* **Distribution** — bundled in the DevKit ZIP alongside ``kibo`` and the
  rest of the toolchain.


Status
------

.. note::

   Stub. Detailed documentation of the template's options, output structure,
   and customization points is forthcoming. Until then, refer to the GitHub
   repository and the :doc:`Kibo manual <../kibo/usage>`.
