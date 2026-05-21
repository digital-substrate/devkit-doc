# Templated Features

The catalogue of templated features shipped with `kibo-template-viper` —
what each one does, in C++ and in Python. Use this page to pick the
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
| `Fuzz`    | Random value generation                          |
| `Test`    | Unit tests for fuzzing, JSON, streaming, storing |
| `TestApp` | Test application entry points                    |

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
templates += ['Fuzz', 'Test', 'TestApp']
```

For invocation patterns, see [Kibo usage](../kibo/usage.md).
