# Template Model Reference

This reference documents the **Template Model** and **DSM Model** — the two class
hierarchies that the StringTemplate engine consumes when generating code from DSM
definitions.

Understanding this reference is essential for anyone writing or modifying `.stg`
template files.

## Code Generation Pipeline

Kibo generates code from a binary representation of DSM definitions. The pipeline is:

1. **Assemble** — Merge multiple `.dsm` files into a single definition set.
2. **Parse** — Produce the AST from the assembled definitions.
3. **Validate** — Check the semantics of the AST.
4. **Encode** — Convert the validated definitions to a binary representation (`.dsmb`).

```bash
dsm_util.py encode model.dsm model.dsmb
```

5. **Load** — Kibo reads the `.dsmb` file to construct a hierarchy of objects where the
   root object is an instance of `DSMDefinitions`.
6. **Convert** — The Object-Oriented representation is not suited for the StringTemplate
   engine, so Kibo converts it to a **Template Model** representation that drastically
   simplifies feature implementation with templates.

```{note}
DSM Model classes are **embedded** in the Template Model classes to provide a basic
introspection API. Template rules can access both layers.
```

## Type Suffix

During the conversion from DSM Model to Template Model, Kibo recursively collects and
decomposes all types and constructs a unique symbol per type called the **type suffix**.

### Decomposition Examples

- `float`
    - `_float`
- `vector<float>`
    - `_vector_float`
    - `_float`
- `map<tuple<int64, float>, vector<key<User>>>`
    - `_map_tuple_int64_float_to_vector_UserKey`
    - `_tuple_int64_float`
    - `_int64`
    - `_float`
    - `_vector_UserKey`
    - `_UserKey`

### Recursive Template Invocation

The type suffix is used in template rules to call the generated implementation for the
inner type (recursion).

In this example, the rule implements the `write` function for the generic type
`map<keyType, elementType>`. The `keyTypeSuffix` and `elementTypeSuffix` are used to call
the implementation of the `write` function for the `keyType` and for the `elementType`:

```text
void StreamWriter::write<v.typeSuffix>(<v.type> const & value) {
    writing->writeUInt64(static_cast<std::uint64_t>(value.size()));
    for (auto const & [k, v] : value) {
        write<v.keyTypeSuffix>(k);
        write<v.elementTypeSuffix>(v);
    }
}
```

The generated code for a `map<int8, string>` is:

```cpp
void StreamWriter::write_map_int8_to_string(std::map<std::int8_t,std::string> const & value) {
    writing->writeUInt64(static_cast<std::uint64_t>(value.size()));
    for (auto const & [k, v] : value) {
        write_int8(k);
        write_string(v);
    }
}
```

In theory, any feature can be implemented by recursively consuming the DSM definitions.
In practice, it is an art to elaborate the patterns used to implement a templated feature.

```{tip}
The best way to learn is by studying the templates:
- `templates/cpp/Model/*.stg`
- `templates/cpp/Stream/*.stg`
```

## Template Naming Convention

Type annotations are not available in StringTemplate, so a good parameter naming
convention improves understanding of the problem decomposition into template rules.

There is no convention for rule naming. However, the first rule is always
`main(m) ::=<<..>>` and the `m` parameter is a `TemplateDefinitions` instance.

| Parameter | Usage                |
|-----------|----------------------|
| `m`       | Definitions (module) |
| `ns`      | Namespace            |
| `a`       | Attachment           |
| `e`       | Enumeration          |
| `em`      | Enumeration Member   |
| `s`       | Structure            |
| `sf`      | Structure Field      |
| `c`       | Concept / Club       |
| `cc`      | Concept Child        |
| `cd`      | Concept Descendant   |
| `cm`      | Club Member          |
| `tm`      | Tuple Member         |
| `vm`      | Variant Member       |
| `po`      | Pool                 |
| `f`       | Function             |
| `p`       | Function Parameter   |
| `v`       | other                |

## Template Model

During the construction of the template model, the converter substitutes complex types
with simple string representations.

For instance, the string values substituted for the type `map<int64, vector<string>>`
in an instance of `TemplateMapFunction` are:

```java
class TemplateMapFunction {
    //...
    public String type;              // "std::map<std::int64, std::vector<string>>"
    public String typeSuffix         // "_map_int64_to_vector_string"
    public String keyTypeSuffix;     // "_int64"
    public String elementTypeSuffix; // "_vector_string"
    //...
}
```

The following sections use a **pseudo-class** representation to illustrate the fields
accessible by the StringTemplate engine to generate code and propagate the recursion.

```{note}
Since the fields for all Template Model classes are self-explanatory, only the use of
the fields for the root class `TemplateDefinitions` is explained in detail to bootstrap
the code generation.
```

### TemplateDefinitions

The root class exposes all the DSM definitions of the `model.dsmb` from the Template
Model perspective.

```java
public class TemplateDefinitions {

    public String generated;
    public String namespace;

    // Namespaces
    public ArrayList<TemplateNameSpace> nameSpaces;

    // Definitions
    public ArrayList<TemplateConcept> concepts;
    public ArrayList<TemplateClub> clubs;
    public ArrayList<TemplateStructure> structures;
    public ArrayList<TemplateStructure> sortedStructures;
    public ArrayList<TemplateEnumeration> enumerations;
    public ArrayList<TemplateAttachment> attachments;
    public ArrayList<TemplateAttachedKeyType> attachedKeyTypes;
    public ArrayList<TemplateAttachedDocumentType> attachedDocumentTypes;

    // Pools
    public ArrayList<TemplateFunctionPool> functionPools;
    public ArrayList<TemplateAttachmentFunctionPool> attachmentFunctionPools;

    // Attachment Pool
    public String attachmentsPoolUuid;

    // Functions
    public ArrayList<TemplateVecFunction> vecFunctions;
    public ArrayList<TemplateMatFunction> matFunctions;
    public ArrayList<TemplateTupleFunction> tupleFunctions;
    public ArrayList<TemplateOptionalFunction> optionalFunctions;
    public ArrayList<TemplateVectorFunction> vectorFunctions;
    public ArrayList<TemplateSetFunction> setFunctions;
    public ArrayList<TemplateMapFunction> mapFunctions;
    public ArrayList<TemplateXArrayFunction> xarrayFunctions;
    public ArrayList<TemplateVariantFunction> variantFunctions;
}
```

The `m` root object is injected in the rule `main(m) ::=<<..>>` and the recursive code
generation starts by consuming the fields of the root object:

```
# Anatomy of a complete Feature
# Depending of the Feature, you can omit some fields.

main(m) ::= <<
// Copyright ...
// <m.generated>
...

# generate something by namespace.
<m.nameSpace:namespace(): separator="\n">

# generate something for decomposed types.
<m.vecFunctions:vec(); separator="\n">
<m.matFunctions:mat(); separator="\n">
<m.tupleFunctions:tuple(); separator="\n">
<m.optionalFunctions:optional(); separator="\n">
<m.vectorFunctions:vector(); separator="\n">
<m.setFunctions:set(); separator="\n">
<m.mapFunctions:map(); separator="\n">
<m.xarrayFunctions:xarray(); separator="\n">
<m.variantFunctions:variant(); separator="\n">

>>

namespace(ns) ::= <<
# generate something for enumerations, structures, concepts and clubs.
<ns.concepts:concept(); separator="\n">
<ns.clubs:club(); separator="\n">
<ns.enumerations:enumeration(); separator="\n">
<ns.structures:structure(); separator="\n">

# generate something for attachments.
<ns.attachments:attachments(); separator="\n">
>>
```

### TemplateNameSpace

Groups definitions by namespace. Each namespace contains its own concepts, clubs,
structures, enumerations and attachments.

```java
public class TemplateNameSpace {
    // Namespace
    public String name;

    // Definitions
    public ArrayList<TemplateConcept> concepts;
    public ArrayList<TemplateClub> clubs;
    public ArrayList<TemplateStructure> structures;
    public ArrayList<TemplateStructure> sortedStructures;
    public ArrayList<TemplateEnumeration> enumerations;
    public ArrayList<TemplateAttachment> attachments;
}
```

### TemplateConcept

Corresponds to the definition of a `concept`.

```java
public class TemplateConcept {
    // DSM
    public DSMConcept dsmConcept;

    // Components
    public TemplateConcept parent;
    public String parentNameInNamespace;

    public ArrayList<TemplateConcept> children;
    public ArrayList<TemplateConcept> descendants;
    public ArrayList<TemplateConcept> strictDescendants;
    public ArrayList<TemplateConceptInNamespace> strictDescendantsInNamespace;

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeSuffix;

    // Attachments
    public ArrayList<TemplateAttachment> attachments;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
}
```

### TemplateConceptInNamespace

Wraps a `TemplateConcept` to provide namespace-qualified names. Used in
`strictDescendantsInNamespace` and `membersInNamespace` to generate correct type
references when a concept belongs to a different namespace.

```java
public class TemplateConceptInNamespace {
    // Component
    public TemplateConcept concept;

    // Namespace
    public String nameInNamespace;
    public String asNameInNamespace;
}
```

### TemplateClub

Corresponds to the definition of a `club`.

```java
public class TemplateClub {
    // DSM
    public DSMClub dsmClub;

    // Components
    public ArrayList<TemplateConcept> members;
    public ArrayList<TemplateConceptInNamespace> membersInNamespace;
    public ArrayList<TemplateConcept> memberDescendants;

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
}
```

### TemplateEnumeration

Corresponds to the definition of an `enum`.

```java
public class TemplateEnumeration {
    // DSM
    public DSMEnumeration dsmEnumeration;

    // Components
    public ArrayList<DSMEnumerationCase> members;

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
}
```

### TemplateStructure

Corresponds to the definition of a `struct`.

```java
public class TemplateStructure {
    // DSM
    public DSMStructure dsmStructure;

    // Components
    public ArrayList<TemplateStructureField> fields;

    // Predicates
    public boolean isMovable;

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
}
```

### TemplateStructureField

```java
public class TemplateStructureField {
    // DSM
    public DSMStructureField dsmField;

    public String name;
    public String passBy;
    public String defaultValue;

    // Predicates
    public boolean isMovable;
    public boolean isTypeAny;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeInNamespace;
    public String typeSuffix;

    // Field
    public TemplateField field;

    // Viper
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
}
```

### TemplateAttachment

Corresponds to the definition of an `attachment`.

```java
public class TemplateAttachment {
    // DSM
    public String dsmAttachment;

    public String representation;
    public String identifier;

    // Namespace
    public String namespace;
    public String name;

    // Runtime ID
    public String runtimeId;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public TemplateAttachedKeyType keyType;
    public TemplateAttachedDocumentType documentType;

    // Python
    public String pythonIdentifier;
}
```

### TemplateAttachedKeyType

```java
public class TemplateAttachedKeyType {
    // Namespace
    public String namespace;
    public String name;

    // Type
    public String type;
    public String typeInNamespace;
    public String typeSuffix;

    // Viper
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
}
```

### TemplateAttachedDocumentType

```java
public class TemplateAttachedDocumentType {
    // Predicates
    public Boolean isStructure;
    public Boolean useBlobId;

    // Component
    public TemplateStructure structure;

    // Type
    public String type;
    public String typeInNamespace;
    public String typeSuffix;

    // Field
    public TemplateField field;

    // Viper
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
}
```

### TemplateField

This class is used to generate **path-based mutators** per container.

```java
public class TemplateField {
    public String passBy;

    // Predicates
    public Boolean isNotBox;
    public Boolean isBox;
    public Boolean isSet;
    public Boolean isMap;
    public Boolean isXArray;

    // Type
    public String type;
    public String keyType;
    public String keyTypeSuffix;
    public String elementType;
    public String elementTypeSuffix;

    // Viper
    public String elementTypeViperValue;

    // Python
    public TemplatePythonType pythonKeyType;
    public TemplatePythonType pythonElementType;
}
```

### TemplateFunctionPool

Corresponds to the definition of a `function_pool`.

```java
public class TemplateFunctionPool {
    // DSM
    public String name;
    public String uuid;

    // Components
    public ArrayList<TemplateFunction> functions;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
}
```

### TemplateFunction

```java
public class TemplateFunction {
    // DSM
    public String name;

    // Components
    public ArrayList<TemplateFunctionParameter> parameters;

    // Predicates
    public Boolean isVoid;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeSuffix;

    // Viper
    public String returnViperValue;

    // Python
    public TemplatePythonType returnPythonType;
}
```

### TemplateFunctionParameter

```java
public class TemplateFunctionParameter {
    // DSM
    public String name;

    public String passBy;

    // Type
    public String type;
    public String typeSuffix;

    // Viper
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
}
```

### TemplateAttachmentFunctionPool

Corresponds to the definition of an `attachment_function_pool`.

```java
public class TemplateAttachmentFunctionPool {
    // DSM
    public String name;
    public String uuid;

    // Components
    public ArrayList<TemplateAttachmentFunction> functions;

    // Documentation
    public boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
}
```

### TemplateAttachmentFunction

```java
public class TemplateAttachmentFunction {
    // DSM
    public String name;

    // Components
    public ArrayList<TemplateFunctionParameter> parameters;

    // Predicates
    public boolean isVoid;

    // Documentation
    public Boolean hasDocumentation;
    public String documentation;

    // Type
    public String type;
    public String typeSuffix;

    // Type
    public String interfaceType;

    // Viper
    public String returnViperValue;

    // Python
    public TemplatePythonType returnPythonType;
}
```

### TemplateVecFunction

Corresponds to the definition of a `vec<elementType, size>`.

```java
public class TemplateVecFunction {
    // DSM
    public String dsmType;
    public String size;

    // Type
    public String type;
    public String typeSuffix;
    public String elementTypeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
    public TemplatePythonType getPythonElementType;
    public String pythonTupleType;
}
```

### TemplateMatFunction

Corresponds to the definition of a `mat<elementType, columns, rows>`.

```java
public class TemplateMatFunction {
    // DSM
    public String dsmType;
    public String columns;
    public String rows;

    // Type
    public String type;
    public String typeSuffix;
    public String elementTypeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
    public TemplatePythonType pythonElementType;
    public String pythonTupleType;
    public String pythonColumnType;
}
```

### TemplateType

Represents a generic type member used in `tuple` and `variant` definitions.

```java
public class TemplateType {
    // Type
    public String type;
    public String typeSuffix;
}
```

### TemplateTupleFunction

Corresponds to the definition of a `tuple<T0, ...>`.

```java
public class TemplateTupleFunction {
    // DSM
    public String dsmType;

    // Components
    public ArrayList<TemplateType> members;

    // Type
    public String type;
    public String typeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
    public ArrayList<TemplatePythonType> pythonMembers;
}
```

### TemplateOptionalFunction

Corresponds to the definition of an `optional<elementType>`.

```java
public class TemplateOptionalFunction {
    // DSM
    public String dsmType;

    // Type
    public String type;
    public String typeSuffix;
    public String elementType;
    public String elementTypeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
    public TemplatePythonType pythonElementType;
}
```

### TemplateVectorFunction

Corresponds to the definition of a `vector<elementType>`.

```java
public class TemplateVectorFunction {
    // DSM
    public String dsmType;

    public String valueRef;

    // Type
    public String type;
    public String elementTypeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
    public TemplatePythonType pythonElementType;
}
```

### TemplateSetFunction

Corresponds to the definition of a `set<elementType>`.

```java
public class TemplateSetFunction {
    // DSM
    public String dsmType;

    // Type
    public String type;
    public String typeSuffix;
    public String elementTypeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
    public TemplatePythonType pythonElementType;
}
```

### TemplateMapFunction

Corresponds to the definition of a `map<keyType, elementType>`.

```java
public class TemplateMapFunction {
    // DSM
    public String dsmType;

    // Type
    public String type;
    public String typeSuffix;
    public String keyTypeSuffix;
    public String elementTypeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
    public TemplatePythonType pythonKeyType;
    public TemplatePythonType pythonElementType;
}
```

### TemplateVariantFunction

Corresponds to the definition of a `variant<T0, ...>`.

```java
public class TemplateVariantFunction {
    // DSM
    public String dsmType;

    // Components
    public ArrayList<TemplateType> members;

    // Type
    public String type;
    public String typeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
    public ArrayList<TemplatePythonType> pythonMembers;
}
```

### TemplateXArrayFunction

Corresponds to the definition of a `xarray<elementType>`.

```java
public class TemplateXArrayFunction {
    // DSM
    public String dsmType;

    // Type
    public String type;
    public String typeSuffix;
    public String elementTypeSuffix;

    // Viper
    public String viperType;
    public String viperValue;

    // Python
    public TemplatePythonType pythonType;
    public TemplatePythonType pythonElementType;
}
```

### TemplatePythonType

Used to generate Python proxy classes for Viper.

```java
public class TemplatePythonType {
    // Proxy
    public Boolean useProxy;
    public String proxy;

    // Type
    public String typeSuffix;
    public String type;
}
```

## DSM Model

The DSM Model is the projection of the DSM definitions into a hierarchy of Java classes.

The pseudo-classes below express the public API that the StringTemplate engine consumes
when evaluating rule substitutions.

```{note}
These classes are **embedded** in the Template Model classes for basic introspection.
For example, `TemplateConcept.dsmConcept` gives access to the underlying `DSMConcept`.
```

### DSMDefinitions

The root class references all the DSM definitions found in the `model.dsmb`.

```java
public class DSMDefinitions {
    public ArrayList<DSMConcept> concepts;
    public ArrayList<DSMClub> clubs;
    public ArrayList<DSMEnumeration> enumerations;
    public ArrayList<DSMStructure> structures;
    public ArrayList<DSMAttachment> attachments;

    public ArrayList<DSMFunctionPool> functionPools;
    public ArrayList<DSMAttachmentFunctionPool> attachmentFunctionPools;
}
```

### DSMTypeReference

Used when a reference to another type is needed. For example, to express the list of
members of a `club`.

```java
public class DSMTypeReference {
    public TypeName typeName;
    public DSMTypeReferenceDomain domain;
}
```

### DSMConcept

Corresponds to the definition of a `concept`.

```java
public class DSMConcept {
    public TypeName typeName;
    public DSMTypeReference parent;
    public String documentation;
    public DSMTypeReference typeReference;
    public UUID runtimeId;
}
```

### DSMClub

Corresponds to the definition of a `club` with related `membership`.

```java
public class DSMClub {
    public TypeName typeName;
    public ArrayList<DSMTypeReference> members;
    public String documentation;
    public DSMTypeReference typeReference;
    public UUID runtimeId;
}
```

### DSMEnumeration

Corresponds to the definition of an `enum`.

```java
public class DSMEnumeration {
    public TypeName typeName;
    public ArrayList<DSMEnumerationCase> members;
    public String documentation;
    public DSMTypeReference typeReference;
    public UUID runtimeId;
}

public class DSMEnumerationCase {
    public String name;
    public String documentation;
}
```

### DSMStructure

Corresponds to the definition of a `struct` and provides access to the definition of the
structure fields.

```java
public class DSMStructure {
    public TypeName typeName;
    public ArrayList<DSMStructureField> fields;
    public String documentation;
    public DSMTypeReference typeReference;
    public UUID runtimeId;
}

public class DSMStructureField {
    public String name;
    public DSMType type;
    public DSMLiteral defaultValue;
    public String documentation;
}
```

### DSMLiteral

Used to express the literal value for the initialization of a field.

```java
public abstract class DSMLiteral {
    public abstract String representation();
}

public class DSMLiteralValue extends DSMLiteral {
    public DSMLiteralDomain domain;
    public String value;
}

public final class DSMLiteralList extends DSMLiteral {
    public final ArrayList<DSMLiteral> members;
}
```

### DSMType

The base class of types.

```java
public abstract class DSMType {
    public abstract String representation();
}
```

### DSMTypeVec

Corresponds to the definition of a `vec<T, n>`.

```java
public class DSMTypeVec extends DSMType {
    public DSMTypeReference elementType;
    public long size;
}
```

### DSMTypeMat

Corresponds to the definition of a `mat<T, columns, rows>`.

```java
public class DSMTypeMat extends DSMType {
    public DSMTypeReference elementType;
    public long columns;
    public long rows;
}
```

### DSMTypeTuple

Corresponds to the definition of a `tuple<T0, ...>`.

```java
public class DSMTypeTuple extends DSMType {
    public ArrayList<DSMType> types;
}
```

### DSMTypeOptional

Corresponds to the definition of an `optional<T>`.

```java
public class DSMTypeOptional extends DSMType {
    public DSMType elementType;
}
```

### DSMTypeVector

Corresponds to the definition of a `vector<T>`.

```java
public class DSMTypeVector extends DSMType {
    public DSMType elementType;
}
```

### DSMTypeSet

Corresponds to the definition of a `set<T>`.

```java
public class DSMTypeSet extends DSMType {
    public DSMType elementType;
}
```

### DSMTypeMap

Corresponds to the definition of a `map<K, V>`.

```java
public class DSMTypeMap extends DSMType {
    public DSMType keyType;
    public DSMType elementType;
}
```

### DSMTypeVariant

Corresponds to the definition of a `variant<T0, ...>`.

```java
public class DSMTypeVariant extends DSMType {
    public ArrayList<DSMType> types;
}
```

### DSMTypeXArray

Corresponds to the definition of a `xarray<elementType>`.

```java
public class DSMTypeXArray extends DSMType {
    public DSMType elementType;
}
```

### DSMFunctionPool

Corresponds to the definition of a `function_pool`.

```java
public class DSMFunctionPool {
    public UUID uuid;
    public String name;
    public ArrayList<DSMFunction> functions;
    public String documentation;
}

public class DSMFunction {
    public DSMFunctionPrototype prototype;
    public String documentation;
}

public class DSMFunctionPrototype {
    public String name;
    public ArrayList<DSMFunctionPrototypeParameter> parameters;
    public DSMType returnType;
}

public class DSMFunctionPrototypeParameter {
    public String name;
    public DSMType type;
}
```

### DSMAttachmentFunctionPool

Corresponds to the definition of an `attachment_function_pool`.

```java
public class DSMAttachmentFunctionPool {
    public UUID uuid;
    public String name;
    public ArrayList<DSMAttachmentFunction> functions;
    public String documentation;
}

public class DSMAttachmentFunction {
    public boolean isMutable;
    public DSMFunctionPrototype prototype;
    public String documentation;
}
```
