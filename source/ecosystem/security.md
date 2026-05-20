# Security posture

Viper assumes a **trusted network**. The runtime carries no
authentication, no authorization, and no transport encryption — these
are delegated to deployment infrastructure (TLS proxy, firewall, Unix
socket permissions).

This applies to every Viper network surface:

- {term}`Services <Service>` — function pools exposed over RPC;
- `commit_database_server` — shared CommitDatabase accessed remotely
  (see {doc}`../dsviper-tools/server`).

Both use the same RPC machinery, with the same model:

| Layer          | Built-in                | Where it lives                |
|----------------|-------------------------|-------------------------------|
| Data integrity | SHA-1 on every commit   | Runtime                       |
| Transport      | Raw TCP / Unix sockets  | Deployment (TLS proxy, VPN)   |
| Authentication | None                    | Deployment (reverse proxy)    |
| Authorization  | None                    | Application code              |

By default, Viper servers bind `0.0.0.0:54321`. Production deployments
should never expose this socket directly to an untrusted network — use
a reverse proxy with TLS termination and authentication, or restrict
access to local Unix sockets.
