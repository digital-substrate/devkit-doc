# The Pipeline: Describe → Generate → Use

The simplest mental model of the dsviper toolchain is a three-step pipeline.
You **describe** your data model in DSM, **generate** typed code with Kibo,
then **use** that code through dsviper at runtime.

This page is the happy path. For the full structural view — including
components, reference apps, and dsviper-tools — see
[value-chains](value-chains.md).

```
   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
   │  Describe   │ ───→ │  Generate   │ ───→ │     Use     │
   │     DSM     │      │    Kibo     │      │   dsviper   │
   └─────────────┘      └─────────────┘      └─────────────┘
       .dsm file        typed Python package    typed runtime
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
For the dsviper world, that template is `kibo-template-viper`, which emits a
Python package wired for the dsviper runtime.

**What you have at the end of this step.** A typed Python package — classes,
functions, type hints — that mirrors your DSM model. Importable from any
Python application.

(Other Kibo templates exist for other runtimes; Kibo itself is not
viper-specific.)

→ Reference: {doc}`../kibo/usage`.

## 3. Use — dsviper

You import the generated package into your application and use it through the
**dsviper** runtime. Your data is strongly typed end-to-end: type mismatches
raise exceptions immediately rather than silently corrupting state. The same
metadata that drove generation now drives serialization, persistence, the
commit DAG, and remote synchronization.

**What you have at the end of this step.** A running, typed application backed
by versioned, persistent storage — without writing the type system,
serialization layer, or version control yourself.

→ Reference: {doc}`../dsviper/index`.

When you need the structural view — components, dependency rules, partial
uses — see [value-chains](value-chains.md).
