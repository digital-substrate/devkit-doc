# Names and validity

A DSM model describes data, independently of any programming language. What makes a model
valid is the DSM's own rules, written down in the standard's
[governance](https://github.com/digital-substrate/dsm/blob/main/spec/dsm-governance.md) and
held by the tests of the runtime. In short:

| Rule | |
|---|---|
| **Identifiers** | an ASCII letter, then ASCII letters, digits and underscores: `[A-Za-z][A-Za-z0-9_]*` |
| **DSM keywords** | `struct`, `concept`, `club`, `enum`, `namespace`, `membership`, `mutable`, `function_pool`, `attachment_function_pool`, `true`, `false` are not names |
| **Type names** | a concept, club, enumeration or structure cannot take the name of a built-in type — `int64`, `uuid`, `string`, `blob_id`, `any`… — which an unqualified reference would read as the built-in one; a field, a namespace or an attachment may |
| **Uniqueness** | the types of a namespace share one space; a namespace keeps its UUID; fields, cases, functions, parameters and pools are unique where they meet; an attachment is unique by its key type and name within a namespace |
| **Documentation** | UTF-8 text without `"""`; it may begin or end with a quote |

## A word a language reserves is a name

`class`, `def`, `function`, `this` are valid names in a model: the DSM does not know the
languages it is generated into. Whether such a name works in generated code is the
target's business, at generation:

- **C++** refuses invalid code at compilation, and says where. A field named `class`
  does not compile in C++.
- **Python and TypeScript** are silent: a name can produce code that imports or runs and
  does something else — a field masking a method of the generated class. So
  [kibo-project](../kibo/kibo-project.md) validates the generated Python and TypeScript after
  each generation, as the template pack declares: Python is imported, every structure built,
  and checked with `mypy --strict`; TypeScript is checked with `tsc`.
- A model's name meeting a name the template pack's own code takes — a field `wrap_value`
  beside the method every generated class has — is refused at generation, saying so.

In every case the project corrects, for that target only, and the model stays as it is:

```toml
[names.cpp.rename]
class = "klass"
```

The DSM name stays the one sent to the runtime, so the targets still meet on the wire. Nothing
is renamed without such a line.
