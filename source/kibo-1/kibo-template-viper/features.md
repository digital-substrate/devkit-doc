# Templated Features

The catalogue of templated features shipped with `kibo-template-viper` —
what each one does, in C++, Python, and TypeScript. Use this page to pick the
features you need; pass each to Kibo via the `-t` flag (see the
[Kibo usage guide](../kibo/usage.md)).

## C++ Templates

Templates in `templates/cpp/` are organised by theme:

### Core Types

| Feature | Purpose                                              |
|---------|------------------------------------------------------|
| `Data`  | Type implementations for enum, struct, concept, club |
| `Model` | Definitions, paths, fields                           |

### Persistence

| Feature       | Purpose                  |
|---------------|--------------------------|
| `Attachments` | Attachment accessors     |
| `Database`    | SQLite persistence layer |

### Serialization

| Feature       | Purpose                                            |
|---------------|----------------------------------------------------|
| `Stream`      | Binary encoder / decoder                           |
| `Json`        | JSON encoder / decoder                             |
| `ValueCodec`  | Bridge between static C++ and dynamic Viper C++ values |
| `ValueHasher` | Content hashing for values                         |
| `ValueType`   | Viper C++ type mappings                                |

### Function Pools

| Feature                              | Purpose                      |
|--------------------------------------|------------------------------|
| `FunctionPool`                       | Pure function bindings       |
| `FunctionPoolRemote`                 | Remote function call API     |
| `AttachmentFunctionPool`             | Stateful function bindings   |
| `AttachmentFunctionPoolRemote`       | Remote stateful calls        |
| `AttachmentFunctionPool_Attachments` | Pool exposing attachment API |

### Python Integration (C++ side)

| Feature  | Purpose                                     |
|----------|---------------------------------------------|
| `Python` | Python module constants for types and paths |

### Testing

| Feature   | Purpose                                          |
|-----------|--------------------------------------------------|
| `Test`    | Unit tests for fuzzing, JSON, streaming, storing — including the seedable fuzz harness |
| `TestApp` | Test application entry points (each accepts `--seed` for reproducible fuzz runs) |

## Python Templates

Templates in `templates/python/package/`. All Python features are emitted
as a single Python package — **typed proxy classes (with type hints) that
delegate to the `dsviper` runtime**. No C bindings, no extension module:
pure Python on top of `dsviper`'s dynamic API.

| Feature                                    | Purpose                                        |
|--------------------------------------------|------------------------------------------------|
| `package/__init__.py`                      | Package initialization                         |
| `package/definitions`                      | Type definitions for Viper C++                     |
| `package/data`                             | Classes for concepts, clubs, enums, structures |
| `package/attachments`                      | Typed attachment proxies (over `dsviper`)      |
| `package/database_attachments`             | Typed database-attachment proxies              |
| `package/path`                             | Field path constants                           |
| `package/value_type`                       | Dynamic type definitions                       |
| `package/function_pools`                   | Typed function-pool proxies                    |
| `package/attachment_function_pools`        | Typed stateful-pool proxies                    |
| `package/function_pool_remotes`            | Typed remote-call proxies                      |
| `package/attachment_function_pool_remotes` | Typed remote stateful-call proxies             |
| `wheel/pyproject.toml`                     | Minimal `pyproject.toml` to build a wheel      |

## TypeScript Templates

Templates in `templates/typescript/`. Emitted as a single npm package —
**typed TypeScript classes that delegate to the
`@digitalsubstrate/dsviper` Node binding**. The TypeScript analogue of the
Python package: the same model-shaped surface and the same Dual Reality
split, over the Node runtime instead of CPython.

One difference from the Python pack: a Node back-end consumes services as a
remote client only, so the TypeScript surface ships the remote function-pool
clients (`function_pool_remotes.ts`, `attachment_function_pool_remotes.ts`)
but not the local pools (`function_pools`, `attachment_function_pools`).

| Feature                                 | Purpose                                          |
|-----------------------------------------|--------------------------------------------------|
| `index.ts`                              | Package entry point — re-exports `data`          |
| `definitions.ts`                        | DSM type definitions                             |
| `data.ts`                               | Classes for concepts, clubs, enums, structures   |
| `attachments.ts`                        | Typed attachment proxies (over the Node binding) |
| `database_attachments.ts`               | Typed database-attachment proxies                |
| `path.ts`                               | Field path constants                             |
| `value_type.ts`                         | Dynamic type definitions                         |
| `function_pool_remotes.ts`              | Typed remote-call clients (over `ServiceRemote`) |
| `attachment_function_pool_remotes.ts`   | Typed remote stateful-call clients               |
| `project/package.json`                  | Minimal `package.json` to publish an npm package |
| `project/tsconfig.json`                 | TypeScript compiler configuration for the package |

```{note}
Unlike the Python package, the TypeScript surface ships **only the remote**
function-pool clients. The Node binding reaches function pools over
`ServiceRemote`, so there is no local (`function_pools` /
`attachment_function_pools`) variant.
```

## Picking a feature set

You don't need every feature. Common selections by use case:

```python
# Minimal — types only
templates = ['Data']

# Persistence (typed data on disk)
templates = ['Model', 'Data', 'Attachments', 'Database']

# Full stack — types + persistence + serialization + RPC
templates = [
    'Model', 'Data',
    'Stream', 'Json',
    'Attachments', 'Database',
    'ValueType', 'ValueCodec', 'ValueHasher',
    'FunctionPool', 'AttachmentFunctionPool',
]

# With testing
templates += ['Test', 'TestApp']
```

For invocation patterns, see [Kibo usage](../kibo/usage.md).
