# The Pipeline

The simplest mental model of the dsviper toolchain is a three-step pipeline.
You **describe** your data model in DSM, **generate** typed code with Kibo,
then **use** that code through dsviper at runtime.

This page is the happy path. For the full structural view — including
components, reference apps, and dsviper-tools — see
[value-chains](value-chains.md).

```
   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
   │  Describe   │ ───→ │  Generate   │ ───→ │     Use     │
   │     DSM     │      │    Kibo     │      │ Viper/dsviper│
   └─────────────┘      └─────────────┘      └─────────────┘
       .dsm file       typed C++/Python      typed runtime
                            surfaces
```

## 1. Describe — DSM

You author your data model in **DSM**, a small declarative language. The
artifact is a plain `.dsm` text file: types, structures, attachments, function
pools. No tooling lock-in — any editor works, with optional VS Code and
JetBrains plugins for syntax highlighting.

**What you have at the end of this step.** A typed *contract* for your data,
ready to be consumed by code generation, by introspection, or just shared
across teams as a spec.

→ Reference: {doc}`../dsm/index`.

## 2. Generate — Kibo

You feed your `.dsm` file plus a Kibo **template** to the `kibo` CLI. Kibo is
the code generator; the template determines the target language and runtime.
For the Viper / dsviper world, that template is `kibo-template-viper`, which
emits two parallel surfaces from a single DSM model: C++ headers and
implementations for Viper, and a typed Python package for dsviper.

**What you have at the end of this step.** Two typed surfaces of your DSM
model — a **C++ surface** (headers + `.cpp`) for embedding in Viper, and a
typed **Python package** importable from any Python application. Both are
generated from the same metadata.

(Other Kibo templates exist for other runtimes; Kibo itself is not
viper-specific.)

→ Reference: {doc}`../kibo/usage`.

## 3. Use — Viper or dsviper

Two paths, one model:

- **Python** — import the generated package and use it through the
  **dsviper** runtime (`pip install dsviper`).
- **C++** — link the generated headers and implementations against the
  **Viper** runtime (commercial license, NDA required — see
  {doc}`naming` for distribution).

Both paths share the same metadata that drove generation, so type checking,
serialization, persistence, the commit DAG, and remote synchronization
behave identically across surfaces. Your data is strongly typed end-to-end;
type mismatches raise exceptions immediately rather than silently corrupting
state.

**What you have at the end of this step.** A running, typed application
backed by versioned, persistent storage — without writing the type system,
serialization layer, or version control yourself.

→ Reference: {doc}`../dsviper/index` (Python),
{doc}`naming` (Viper distribution).

When you need the structural view — components, dependency rules, partial
uses — see [value-chains](value-chains.md).
