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
safe at the state-ownership level** because the server has no handle on
the client's authoritative state. Mutations land in an `AttachmentMutating` *context* owned by
the client, isolated from the model the client treats as ground
truth. The client alone decides whether — and when — to integrate
that context back into its authoritative state.

The protocol's safety property is at the **state-ownership** level :
the server cannot reach into the client's model. What happens
downstream of the context (held in memory, integrated into the
authoritative state, eventually persisted, discarded) is the
client's prerogative and is orthogonal to the protocol.

```text
CLIENT                                                  SERVER
   │                                                       │
   │  ┌───────────────────────────────────┐                │
   │  │  AttachmentMutating (context)     │                │
   │  │  CLIENT-LOCAL, server-isolated    │                │
   │  │                                   │                │
   │  │  All mutations land here          │◄───────────────│  Server sends mutations
   │  └───────────────┬───────────────────┘                │
   │                  │                                    │
   │                  │ Integration into authoritative     │
   │                  │ state is the CLIENT's decision.    │
   │                  │ Persistence, if any, is downstream │
   │                  │ of integration — never driven      │
   │                  │ by the server.                     │
   │                  ▼                                    │
   │  ┌───────────────────────────────────┐                │
   │  │  Client-authoritative state       │                │
   │  └───────────────────────────────────┘                │
```

| Failure mode              | Effect on the client's authoritative state        |
|---------------------------|---------------------------------------------------|
| Network timeout           | Mutation context abandoned, never integrated      |
| Server exception          | Mutation context abandoned, never integrated      |
| Server sends invalid data | Client may discard the context before integration |
| Partial mutations         | Context never integrated as a whole               |

The structural integrity of the client's authoritative state is
guaranteed at the protocol level. **Semantic integrity** under
multi-author reduction is a separate concern of the commit layer —
see [Dual-Layer Contract](../commit/commit_contract.md).

**Transport security** — authentication and encryption against a
spoofed or eavesdropping server — is a separate concern again: Viper
assumes a trusted network and delegates it to deployment (see
[Security posture](../ecosystem/security.md)). State isolation bounds
what a *connected* server can do; it is not a substitute for securing
the connection.
