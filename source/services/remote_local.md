# Remote-Local Protocol

For `AttachmentFunctionPool` calls, the Viper RPC layer implements a
pattern that is unusual but central to the design: **business logic
executes on the server, but state mutations happen on the client**.
The roles *invert* during execution.

When a stateful pool method runs server-side and needs to read or
mutate the client's `AttachmentMutating`, the server sends a callback
RPC back to the client. The client reads (or mutates) its
**client-local** `AttachmentMutating`, responds, and the server
continues.

```text
CLIENT                                         SERVER
   │                                              │
   │──► RPCPacketCallAttachmentFunction ─────────►│
   │    (pool: PlayerModel, func: create)         │
   │                                              │
   │                                        ┌─────┴─────┐
   │                                        │  Execute  │
   │                                        │  business │
   │                                        │   logic   │
   │                                        └─────┬─────┘
   │                                              │
   │◄── RPCPacketCallAttachmentGettingGet ◄───────│  ← ROLE INVERSION
   │    (server asks client to read)              │    Server CALLS
   │                                              │
   │    [Read from LOCAL AttachmentMutating]      │
   │──► RPCPacketReturnValue ────────────────────►│  ← Client RESPONDS
   │                                              │
   │◄── RPCPacketCallAttachmentMutatingUpdate ◄───│  ← ROLE INVERSION
   │    (server asks client to mutate)            │
   │                                              │
   │    [Mutate CLIENT-LOCAL AttachmentMutating]  │
   │──► RPCPacketReturnVoid ─────────────────────►│
   │                                              │
   │                                        [Function complete]
   │                                              │
   │◄── RPCPacketReturnValue (final result) ◄─────│
   │                                              │
```

On the server, the `mutating` parameter passed to the pool function
is an `AttachmentMutatingRemote` — a proxy that forwards every
operation to the client. The bridge code that implements the pool
method does not know it is talking to a remote state:

```cpp
// Server-side bridge — the same code runs locally and remotely.
// When called via RPC, `mutating` is AttachmentMutatingRemote,
// which proxies every Set/Get/Update back to the client.
PlayerKey create(std::shared_ptr<Viper::AttachmentMutating> const & mutating,
                 std::string const & nickname, Demo::Level level) {
    auto const key      = PlayerKey::create();
    auto const property = PlayerProperty{nickname, level};
    Attachments::Player_Property::set(mutating, key, property);  // proxied!
    return key;
}
```

The Viper RPC layer defines fifteen callback packet types covering
every read and mutation operation an `AttachmentMutating` can
perform — three reads (`Keys`, `Has`, `Get`) and twelve mutations
(`Set`, `Diff`, `Update` on documents; `UnionInSet`, `SubtractInSet`
on sets; map and ordered-array mutations).

## Safety by isolation

The Remote-Local pattern looks dangerous at first read — the server
sends commands that mutate client state. The design is **inherently
safe** because mutations land in the client's `AttachmentMutating`,
and **persistence (if any) is triggered by the client**, never by
the server.

```text
CLIENT                                         SERVER
   │                                              │
   │  ┌─────────────────────────┐                 │
   │  │  AttachmentMutating     │                 │
   │  │  (CLIENT-LOCAL)         │                 │
   │  │                         │                 │
   │  │  All mutations land     │◄────────────────│  Server sends mutations
   │  │  here, locally          │                 │
   │  └───────────┬─────────────┘                 │
   │              │                               │
   │              │ Persistence (if any) is       │
   │              │ TRIGGERED BY THE CLIENT       │
   │              │ — never by the server.        │
   │              ▼                               │
   │  ┌─────────────────────────┐                 │
   │  │  Backing store          │                 │
   │  │  (whatever the client   │                 │
   │  │   chose to bind to its  │                 │
   │  │   AttachmentMutating)   │                 │
   │  └─────────────────────────┘                 │
```

| Failure mode                | Result                             | Data corruption |
|-----------------------------|------------------------------------|-----------------|
| Network timeout             | Client-local state abandoned       | Impossible      |
| Server exception            | Client-local state abandoned       | Impossible      |
| Client crash before persist | Client-local state lost            | Impossible      |
| Server sends invalid data   | Client validates before persisting | Impossible      |
| Partial mutations           | Never reach the backing store      | Impossible      |
