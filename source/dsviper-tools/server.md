# Database Server & Administration

Tools for running CommitDatabase as a network service and performing administrative
operations.

| Tool                          | Type   | Purpose                                      |
|-------------------------------|--------|----------------------------------------------|
| **commit_database_server.py** | Server | Expose CommitDatabase over RPC               |
| **commit_admin.py**           | CLI    | Database administration (reset, sync, converge heads) |

---

## commit_database_server.py

RPC server that exposes a CommitDatabase over the network, allowing multiple clients
to synchronize with a central database.

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

## commit_admin.py

Administration tool for CommitDatabase operations: reset, sync, and converge heads.

### Reset Database

Reset a database to its initial commit, deleting all history:

```bash
python3 tools/commit_admin.py --database project.cdb reset
```

```{warning}
This operation is destructive and cannot be undone. All commits except the
initial commit will be deleted.
```

### Reduce Heads

When multiple clients commit concurrently, the database may have multiple "heads"
(concurrent streams). Use `reduce_heads` to converge them:

```bash
# Single convergence pass
python3 tools/commit_admin.py --database project.cdb reduce_heads

# Continuous convergence (loop mode)
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

| Command        | Description                                 |
|----------------|---------------------------------------------|
| `reset`        | Reset to first commit (deletes all history) |
| `reduce_heads` | Merge multiple heads into one               |
| `sync`         | Synchronize local database with source      |

---

