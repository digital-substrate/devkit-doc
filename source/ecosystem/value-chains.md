# Value Chains

Two value chains structure the dsviper ecosystem. **Toolchain** turns a data
model into runnable code; **Runtime** runs your application backed
by versioned, persistent storage. Each chain composes from independent
components — you can engage at any link without adopting the rest.

## The toolchain (code-generation side)

```
dsm  →  kibo  →  kibo-template-viper
```

**Goal.** Turn a data-model description into typed code that runs.

**dsm** — the modeling language. Standalone. Defines types, structures,
attachments, function pools. **No dependency on kibo, no dependency on
viper.** You can use dsm for spec-only purposes — sharing a typed data
contract between teams — without ever generating code from it.

**kibo** — the code generator. Reads a dsm model plus a template, emits code.
kibo itself is template-agnostic: the target language and runtime are
determined by the template you give it.

**kibo-template-viper** — the kibo template pack for the viper runtime
(Python via dsviper, Viper C++).

## The runtime (execution side)

The runtime has two paths. **Python** imports the Kibo-emitted Python
package and consumes it through **dsviper** (PyPI). **C++** links the
Kibo-emitted C++ surfaces directly against **Viper C++** (commercial).
What follows describes the Python path;
the C++ side mirrors it with Qt and AppKit component profiles.

```
dsviper  →  dsviper-components  →  Commit Application Model
```

**Goal.** Run a typed Python application with versioned, persistent data.

**dsviper** — the Python runtime. Strong-typed Python API over the Viper C++
engine. The foundation: type system, value system, commit DAG, database tier.
Distributed exclusively on PyPI (`pip install dsviper`) — not bundled in the
DevKit ZIP. Public test suite at
[`digital-substrate/dsviper-tests`](https://github.com/digital-substrate/dsviper-tests).

**dsviper-components** — reusable building blocks built on top of dsviper.
Consumed by applications. Comes in two parallel tracks: `dsviper-components`
(Qt Widgets) and `dsviper-components-qml` (Qt Quick / QML). Most of the
runtime stack mirrors this split.

**Commit Application Model** — the application pattern on top of the
Commit Engine. An Application Context composing a `CommitStore`, the
domain state, the dispatch surface, and a platform-agnostic notifier. See
[Commit Application Model](../commit-apps/model.md) for the pattern
itself; the walkthroughs that exercise the *whole* ecosystem
end-to-end (dsm, kibo, template, dsviper-components, runtime) are:

- `cdbe` — the Commit Database Editor.
- `ge-py` — Graph Editor, PySide6 desktop app (Qt Widgets).
- `ge-qml` — Graph Editor, PySide6 desktop app (Qt Quick / QML).
- `web-cdbe` — Flask web application, server-rendered HTML5.

## Services

A **Service** is a Viper C++ Runtime feature, hosted C++-side: it composes
DSM function-pool definitions (stateless `FunctionPool` and stateful
`AttachmentFunctionPool`) into an immutable bundle exposed as typed RPC
over a socket. Both `dsviper` (Python) and `Viper C++` can act as
clients. See [Services](../services/index.rst).

## Where the chains meet

The two chains meet at the **artifact**: the toolchain produces a typed
Python package; the runtime consumes it. See [pipeline](pipeline.md) for the
step-by-step view.

## Dependency rules

The arrows go one way. A change at a lower level can ripple up; a change at a
higher level cannot ripple down. Documentation, code, and tests for each
component must respect the same direction.

| Component                              | Depends on                  | Must not assume          |
|----------------------------------------|-----------------------------|--------------------------|
| dsm                                    | —                           | kibo, viper, dsviper     |
| kibo                                   | dsm                         | viper, dsviper           |
| kibo-template-viper                    | kibo, viper / dsviper       | applications             |
| dsviper-tools (Widgets and QML)        | dsm, dsviper                | applications             |
| dsviper                                | Viper C++                   | applications, components |
| dsviper-components (Widgets and QML)   | dsviper                     | applications             |
| Services                               | dsm, dsviper                | applications             |
| Commit Application Model (instances)   | dsviper, dsviper-components | —                        |

This table is the contract per-component documentation must respect: a `dsm`
page may not assume kibo is in the picture; a `kibo` page may assume dsm but
not viper; and so on.

## When you only need part of the chain

You do not have to adopt the whole stack. Common partial uses:

- **Just a data-model spec.** Share `.dsm` files between teams as a typed
  contract. No kibo, no viper involved.
- **Generated code for a non-viper runtime.** Use `kibo` with a different
  template; viper and dsviper are out of the picture.
- **Versioned data without code generation.** Use `dsviper`'s dynamic API
  directly, loading dsm definitions at runtime — no static package needed.
- **Inspect a database.** `dsviper-tools` (`cdbe`, `dbe`) 
  work standalone against any compatible database, regardless of
  whether you authored its schema in dsm yourself.
