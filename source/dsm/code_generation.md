# Code Generation

Kibo generates application infrastructure from DSM definitions. The developer
focuses on business logic while Kibo handles repetitive plumbing.

## Why Generate Code?

### The Amplification Effect

For every line of DSM, Kibo generates approximately 57 lines of C++ and Python:

| Project                    | DSM Lines | Generated Lines | Ratio |
|----------------------------|-----------|-----------------|-------|
| Graph Editor (Pilot)       | 273       | 15,592          | 57x   |
| Raptor Editor (Industrial) | 2,003     | 126,182         | 63x   |

### What Gets Generated vs What You Write

| Category            | Who Writes It | Examples                              |
|---------------------|---------------|---------------------------------------|
| **DSM definitions** | Developer     | `Graph.dsm`, `Pool_ModelGraph.dsm`    |
| **Infrastructure**  | Kibo          | Serialization, persistence, accessors |
| **Business logic**  | Developer     | Domain rules, algorithms, UI          |

The generated infrastructure handles:

- Type-safe data structures
- Attachment accessors (get/set/keys via abstract interfaces)
- Database persistence layer
- Binary and JSON serialization
- Python proxies with type hints
- RPC marshalling

## Dual Reality

Generated code is an adapter over Viper's dynamic runtime: the developer
writes idiomatic C++ / Python against typed classes; the runtime
sees metadata-driven values underneath. See
{term}`Dual Reality` in the glossary.

## Generated Layers

Kibo (with `kibo-template-viper`) emits, per DSM file:

- **Data** — concept keys, struct classes, enums
- **Attachments** — accessors over `AttachmentGetting` / `AttachmentMutating`
- **Database** — persistence layer
- **Serialization** — binary, JSON, and Viper Value converters
- **Function Pools** — marshalling stubs (in-process and RPC)
- **Python package** — typed proxies over the above

For the Bridge pattern that connects generated pool stubs to hand-written
business logic, see [Architecture — Layer 3: Bridges](architecture.md#layer-3-bridges).
