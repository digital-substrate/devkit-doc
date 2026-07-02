Values
======

Values are instances of types. ``Value`` is the base class with factory methods
for creating and converting values.

**When to use**: Use values to hold typed data. Primitives are immutable;
containers (Vector, Map, Set, XArray) are mutable.

Quick Start
-----------

.. code-block:: python

   from dsviper import Value, ValueString, ValueInt64, ValueVector, TypeVector, Type

   # Direct construction for primitives
   name = ValueString("Alice")
   count = ValueInt64(42)

   # Factory method with type (for containers)
   t_vec = TypeVector(Type.INT64)
   numbers = Value.create(t_vec, [1, 2, 3])

   # Access underlying Python value
   print(name.get())         # "Alice"
   print(list(numbers))      # [1, 2, 3]

   # Check type
   print(name.type())        # string

Choosing the Right Pattern
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - Pattern
     - When to Use
     - Example
   * - ``ValueString("...")``
     - Direct primitive construction
     - ``ValueInt64(42)``
   * - ``Value.create(type, data)``
     - Generic factory with type
     - ``Value.create(t_vec, [1,2,3])``
   * - ``Value.decode(type, bytes)``
     - Deserialize from binary
     - ``Value.decode(Type.STRING, data)``
   * - ``ValueXxx.cast(value)``
     - Type casting
     - ``ValueInt64.cast(v)``

Base Class
----------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.Value

Primitive Values
----------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ValueVoid
   dsviper.ValueBool
   dsviper.ValueUInt8
   dsviper.ValueUInt16
   dsviper.ValueUInt32
   dsviper.ValueUInt64
   dsviper.ValueInt8
   dsviper.ValueInt16
   dsviper.ValueInt32
   dsviper.ValueInt64
   dsviper.ValueFloat
   dsviper.ValueDouble
   dsviper.ValueString
   dsviper.ValueBlob
   dsviper.ValueBlobId
   dsviper.ValueCommitId
   dsviper.ValueUUId

Container Values
----------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ValueVector
   dsviper.ValueVectorIter
   dsviper.ValueSet
   dsviper.ValueSetIter
   dsviper.ValueMap
   dsviper.ValueMapKeysIter
   dsviper.ValueMapValuesIter
   dsviper.ValueMapItemsIter
   dsviper.ValueXArray
   dsviper.ValueOptional

Algebraic Values
----------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ValueTuple
   dsviper.ValueTupleIter
   dsviper.ValueVec
   dsviper.ValueMat
   dsviper.ValueVariant
   dsviper.ValueAny

User-Defined Values
-------------------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ValueStructure
   dsviper.ValueEnumeration
   dsviper.ValueKey

Value Program
-------------

A ``ValueProgram`` is a sequence of opcodes that describe mutations to values.
Each opcode represents an atomic operation (set, update, union, subtract, etc.).

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ValueProgram
   dsviper.ValueOpcodeKey
   dsviper.ValueOpcode
   dsviper.ValueOpcodeDocumentSet
   dsviper.ValueOpcodeDocumentUpdate
   dsviper.ValueOpcodeMapUnion
   dsviper.ValueOpcodeMapSubtract
   dsviper.ValueOpcodeMapUpdate
   dsviper.ValueOpcodeSetUnion
   dsviper.ValueOpcodeSetSubtract
   dsviper.ValueOpcodeXArrayInsert
   dsviper.ValueOpcodeXArrayRemove
   dsviper.ValueOpcodeXArrayUpdate

