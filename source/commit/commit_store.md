# CommitStore

A `CommitDatabase` is the persistence layer — an immutable DAG of
commits on disk. It exposes mutations, but every read and write goes
through explicit commit ids: there is no "current commit", no undo
stack, no notifications. Useful as a backing store; awkward as the
core of an interactive application.

**CommitStore** is the in-memory wrapper that turns a `CommitDatabase`
into the runtime surface a Commit Application actually uses. It:

* owns a current state (the commit a UI is looking at),
* dispatches typed mutations as commits,
* maintains an undo / redo stack,
* notifies observers when any of the above changes,
* exposes DAG navigation (multi-head, merge, forward).

This page introduces the four surfaces and points at the canonical
references for each. For full method signatures, see the
[CommitStore API reference](../dsviper/api/commit.rst).

---

## The four surfaces

### 1. Lifecycle

A store starts empty. It is bound to a database (and optionally a
specific state) and released the same way:

```pycon
>>> from dsviper import CommitStore, CommitDatabase
>>> store = CommitStore()
>>> store.use(CommitDatabase.open("model.cdb"))
>>> store.has_database()
True
>>> store.close()
```

`use()` is the high-level entry; `set_database()` / `set_state()`
exist for finer control (cdbe-style generic editors that decide
"open this database at this commit"). Once a database is attached,
`state()` returns the current `CommitState` and `mutable_state()`
hands out a fresh `CommitMutableState` to build a commit on top.

### 2. Dispatch

All mutations flow through `dispatch`. The store builds a mutable
state, runs the callable, persists the resulting commit, advances
the head, and notifies observers — atomically:

```pycon
>>> store.dispatch(
...     "Add Alice",
...     lambda m: m.set(TUTO_A_USER_LOGIN, key, login),
... )
```

Convenience wrappers for the most common shapes:

| Method                     | What it dispatches                              |
|----------------------------|-------------------------------------------------|
| `dispatch_set`             | A single `set(attachment, key, value)`.         |
| `dispatch_update`          | A path-based `update(...)`.                     |
| `dispatch_diff`            | The diff of an updated document vs current.    |
| `dispatch_enable_commit`   | Enable / disable a commit in the DAG.           |

The single dispatch surface is what gives the
[Commit Application Model](commit_application_model.md#the-dispatch-pattern)
its Redux-like shape: every state change is an explicit, labelled
action against the store, never a sideways write to the database.

### 3. Undo / redo and DAG navigation

The store maintains an in-memory undo stack on top of the underlying
commit DAG. Calls do not rewrite history — they move the current
state along existing commits, diverging when necessary.

```pycon
>>> store.can_undo()
True
>>> store.undo()
>>> store.redo()
>>> store.use_commit(some_commit_id)        # jump anywhere
>>> store.forward()                          # follow to the most plausible head
>>> store.reduce_heads()                     # collapse multi-head to one
```

For the conceptual model of divergence and multi-head exploration,
see [Modes of Use](commit_database.md#modes-of-use). For the underlying
DAG guarantees the store leans on, see
[the Dual-Layer Contract](commit_contract.md).

### 4. The notification protocol

The store communicates with the UI through `CommitStoreNotifying` —
a small, framework-agnostic Python protocol. Each platform adapts
it to its own notification mechanism (Qt Signals,
`NSNotificationCenter`, …). The store never imports a UI framework.

| Notification                    | When                                                |
|---------------------------------|-----------------------------------------------------|
| `notify_database_did_open`      | A database has been attached.                       |
| `notify_database_did_close`     | The store has been closed.                          |
| `notify_state_did_change`       | The current state moved (commit, undo, navigation). |
| `notify_definitions_did_change` | Definitions extended at runtime.                    |
| `notify_dispatch_error`         | A dispatched callable raised.                       |
| `notify_database_will_reset` / `notify_database_did_reset` | Reset bracket.           |
| `notify_stop_live`              | Live mode requested to stop.                        |

A notifier is installed once:

```pycon
>>> store.set_notifier(my_notifier)   # any CommitStoreNotifying impl
```

The canonical Qt adapter — `DSCommitStoreNotifier`, which turns each
notification into a Qt Signal — lives in `dsviper-components`. See
[The Notifier Bridge](../dsviper-components/architecture.md#the-notifier-bridge)
for the bridge code and the Qt integration recipe.

---

## End-to-end

```python
from dsviper import CommitStore, CommitDatabase

store = CommitStore()
store.use(CommitDatabase.open("model.cdb"))
store.set_notifier(my_notifier)            # observable

store.dispatch("Add Alice",
               lambda m: m.set(TUTO_A_USER_LOGIN, key, login))

assert store.can_undo()
store.undo()
store.redo()

store.close()
```

A real application wraps this in an
[Application Context](commit_application_model.md#the-application-context)
that also holds domain state and the dispatch wiring its UI calls
into.

---

## See also

* [Commit Database](commit_database.md) — the `CommitDatabase` API the
  store sits on.
* [Commit Application Model](commit_application_model.md) — the
  architectural pattern that composes a `CommitStore` with an
  Application Context.
* [Dual-Layer Contract](commit_contract.md) — the structural guarantees
  the store relies on and the semantic checks that remain the
  application's responsibility.
* [Component architecture](../dsviper-components/architecture.md) — the
  Qt adapter for `CommitStoreNotifying`.
* [CommitStore API reference](../dsviper/api/commit.rst) — full method
  signatures.
