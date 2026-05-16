Type System
===========

The type system defines all available types in Viper C++. ``Type`` is the base class
with static accessors for primitive types.

**When to use**: Use types to define schemas, validate data, and create
parameterized containers like vectors and maps.

Quick Start
-----------

.. code-block:: python

   from dsviper import Type, TypeVector, TypeMap, TypeOptional

   # Primitive type constants
   t_int = Type.INT64
   t_str = Type.STRING

   # Parameterized container types
   t_vec = TypeVector(Type.STRING)           # list of strings
   t_map = TypeMap(Type.STRING, Type.INT64)  # dict[str, int]

   # Nested types
   t_nested = TypeMap(Type.STRING, TypeVector(Type.FLOAT))

   # Nullable type
   t_opt = TypeOptional(Type.STRING)

Choosing the Right Type
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - Use Case
     - Type Class
     - Example
   * - Primitive value
     - ``Type.STRING``, ``Type.INT64``
     - Built-in constants
   * - Homogeneous list
     - :class:`TypeVector`
     - ``TypeVector(Type.INT64)``
   * - Key-value mapping
     - :class:`TypeMap`
     - ``TypeMap(Type.STRING, Type.INT64)``
   * - Nullable value
     - :class:`TypeOptional`
     - ``TypeOptional(Type.STRING)``
   * - Concurrent list
     - :class:`TypeXArray`
     - ``TypeXArray(Type.STRING)``
   * - Fixed-size tuple
     - :class:`TypeTuple`
     - ``TypeTuple([Type.INT64, Type.STRING])``

Base Class
----------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Type
   dsviper.TypeName

Primitive Types
---------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.TypeVoid
   dsviper.TypeBool
   dsviper.TypeUInt8
   dsviper.TypeUInt16
   dsviper.TypeUInt32
   dsviper.TypeUInt64
   dsviper.TypeInt8
   dsviper.TypeInt16
   dsviper.TypeInt32
   dsviper.TypeInt64
   dsviper.TypeFloat
   dsviper.TypeDouble
   dsviper.TypeString
   dsviper.TypeBlob
   dsviper.TypeBlobId
   dsviper.TypeCommitId
   dsviper.TypeUUId

Container Types
---------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.TypeVector
   dsviper.TypeSet
   dsviper.TypeMap
   dsviper.TypeXArray
   dsviper.TypeOptional

Algebraic Types
---------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.TypeTuple
   dsviper.TypeVec
   dsviper.TypeMat
   dsviper.TypeVariant
   dsviper.TypeAny

User-Defined Types
------------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.TypeStructure
   dsviper.TypeStructureDescriptor
   dsviper.TypeStructureField
   dsviper.TypeEnumeration
   dsviper.TypeEnumerationCase
   dsviper.TypeEnumerationDescriptor

Concept Types
-------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.TypeConcept
   dsviper.TypeClub
   dsviper.TypeKey
   dsviper.TypeAnyConcept
