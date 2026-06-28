# dsviper for Node.js

The `@digitalsubstrate/dsviper` **npm** package is a native Node.js binding over
the same Viper C++ 1.2 runtime that backs the Python `dsviper`. It ships as
prebuilt binaries (`prebuilds/<platform>-<arch>/`), built with `node-addon-api`
and `cmake-js`, and requires Node 16+.

The two distributions share a runtime but not a package name: `pip install
dsviper` gives you the Python runtime; `npm install @digitalsubstrate/dsviper`
gives you the Node binding. Both drive the same Viper C++ engine and the same
on-disk format.

```{note}
`dsviper` is distributed under the Digital Substrate Commercial License 1.2,
which grants a free **Evaluation License** for assessment and training, and a
paid **Commercial License** by written agreement. See [License](../legal/license.md)
before any commercial use.
```

## Place in the ecosystem

- **Depends on** — {term}`Viper C++`.
- **Sibling of** — the Python {doc}`dsviper <../dsviper/index>` runtime: a second
  binding over the same engine, not a replacement.
- **Distribution** — the `@digitalsubstrate/dsviper` npm package
  (`npm install @digitalsubstrate/dsviper`), shipped as prebuilt native
  binaries. Like the Python `dsviper`, it is not bundled in the DevKit ZIP.

## Two ways to work

As with the Python runtime, there are two ways to reach the engine:

- **Dynamic API** — load definitions at runtime and work through the runtime
  type system, value system, and commit tier (`Type*`, `Value*`, `Definitions`,
  `CommitMutableState`, `Attachment*`). These are the **same class names**
  documented for Python under {doc}`../dsviper/dsm` and
  {doc}`../dsviper/serialization`. This path is available today and is what the
  pages in this section cover.
- **Static TS API** — typed TypeScript packages generated from a DSM model by
  Kibo, using the `kibo-template-viper` TypeScript templates (the Node analogue
  of the Python static path). The generated surface is catalogued under
  {doc}`../kibo-template-viper/features`; this section documents the dynamic API
  only.

## Value semantics: Java-like, not Pythonic

The Node surface corresponds to the Python type stub **without the function
pools and without Python's `__dunder__` methods**. Where Python overloads
operators, Node exposes **explicit, Java-like methods** — `equals`, `hash`,
`compare` are the value contract. When porting a Python snippet, translate
through this table:

| Python (dunder / builtin) | Node (explicit method) |
|---|---|
| `a == b`            (`__eq__`)            | `a.equals(b)` |
| `a < b`, `a > b`, … (`__lt__` / `__gt__`) | `a.compare(b)` — three-way, returns a number |
| `hash(a)`           (`__hash__`)          | `a.hash()` |
| `str(a)` / `repr(a)` (`__str__` / `__repr__`) | `a.toString()` / `a.representation()` |
| `for x in v`        (`__iter__`)          | iterable — `[...v]`, or the iterator class |
| `v[i]`              (`__getitem__`)       | `v.at(i)` / `v.get(k)` |
| `v[i] = x`          (`__setitem__`)       | `v.set(i, x)` |
| `k in m`            (`__contains__`)      | `m.has(k)` / `m.contains(x)` |
| `len(v)`            (`__len__`)           | `v.size()` |

`equals` and `compare` **seamlessly coerce a native argument**, so you rarely
wrap by hand: `new ValueDouble(2).equals(2)` is `true` and
`new ValueDouble(1).compare(2) < 0`. Comparing two values of incompatible types
throws (`compare`) or returns `false` (`equals`) rather than guessing.

```{warning}
JavaScript `==` does **not** call `equals`. Between two values it is reference
equality — `a == b` is `false` even when they hold the same value, so always use
`.equals`. (Against a primitive, `a == 3.0`, `+a`, and `` `${a}` `` do work, via
`Symbol.toPrimitive`.)
```

## Verified examples

Every page in this section draws its examples from the public
`dsviper-node-tests` suite — the Node twin of the Python
[`dsviper-tests`](https://github.com/digital-substrate/dsviper-tests). That repo
is the canonical place to read working, runtime-verified Node usage, for humans
and agents alike.

## API reference

The complete Node class reference is generated from the package's TypeScript
declarations (`index.d.ts`) and mirrors the dynamic-API classes documented for
Python. Because operations are named methods here rather than dunders, methods
such as `equals`, `compare`, `hash`, and `toString` appear as first-class,
documented entries — more explicit than their Python operator-overload
equivalents.

The declarations carry doc comments mirrored from the Python stub, so the
generated reference is prose-rich and stays in step with the Python API
documentation by construction. The one systematic gap is the dunder-replacement
methods themselves — `equals`, `compare`, `hash` — which have no source
docstring to extract, because their Python origins are operator dunders
(`__eq__`, `__lt__`, `__hash__`) that carry none. Those few are worth a
hand-written line on the relevant pages.

The full generated reference is in {doc}`api/index`.

## Topics

```{toctree}
:maxdepth: 2

installation
hello
types_values
collections
structures
errors
dsm
database
blobs
serialization
```
