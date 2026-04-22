# Services and RPC

This document explains the service architecture for distributed Viper applications.

## Overview

Viper provides a complete RPC (Remote Procedure Call) system for distributed applications:

- **FunctionPool**: Named container of callable functions
- **Service**: Central aggregator of Definitions and FunctionPools
- **RPC**: Protocol for remote function execution
- **Transparent Remote Access**: Local and remote interfaces are identical

---

## Service Architecture

```
+---------------------------------------------------------------+
|                          Client                               |
|  +-------------------+                                        |
|  |   ServiceRemote   |  <-- Same interface as local Service   |
|  +-------------------+                                        |
|           |                                                   |
|           |  RPC (TCP/IP)                                     |
|           v                                                   |
+---------------------------------------------------------------+
|                          Server                               |
|  +-------------------+                                        |
|  |      Service      |  <-- Aggregates FunctionPools          |
|  +-------------------+                                        |
|           |                                                   |
|  +-------------------+                                        |
|  |   FunctionPool    |  <-- Named container of Functions      |
|  +-------------------+                                        |
+---------------------------------------------------------------+
```

---

## Function System

### Function

Abstract callable with typed prototype:

```cpp
class Function {
public:
    std::shared_ptr<FunctionPrototype> const prototype;  // Public const member
    std::string const documentation;

    std::shared_ptr<Value> call(std::vector<std::shared_ptr<Value>> const & args) const;
};
```

### FunctionPrototype

Encodes the function signature:

| Field      | Type                      | Description             |
|------------|---------------------------|-------------------------|
| name       | string                    | Function name           |
| parameters | vector<FunctionParameter> | Parameter names + types |
| returnType | shared_ptr<Type>          | Return type             |

### FunctionLambda

Concrete implementation wrapping a C++ lambda:

```cpp
auto addFunc = FunctionLambda::make(
    {TypeInt32::Instance(), TypeInt32::Instance()},  // Parameter types
    TypeInt32::Instance(),                            // Return type
    [](std::vector<std::shared_ptr<Value>> const & args) -> std::shared_ptr<Value> {
        auto a = ValueInt32::cast(args[0])->value;
        auto b = ValueInt32::cast(args[1])->value;
        return ValueInt32::make(a + b);
    }
);
```

### FunctionPool

Named container of Functions:

```cpp
auto pool = FunctionPool::make(poolUUId, "MathPool");
pool->add(addFunc);
pool->add(multiplyFunc);

// Lookup (check throws if not found, query returns nullptr)
auto func = pool->check("add");   // Throws if not found
auto func2 = pool->query("mul");  // Returns nullptr if not found
```

---

## Service

Central aggregator providing:

| Component               | Purpose                                  |
|-------------------------|------------------------------------------|
| Definitions             | Type registry for RPC type compatibility |
| FunctionPools           | Container of function pools              |
| AttachmentFunctionPools | Function pools with attachment context   |

```cpp
// Service is created with definitions and pools
auto service = Service::make(definitions, {mathPool, cameraPool}, {});

// Access pools by UUID
auto pool = service->checkFunctionPool(mathPoolUUId);
auto func = pool->check("add");
auto result = func->call({ValueInt32::make(2), ValueInt32::make(3)});
```

---

## RPC Protocol

### Packet Structure

```
+----------------+------------------+
|    UUID (16)   |    Payload       |
+----------------+------------------+
     |                  |
     |                  +-- Encoded function call / return
     +-- Packet type identifier
```

### Packet Types

| Category     | Packet Types                                |
|--------------|---------------------------------------------|
| **Call**     | CallService, CallFunction                   |
| **Return**   | ReturnValue, ReturnVoid, ReturnError        |
| **Database** | DatabaseKeys, DatabaseGet, DatabaseSet, ... |
| **Commit**   | CommitIds, CommitCreate, CommitMerge, ...   |
| **Blob**     | BlobCreate, BlobGet, BlobStream, ...        |

### RPC Connection

Orchestrates the call/return cycle:

```cpp
auto connection = RPCConnection::make(socket, codec);

// Client side: call remote function
auto result = connection->call(packet);

// Server side: handle incoming call
auto request = connection->receive();
auto response = service->handle(request);
connection->send(response);
```

---

## Transparent Remote Access

Local and remote services share similar patterns:

```cpp
// Local service
auto service = Service::make(definitions, {mathPool}, {});
auto pool = service->checkFunctionPool(mathPoolUUId);
auto func = pool->check("add");

// Remote service - similar access pattern
auto remote = ServiceRemote::make(connection);
auto remotePool = remote->checkFunctionPool(mathPoolUUId);
auto remoteFunc = remotePool->check("add");

// Both can be used identically
auto result = func->call({ValueInt32::make(2), ValueInt32::make(3)});
```

This enables:

- Same code for local and remote execution
- Easy testing with local mocks
- Transparent distribution

---

## Bidirectional Protocol

For `attachment_function_pool` functions, the RPC protocol is **bidirectional**:
remote execution with local mutation.

### How It Works

1. **Client** calls a function on the server (e.g. `newVertex`)
2. **Server** executes the business logic
3. When server code calls `mutating->set(...)`, the `mutating` parameter is actually an
   `AttachmentMutatingRemote` — a proxy that sends the mutation **back to the client**
   via RPC callback
4. **Client** receives the callback and applies the mutation to its local
   `CommitMutableState`
5. Client decides when to `commit_mutations()` — the server only interacts through the
   `AttachmentMutating` interface

```
+-----------------------------------------------------------+
|                   Client (Python/C++)                     |
|  CommitMutableState (LOCAL)                               |
|  All mutations accumulate here                            |
+-------------------------------+---------------------------+
|          RPC Layer            |                           |
|  1. CallFunction  ----------->|                           |
|  4. <--- Callback packets     |  AttachmentGetting*       |
|          (Set, Update, Diff,  |  AttachmentMutating*      |
|           UnionInSet, ...)    |                           |
+-------------------------------+---------------------------+
|                   Server (C++)                            |
|  AttachmentFunctionPool                                   |
|  + AttachmentMutatingRemote (proxy back to client)        |
+-----------------------------------------------------------+
```

### Key Properties

| Property             | Guarantee                                          |
|----------------------|----------------------------------------------------|
| **Remote execution** | Business logic runs on the server                  |
| **Local mutation**   | All mutations apply to client's CommitMutableState |
| **Client control**   | Only the client can trigger `commit_mutations()`   |
| **Server stateless** | Server only sees the `AttachmentMutating` proxy    |
| **Isolation**        | Mutations are in-memory only until commit          |

### AttachmentMutatingRemote

`AttachmentMutatingRemote` is the server-side proxy that implements the
`AttachmentMutating`
interface. Each method call (`set`, `update`, `diff`, `unionInSet`, `insertInXArray`,
etc.)
is converted into an RPC callback packet sent back to the client.

The generated bridge code on the server is unaware of the proxy — it simply calls
`AttachmentMutating` methods, making `attachment_function_pool` functions
network-transparent.

---

## Attachment Function Integration

For functions that modify attachment state:

### AttachmentFunction

Abstract class with typed prototype:

```cpp
class AttachmentFunction {
public:
    std::shared_ptr<FunctionPrototype> const prototype;
    std::string const documentation;
};
```

### AttachmentFunctionPool

Container of AttachmentFunctions:

```cpp
auto pool = AttachmentFunctionPool::make(poolUUId, "CameraCommands");
pool->add(createCameraFunc);
pool->add(deleteCameraFunc);

auto func = pool->check("createCamera");  // Throws if not found
```

### Usage with CommitStore

```cpp
store.dispatchPool("Create Camera",       // label
                   attachmentFunctionPool,    // pool
                   "createCamera",        // function name
                   {name, position});     // args
```

---

## Database Remote Access

DatabaseRemote provides transparent remote database access:

```cpp
// Local database
auto db = Database::open(path);
db->set(attachment, key, document);

// Remote database - SAME INTERFACE
auto remote = DatabaseRemote::make(connection);
remote->set(attachment, key, document);
```

### Operations

| Operation | Description                    |
|-----------|--------------------------------|
| `keys()`  | Get all keys for an attachment |
| `has()`   | Check if document exists       |
| `get()`   | Read document                  |
| `set()`   | Write document                 |
| `del()`   | Delete document                |

---

## Commit Database Remote

CommitDatabaseRemote provides remote access to the Commit Engine:

```cpp
// Remote commit database
auto remote = CommitDatabaseRemote::make(connection);

// Same operations as local
auto state = remote->state(commitId);
auto doc = state->get(attachment, key);
```

---

## Definitions Synchronization

Before RPC, Definitions must be synchronized:

1. **Client connects**: Sends its reduced Definitions
2. **Server responds**: Sends its reduced Definitions
3. **Both merge**: Common type understanding established
4. **RPC proceeds**: Types verified via RuntimeId

This ensures type compatibility across network boundaries.

---

## See Also

- [Viper Architecture](viper_architecture.md) - Network layer
- [Code Generation](code_generation.md) - FunctionPool generation
- [Commit Patterns](commit_patterns.md) - CommitStore and dispatch patterns
