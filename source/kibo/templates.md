# Templates

A **templated feature** — or "template" for short — is a parameterised code
recipe that Kibo expands against a DSM model to produce source code.

```text
DSM Model + Template → Generated Code
```

A template is, in practice, a giant code snippet (a set of StringTemplate
`.stg` files) where the DSM definitions are injected and recursively
consumed. As Kibo walks the model, it emits the snippet for every type,
attachment, function pool, etc., that the template targets. The result is
repetitive, schema-shaped code that you would otherwise hand-write.

## What templates know about DSM

Kibo carries the mapping from DSM types to each target: the native spelling of a primitive and
of a container for C++, and, for a target that reaches the runtime through a binding (Python,
TypeScript), how that binding spells the same type — `int64` is `int` in Python and `bigint`
in TypeScript. A template reads these spellings from the model rather than re-implementing
them; the [Template Model reference](template_model.md) lists what it reads.

## Templates form an ecosystem

A template pack groups its templates into features, and a feature can require others. In the
[viper template pack](../kibo-template-viper/index.rst), the C++ `Attachments` feature requires
`Base` and `Fields`: you don't render `Attachments` in isolation. The pack declares these
dependencies in its `features.json`, and [kibo-project](kibo-project.md) expands a project's
choice into the templates it needs; kibo itself renders whatever template it is given.

This dependency structure is why selecting features is a real choice: you pick the minimal set
that covers your needs, and the dependencies follow. See
[Picking a feature set](../kibo-template-viper/features.md#picking-a-feature-set) for common
selections by use case.

## Two ways to encounter templates

* **Use an existing template pack** — for the Viper world, that
  pack is [kibo-template-viper](../kibo-template-viper/index.rst), which
  ships C++, Python, and TypeScript templates for every layer of the stack.
* **Write your own** — Kibo's template format is generic. You can build a
  template targeting any language or runtime. See
  [Template Model Reference](template_model.md) for the type-suffix
  mechanism, naming conventions, and complete reference.
