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
| `ValueCodec`  | Bridge between static C++ and dynamic Viper values |
| `ValueHasher` | Content hashing for values                         |
| `ValueType`   | Viper type mappings                                |

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
as a single Python package:

| Feature                                    | Purpose                                        |
|--------------------------------------------|------------------------------------------------|
| `package/__init__.py`                      | Package initialization                         |
| `package/definitions`                      | Type definitions for Viper                     |
| `package/data`                             | Classes for concepts, clubs, enums, structures |
| `package/attachments`                      | Attachment API wrappers                        |
| `package/database_attachments`             | Database attachment API wrappers               |
| `package/path`                             | Field path constants                           |
| `package/value_type`                       | Dynamic type definitions                       |
| `package/function_pools`                   | Function pool wrappers                         |
| `package/attachment_function_pools`        | Stateful pool wrappers                         |
| `package/function_pool_remotes`            | Remote function call wrappers                  |
| `package/attachment_function_pool_remotes` | Remote stateful call wrappers                  |
| `wheel/pyproject.toml`                     | Minimal `pyproject.toml` to build a wheel      |

## Picking a feature set

You don't need every feature. Common selections by use case:

```python
# Minimal — types only
templates = ['Data']

# Persistence (versioned data on disk)
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
