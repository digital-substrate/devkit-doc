# Templated Features

The catalogue of templated features shipped with `kibo-template-viper` —
what each one generates, in C++ and in Python. Use this page to pick the
features you need; pass each to Kibo via the `-t` flag (see the
[Kibo usage guide](../kibo/usage.md)).

## C++ Templates

Templates in `templates/cpp/` are organised by feature:

### Core Types

| Template | Generated Files         | Purpose                                              |
|----------|-------------------------|------------------------------------------------------|
| `Data`   | `*_Data.hpp/cpp`        | Type implementations for enum, struct, concept, club |
| `Model`  | `*_Definitions.hpp/cpp` | definitions, paths, fields                           |

### Persistence

| Template      | Generated Files         | Purpose                  |
|---------------|-------------------------|--------------------------|
| `Attachments` | `*_Attachments.hpp/cpp` | Attachment accessors     |
| `Database`    | `*_Database*.hpp/cpp`   | SQLite persistence layer |

### Serialization

| Template      | Generated Files                  | Purpose                                            |
|---------------|----------------------------------|----------------------------------------------------|
| `Stream`      | `*_Reader/Writer.hpp/cpp`        | Binary encoder / decoder                           |
| `Json`        | `*_JsonEncoder/Decoder.hpp/cpp`  | JSON encoder / decoder                             |
| `ValueCodec`  | `*_ValueEncoder/Decoder.hpp/cpp` | Bridge between static C++ and dynamic Viper values |
| `ValueHasher` | `*_ValueHasher.hpp/cpp`          | Content hashing for values                         |
| `ValueType`   | `*_ValueType.hpp/cpp`            | Viper type mappings                                |

### Function Pools

| Template                             | Generated Files                                 | Purpose                      |
|--------------------------------------|-------------------------------------------------|------------------------------|
| `FunctionPool`                       | `*_FunctionPools.hpp/cpp`                       | Pure function bindings       |
| `FunctionPoolRemote`                 | `*_FunctionPoolsRemote.hpp/cpp`                 | Remote function call API     |
| `AttachmentFunctionPool`             | `*_AttachmentFunctionPools.hpp/cpp`             | Stateful function bindings   |
| `AttachmentFunctionPoolRemote`       | `*_AttachmentFunctionPoolsRemote.hpp/cpp`       | Remote stateful calls        |
| `AttachmentFunctionPool_Attachments` | `*_AttachmentFunctionPools_Attachments.hpp/cpp` | Pool exposing attachment API |

### Python Integration (C++ side)

| Template | Generated Files    | Purpose                                     |
|----------|--------------------|---------------------------------------------|
| `Python` | `*_Python.hpp/cpp` | Python module constants for types and paths |

### Testing

| Template  | Generated Files   | Purpose                                          |
|-----------|-------------------|--------------------------------------------------|
| `Fuzz`    | `*_Fuzz.hpp/cpp`  | Random value generation                          |
| `Test`    | `*_Test*.hpp/cpp` | Unit tests for fuzzing, JSON, streaming, storing |
| `TestApp` | `*_TestApp.cpp`   | Test application entry points                    |

## Python Templates

Templates in `templates/python/package/`. All Python features are emitted
as a single Python package:

| Template                                   | Generated File                        | Purpose                                        |
|--------------------------------------------|---------------------------------------|------------------------------------------------|
| `package/__init__.py`                      | `__init__.py`                         | Package initialization                         |
| `package/definitions`                      | `definitions.py`                      | Type definitions for Viper                     |
| `package/data`                             | `data.py`                             | Classes for concepts, clubs, enums, structures |
| `package/attachments`                      | `attachments.py`                      | Attachment API wrappers                        |
| `package/database_attachments`             | `database_attachments.py`             | Database attachment API wrappers               |
| `package/path`                             | `path.py`                             | Field path constants                           |
| `package/value_type`                       | `value_type.py`                       | Dynamic type definitions                       |
| `package/function_pools`                   | `function_pools.py`                   | Function pool wrappers                         |
| `package/attachment_function_pools`        | `attachment_function_pools.py`        | Stateful pool wrappers                         |
| `package/function_pool_remotes`            | `function_pool_remotes.py`            | Remote function call wrappers                  |
| `package/attachment_function_pool_remotes` | `attachment_function_pool_remotes.py` | Remote stateful call wrappers                  |
| `wheel/pyproject.toml`                     | `pyproject.toml`                      | Minimal `pyproject.toml` to build a wheel      |

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
