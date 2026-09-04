# Remote Services

The client-side surface for consuming a Viper **Service** over the network. Every
class here is a `ServiceRemote*` type: the handle returned by `ServiceRemote.connect`
and the pool / function objects introspected from it.

The single entry point is {js:meth}`ServiceRemote.connect` — everything else is
discovered at runtime from the DSM the service embeds. The same handle connects to
*any* Viper service with no per-service codegen. For *what* a service is, the two
pool kinds, and the server side, see {doc}`/services/index`.

**When to use**: reach for this family when a Viper service already runs somewhere
and this process is its client. Nothing here starts a service.

```{note}
The server side (`Viper::Service`, `Viper::ServiceServer`) is C++ only — it is not
part of `@digitalsubstrate/dsviper`. Node is a **client** of Viper services.
```

## Quick Start

Connect, then dispatch by pool name and function name. No service-specific import:

```js
const { Definitions, ServiceRemote } = require('@digitalsubstrate/dsviper');

const defs = new Definitions();
const s = ServiceRemote.connect('localhost', '54328', defs);

// Resolve a function by pool name + function name, then call it.
const add = s.functionPoolFunc('Tools', 'add');
add.call(32, 10);                      // 42

s.close();
```

`functionPoolFunc()` resolves one function; `functionPools()` enumerates them all,
each pool answering `name()`, `documentation()` and `functions()`. That is enough to
walk a service whose schema this process has never seen — the pools carry the
documentation authored in the DSM.

```{tip}
Python's binding indexes a pool like a dictionary
(`s.function_pool_funcs("Tools")["add"](32, 10)`). JS has no equivalent on a native
handle, so the Node path is `functionPoolFunc(pool, name)` followed by `.call(…)`.
`dsviper-node-tools` ships `service_client.mjs`, which builds a `pools.Tools.add(…)`
comfort layer over exactly these calls — the same shape the Python REPL client has.
```

## Key classes

| Class | Purpose | Example |
|-------|---------|---------|
| {js:class}`ServiceRemote` | The connection to a service, and the root of what it exposes |
| {js:class}`ServiceRemoteFunctionPool` | One stateless pool on a connected service |
| {js:class}`ServiceRemoteFunction` | A resolved callable, obtained from a pool and a function name |
| {js:class}`ServiceRemoteAttachmentFunctionPool` | One stateful pool on a connected service |

The mirror of this page for the Python binding is {doc}`../../dsviper-python/api/services`.

## Connection

```{js-summary}
ServiceRemote
```

## Stateless Pools

```{js-summary}
ServiceRemoteFunctionPool
ServiceRemoteFunctionPoolFunctions
ServiceRemoteFunctionPoolFunction
ServiceRemoteFunction
```

## Stateful Pools

```{js-summary}
ServiceRemoteAttachmentFunctionPool
ServiceRemoteAttachmentFunctionPoolFunctions
ServiceRemoteAttachmentFunctionPoolFunction
ServiceRemoteAttachmentFunction
```

## Reference

```{js:autoclass} ServiceRemote
:members:
```

```{js:autoclass} ServiceRemoteFunctionPool
:members:
```

```{js:autoclass} ServiceRemoteFunctionPoolFunctions
:members:
```

```{js:autoclass} ServiceRemoteFunctionPoolFunction
:members:
```

```{js:autoclass} ServiceRemoteFunction
:members:
```

```{js:autoclass} ServiceRemoteAttachmentFunctionPool
:members:
```

```{js:autoclass} ServiceRemoteAttachmentFunctionPoolFunctions
:members:
```

```{js:autoclass} ServiceRemoteAttachmentFunctionPoolFunction
:members:
```

```{js:autoclass} ServiceRemoteAttachmentFunction
:members:
```
