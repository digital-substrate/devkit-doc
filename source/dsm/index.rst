DSM
===

The **Digital Substrate Model (DSM)** is a small declarative language for
describing data models — namespaces, concepts, structures, attachments,
function pools. It is the modeling layer of the dsviper ecosystem and the
entry point of the :doc:`code-generation pipeline <../ecosystem/pipeline>`.

DSM is **standalone**: authoring a ``.dsm`` file does not require Kibo, the
Viper runtime, or dsviper. You can use it as a typed contract between teams,
or feed it into code generation when typed code is needed. See
:doc:`../ecosystem/value-chains` for where DSM sits in the broader picture.


Place in the ecosystem
----------------------

* **Depends on** — nothing. DSM is the root of the toolchain value chain.
* **Consumed by** — :term:`Kibo` (generates code from ``.dsm`` plus a
  template), :term:`dsviper` (loads ``.dsm`` through its
  :term:`dynamic API <static API / dynamic API>`),
  :term:`Commit Applications <Commit Application>` such as ``ge-py`` and
  ``ge-qml``.
* **Source repository** —
  `digital-substrate/dsm <https://github.com/digital-substrate/dsm>`_. Carries
  the ANTLR4 grammar (``DSM.g4``) and the canonical JSON wire format —
  producer-neutral, implemented by viper, kibo, and the IDE plugins.
* **Related repositories** —

  * `digital-substrate/dsm-samples
    <https://github.com/digital-substrate/dsm-samples>`_ — reference DSM
    models (``Tuto``, ``Ge``, ``Re``).
  * `digital-substrate/dsm-vscode
    <https://github.com/digital-substrate/dsm-vscode>`_ — VS Code plugin.
  * `digital-substrate/dsm-jetbrains
    <https://github.com/digital-substrate/dsm-jetbrains>`_ — JetBrains plugin.

  Install instructions: see :doc:`ide`.


Quickstart
----------

A minimal DSM file, exercising the
:doc:`five fundamental notions <introduction>` (namespace, concept, key,
document, attachment):

.. code-block:: dsm

   namespace Tuto {f529bc42-0618-4f54-a3fb-d55f95c5ad03} {

       concept User;

       struct Login {
           string nickname;
           string password;
       };

       attachment<User, Login> login;

   };

Validate the syntax:

.. code-block:: bash

   python3 tools/dsm_util.py check model.dsm

Generate a typed Python package (this delegates to Kibo with the viper
template):

.. code-block:: bash

   python3 tools/dsm_util.py create_python_package model.dsm

To use a model without code generation — load it through dsviper's dynamic
API at runtime — see :doc:`../dsviper/dsm`.


Topics
------

.. toctree::
   :maxdepth: 2

   introduction
   types
   concepts
   attachments
   function_pools
   ide
   samples/index


Status
------

Part of DevKit 1.2.x (LTS, feature-locked).
