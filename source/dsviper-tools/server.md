# Database Server

Tools for running CommitDatabase as a network service and performing administrative
operations.

| Tool                          | Type   | Purpose                                      |
|-------------------------------|--------|----------------------------------------------|
| **commit_database_server.py** | Server | Expose CommitDatabase over RPC               |
| **commit_admin.py**           | CLI    | Database administration (reset, sync, reduce heads)   |

---

## commit_database_server.py

RPC server that exposes a CommitDatabase over the network. Multiple clients can
work against it directly (transparent proxy) or synchronise a local replica with
it (CommitSynchronizer).

### Basic Usage

```bash
# Start server with default settings (TCP port 54321)
python3 tools/commit_database_server.py project.cdb

# Custom host and port
python3 tools/commit_database_server.py --host 0.0.0.0 --port 54322 project.cdb

# Unix socket (for local IPC, better performance)
python3 tools/commit_database_server.py --socket-path /tmp/project.sock project.cdb

# Verbose logging
python3 tools/commit_database_server.py -vvv project.cdb
```

### Options

| Option          | Description                                        | Default   |
|-----------------|----------------------------------------------------|-----------|
| `--host`        | Bind address                                       | `0.0.0.0` |
| `--port`        | TCP port                                           | `54321`   |
| `--socket-path` | Unix socket path (alternative to TCP)              | -         |
| `-v`            | Verbosity: `-v` critical, `-vv` info, `-vvv` debug | quiet     |

### Graceful Shutdown

Press `Ctrl+C` to stop the server gracefully. Active connections will be closed
and the database will be properly finalized.

### Security

`commit_database_server` shares the network surface and security
posture of all Viper RPC endpoints — trusted-network assumption, no
built-in auth or transport encryption. See
{doc}`../ecosystem/security`.

### Client Connection

Clients connect using `CommitDatabase.connect()` or `CommitDatabase.connect_local()`:

```python
from dsviper import CommitDatabase

# TCP connection
db = CommitDatabase.connect("server.local", "54321")

# Unix socket
db = CommitDatabase.connect_local("/tmp/project.sock")
```

### Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  cdbe.py    │     │  cdbe.py    │     │ Python app  │
│  (client)   │     │  (client)   │     │  (client)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │ RPC Protocol
                           ▼
              ┌────────────────────────┐
              │ commit_database_server │
              │        (server)        │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │    project.cdb         │
              │   (CommitDatabase)     │
              └────────────────────────┘
```

---

(commit-admin-py)=

## commit_admin.py

Administration tool for CommitDatabase operations: sync, reduce heads,
and a demo-only `reset` trick (see warning below).

### Reset Database (demo-only trick)

Remove every commit except the initial one:

```bash
python3 tools/commit_admin.py --database project.cdb reset
```

```{warning}
`reset` is **not a feature** — it is a trick for live-demo scenarios
that need to replay from a known baseline between runs. It breaks the
append-only invariant every other reader relies on; never use it as a
storage-management tool. See
[Storage growth](../commit/commit_database.md#storage-growth) in the
Commit Database chapter for the only sanctioned way to shrink a
database (Flatten).
```

### Reduce Heads

When multiple clients commit concurrently, the database may have multiple "heads"
(concurrent streams). Use `reduce_heads` to reduce them to one:

```bash
# Single reduction pass
python3 tools/commit_admin.py --database project.cdb reduce_heads

# Continuous reduction (loop mode)
python3 tools/commit_admin.py --database project.cdb reduce_heads \
    --loop --update-interval 5
```

### Sync Local with Remote

Synchronize a local database with a remote server:

```bash
# Single sync pass
python3 tools/commit_admin.py --host server.local --port 54321 sync local.cdb

# Continuous sync (loop mode)
python3 tools/commit_admin.py --host server.local sync local.cdb \
    --loop --update-interval 2

# Via Unix socket
python3 tools/commit_admin.py --socket-path /tmp/project.sock sync local.cdb
```

### Options Reference

| Option              | Description                             |
|---------------------|-----------------------------------------|
| `--database`        | Local database path                     |
| `--host`            | Remote server hostname                  |
| `--port`            | Remote server port (default: 54321)     |
| `--socket-path`     | Unix socket path                        |
| `--loop`            | Run continuously                        |
| `--update-interval` | Seconds between iterations (default: 1) |
| `--blob-data-size`  | Max blob pack size in MB (default: 25)  |

### Sub-commands

| Command        | Description                                                  |
|----------------|--------------------------------------------------------------|
| `sync`         | Synchronize local database with source                       |
| `reduce_heads` | Reduce multiple heads into one                               |
| `reset`        | **Demo-only trick** — remove all commits except the initial; see warning above |

