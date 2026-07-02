# npm Packages

Creating a distributable npm package from your DSM model — the TypeScript
analogue of {doc}`Python wheels <wheels>`, over the
`@digitalsubstrate/dsviper` Node binding instead of CPython.

## Quick Start

### Step 1: Generate

```bash
python3 tools/dsm_util.py create_node_package model.dsm
```

This creates a ready-to-build package in `model/`:

- TypeScript sources in `model/src/` (including the embedded definitions
  blob, `resources.ts`)
- `model/package.json` and `model/tsconfig.json`

Unlike `create_python_package`, there is no `--wheel` flag — `package.json`
and `tsconfig.json` are always emitted.

### Step 2: Review package.json

The generated manifest names the package after the DSM namespace, depends on
the Node binding, and builds with `tsc`:

```json
{
    "name": "model",
    "version": "1.0.0",
    "type": "module",
    "exports": {
        ".": {
            "types": "./dist/index.d.ts",
            "import": "./dist/index.js"
        }
    },
    "files": ["dist", "src"],
    "scripts": {
        "build": "tsc -p tsconfig.json"
    },
    "dependencies": {
        "@digitalsubstrate/dsviper": ">=1.2.1 <1.3.0"
    },
    "devDependencies": {
        "typescript": "^5.0.0"
    },
    "license": "UNLICENSED"
}
```

Adjust `name`, `version`, and `license` for your release; keep the
`@digitalsubstrate/dsviper` range aligned with the `1.2` runtime contract.

### Step 3: Build

```bash
cd model
npm install
npm run build
```

`npm run build` runs `tsc -p tsconfig.json`, compiling `src/` to `dist/`
(`.js` plus `.d.ts` declarations).

### Step 4: Distribute

Pack the package into a tarball:

```bash
npm pack
```

This creates `model-1.0.0.tgz` (the `files` entry ships `dist` and `src`).
Publish it to a private npm registry, or install the tarball directly in a
consuming application.

### Step 5: Use

```typescript
import { Tuto_UserKey, Tuto_Login } from "model";

const key = Tuto_UserKey.create();
```

The entry point re-exports the `data` classes at the package root; the other
surfaces are available as namespaces (`attachments`, `databaseAttachments`,
`path`, `types`, `definitions`, `functionPoolRemotes`,
`attachmentFunctionPoolRemotes`).

## Package Structure

After generation, before building:

```
model/
├── package.json
├── tsconfig.json
└── src/
    ├── index.ts                            # Entry point — re-exports data + namespaced modules
    ├── data.ts                             # Concept, struct, enum, key classes
    ├── value_type.ts                       # Dynamic type definitions
    ├── definitions.ts                      # DSM type definitions
    ├── path.ts                             # Field path constants
    ├── attachments.ts                      # Typed attachment proxies (over the Node binding)
    ├── database_attachments.ts             # Typed database-attachment proxies
    ├── function_pool_remotes.ts            # Typed remote-call clients (over ServiceRemote)
    ├── attachment_function_pool_remotes.ts # Typed remote stateful-call clients
    └── resources.ts                        # Embedded definitions (base64 blob)
```

`npm run build` adds a `dist/` directory holding the compiled `.js` and
`.d.ts` files.

A Node back-end consumes services as a remote client only, so the generated
surface ships the remote function-pool clients but not the local pools — see
{doc}`features` for the full template list.

## Distribution

### Private npm registry

```bash
npm publish --registry https://your-registry.example.com
```

### Consuming application

The package declares `@digitalsubstrate/dsviper` as a peer runtime
dependency; the consuming application installs it from npm alongside the
generated package:

```bash
npm install @digitalsubstrate/dsviper ./model-1.0.0.tgz
```

## Version Management

Bump the `version` field in `package.json` for each release; follow semver
against your DSM model surface.

## Embedded definitions

`create_node_package` writes the DSM definitions into `src/resources.ts` as a
base64 string:

```typescript
export const B64_DEFINITIONS = "…";
```

The bytes are the default `StreamTokenBinary` encoding — exactly what the Node
binding's `Definitions.decode(blob)` assumes when no codec is given, so
`definitions.ts` decodes the blob as-is. The blob is **not** compressed (the
Python package's `resources.py` zlib-compresses; the Node one does not).
