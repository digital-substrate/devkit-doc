Values
======

Values are instances of types. ``Value`` is the base class with factory methods
for creating and converting values.

**When to use**: Use values to hold typed data. Primitives are immutable;
containers (Vector, Map, Set, XArray) are mutable.

Quick Start
-----------

>>> from dsviper import Value, ValueString, ValueInt64, TypeVector, Type

Primitives construct directly; containers go through ``Value.create``:

>>> name = ValueString("Alice")
>>> count = ValueInt64(42)
>>> numbers = Value.create(TypeVector(Type.INT64), [1, 2, 3])

Coming back out to Python objects is ``Value.dumps`` for anything, and
``encoded()`` for a primitive:

>>> Value.dumps(name)
'Alice'
>>> name.encoded()
'Alice'
>>> Value.dumps(numbers)
[1, 2, 3]

Reading an element of a container already gives a native:

>>> numbers[0]
1
>>> name.type()
string

A Value is not the Python object it wraps — ``str()`` gives the DSM
representation, quotes included:

>>> isinstance(name, str)
False
>>> str(name)
"'Alice'"

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
   * - ``Value.decode(blob, type, definitions)``
     - Deserialize from binary
     - ``Value.decode(blob, Type.STRING, defs.const())``
   * - ``ValueXxx.cast(value)``
     - Type casting
     - ``ValueInt64.cast(v)``
   * - ``Value.dumps(value)``
     - Back out to Python objects
     - ``Value.dumps(name)`` → ``'Alice'``
   * - ``value.encoded()``
     - Back out a primitive
     - ``name.encoded()`` → ``'Alice'``

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

Executing a program leaves a trace of the opcodes it ran, in the same
vocabulary:

.. autosummary::
   :toctree: generated/
   :nosignatures:

   dsviper.ValueProcessorTrace
   dsviper.ValueProcessorTraceOpcode

