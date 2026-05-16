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

Kibo carries a built-in mapping from DSM primitives to the target's native
types: ``bool``, ``int8``, ``float``, … and from generic DSM collections
(``vector<T>``, ``map<K, V>``, …) to the target language's standard
containers and to the Viper C++ type-and-value system. Authors of templates
build on top of this mapping rather than re-implementing it.

## Templates form an ecosystem

Templates can depend on other templates. They form a small ecosystem where
features compose. For example, in the
[viper template pack](../kibo-template-viper/index.rst), the ``Database``
feature depends on ``Attachments`` and ``Model``: you don't activate
``Database`` in isolation.

This dependency structure is why "selecting features" is a real choice:
you pick the minimal set that covers your needs, and Kibo expands the
graph of dependencies for you. See
[Picking a feature set](../kibo-template-viper/features.md#picking-a-feature-set)
for common selections by use case.

## Two ways to encounter templates

* **Use an existing template pack** — for the dsviper / Viper C++ world, that
  pack is [kibo-template-viper](../kibo-template-viper/index.rst), which
  ships C++ and Python templates for every layer of the stack.
* **Write your own** — Kibo's template format is generic. You can build a
  template targeting any language or runtime. See
  [Template Model Reference](template_model.md) for the type-suffix
  mechanism, naming conventions, and complete reference.
