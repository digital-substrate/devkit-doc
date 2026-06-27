# Installation

This chapter covers installing and verifying the `dsviper` Node.js binding.

## Prerequisites

- Node 16+ (the binding targets the N-API ABI; the test suite uses Node 18+).
- npm (or any package manager that installs from the npm registry).

No C++ toolchain is required to consume the package: it ships **prebuilt native
binaries** (`prebuilds/<platform>-<arch>/`) and selects the right one for your
platform and architecture at load time.

## Installing from npm

```bash
npm install @digitalsubstrate/dsviper
```

```{note}
`dsviper` is distributed under the Digital Substrate Commercial License 1.2,
which grants a free **Evaluation License** for assessment and training, and a
paid **Commercial License** by written agreement. See [License](../legal/license.md)
before any commercial use.
```

## Importing the binding

The package is a native addon, so it is loaded with CommonJS `require`:

```js
const dsviper = require('@digitalsubstrate/dsviper');
const { Value, Type, ValueDouble, CommitDatabase } = dsviper;
```

From an ES module, a native addon is not statically analysable, so bind it
through `createRequire` rather than a named `import`:

```js
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const dsviper = require('@digitalsubstrate/dsviper');
```

## Verifying the install

A minimal round-trip — create a typed value and an in-memory database, then
close it:

```js
const { Value, Type, CommitDatabase } = require('@digitalsubstrate/dsviper');

const pi = Value.create(Type.DOUBLE, 3.14159);
console.log(pi.representation());   // "3.14159"

const db = CommitDatabase.createInMemory();
console.log(db.isClosed());         // false
db.close();
console.log(db.isClosed());         // true
```

If that runs without throwing, the binary loaded for your platform and the
runtime is reachable.

## TypeScript

The package ships `index.d.ts`, so types resolve automatically — no
`@types/dsviper` to install. Strict-mode projects work out of the box.
