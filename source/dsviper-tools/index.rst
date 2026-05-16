dsviper-tools
=============

**dsviper-tools** is the runtime-side developer toolkit: CLI utilities, two
GUI editors (``cdbe.py`` for the commit-based ``CommitDatabase`` and
``dbe.py`` for the plain ``Database`` — see :doc:`editors` for the
distinction), and the server that exposes a ``CommitDatabase`` over the
network. Together with :doc:`Kibo <../kibo/index>`, it forms the day-to-day
developer experience around the dsviper runtime.

The toolkit covered here is the Qt Widgets variant; ``dsviper-tools-qml``
provides Qt Quick versions of the same database browsers.

See also :doc:`../dsm/ide` (VS Code / JetBrains plugins) and
:doc:`../kibo-template-viper/wheels` (Python wheel packaging).


Place in the ecosystem
----------------------

* **Depends on** — :term:`DSM`, :term:`dsviper`, PySide
* **Consumed by** — developer toolchains. Not a runtime dependency of
  applications.
* **Source repositories** —

  * `digital-substrate/dsviper-tools
    <https://github.com/digital-substrate/dsviper-tools>`_ — Qt Widgets.
  * `digital-substrate/dsviper-tools-qml
    <https://github.com/digital-substrate/dsviper-tools-qml>`_ — Qt Quick /
    QML.

* **Distribution** — bundled in the DevKit ZIP.


Quickstart
----------

Validate a DSM model:

.. code-block:: bash

   python3 tools/dsm_util.py check model.dsm

Create a versioned database from a DSM model:

.. code-block:: bash

   python3 tools/dsm_util.py create_commit_database model.dsm project.cdb

Open the database in the GUI editor:

.. code-block:: bash

   python3 tools/cdbe.py project.cdb

Expose the database over the network for multi-client editing:

.. code-block:: bash

   python3 tools/commit_database_server.py project.cdb


Topics
------

.. toctree::
   :maxdepth: 2
   :caption: Development

   dsm_util

.. toctree::
   :maxdepth: 2
   :caption: Database Tools

   editors
   server


Status
------

Part of DevKit 1.2.x (LTS, feature-locked).
