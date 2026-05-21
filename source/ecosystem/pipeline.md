# The Pipeline

The simplest mental model of the dsviper toolchain is a three-step pipeline.
You **describe** your data model in DSM, **generate** code with Kibo,
then **use** that code through Viper C++ or dsviper at runtime.

```
   ┌────────────┐      ┌────────────┐      ┌───────────────────┐
   │  Describe  │ ───→ │  Generate  │ ───→ │      Use          │
   │    DSM     │      │    Kibo    │      │ Viper C++/dsviper │
   └────────────┘      └────────────┘      └───────────────────┘
       .dsm file         C++/Python               runtime
                          surfaces
```

## 1. Describe — DSM

You author your data model in **DSM**, a small declarative language. The
artifact is a plain `.dsm` text file: types, structures, attachments, function
pools. VS Code and JetBrains plugins provide syntax highlighting.

**What you have at the end of this step.** A typed *contract* for your data,
ready to be consumed by code generation, by introspection, or just shared
across teams as a spec.

→ Reference: {doc}`../dsm/index`.

## 2. Generate — Kibo

You feed your `.dsm` file plus a Kibo **template** to the `kibo` CLI. Kibo is
the code generator; the template pack determines the runtime.
For the Viper C++ / dsviper world, that template pack is `kibo-template-viper`, which
can emits two parallel surfaces from a single DSM model: C++ headers and
implementations for Viper C++, and a typed Python package for dsviper.

**What you have at the end of this step.** Two typed surfaces of your DSM
model — a **C++ surface** (headers + `.cpp`) for embedding in Viper C++, and a
typed **Python package** importable from any Python application. Both are
generated from the same metadata.

→ Reference: {doc}`../kibo/usage`.

## 3. Use — Viper C++ or dsviper

Two paths, one model:

- **Python** — import the generated package and use it through the
  **dsviper** runtime (`pip install dsviper`).
- **C++** — link the generated headers and implementations against the
  **Viper C++** runtime (commercial).

Both paths share the same metadata that drove generation, so type checking,
serialization, persistence, the mutation DAG, and remote synchronization
behave identically across surfaces. Your data is strongly typed end-to-end;
type mismatches raise exceptions immediately rather than silently coercing
values.

→ Reference: {doc}`../dsviper/index` (Python).

When you need the structural view — components, dependency rules, partial
uses — see [value-chains](value-chains.md).
