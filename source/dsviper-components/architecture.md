# Architecture

The library's components share two conventions: **signal-based state
updates** (the Notifier Bridge) and **constructor-based store injection**
(composition over inheritance).

## The Notifier Bridge

```{seealso}
This page describes the **Python / Qt implementation**. For the
language-agnostic statement of the same pattern, see
[Commit Application Model — The notification contract](../commit-apps/model.md#the-notification-contract).
```

The dsviper runtime exposes change notifications through the
`CommitStoreNotifying` protocol — a plain Python interface with methods
like `notify_state_did_change()` and `notify_database_did_open()`.
For Qt to consume these notifications, they must become Qt **Signals**.

`DSCommitStoreNotifier` is the **adapter** that bridges the two worlds.
It is a `QObject` whose signals mirror the protocol's notification
methods one-for-one:

```python
# dsviper_components/ds_commit_store_notifier.py
class DSCommitStoreNotifier(QObject):

    # Database
    database_did_open      = Signal()
    database_did_close     = Signal()
    state_did_change       = Signal()
    definitions_did_change = Signal()

    # Dispatch
    dispatch_error = Signal(Error)

    # Live Mode
    stop_live = Signal()

    # Reset
    reset_database     = Signal()
    database_will_reset = Signal()
    database_did_reset  = Signal()

    message = Signal(str)

    def notify_state_did_change(self):
        self.state_did_change.emit()
    # … one method per Signal
```

The pattern is the same on every platform that has its own notification
mechanism (NSNotificationCenter on AppKit, signals/slots on Qt C++,
`QObject` Signals here). The runtime stays platform-agnostic; each UI
adapter translates the abstract notifications into the platform's
native event mechanism.

## Composition over inheritance

Every widget in the library accepts the running `CommitStore` (or one of
its lower-level cousins like `Databasing`) **as a constructor argument**:

```python
# A typical dialog
class DSCommitsDialog(QDialog):
    def __init__(self, store: CommitStore, *args, **kwargs):
        super().__init__(*args, **kwargs)
        component = self._setup_ui()
        component.set_store(store)
```

The widget does not subclass anything domain-specific; it does not reach
out to a global. The application owns the store and **injects** it into
each component. This makes the library equally usable in:

- a single-store application (one `CommitStore.instance()`, used by ge-py),
- a multi-store application (one `CommitStore` per document, used by
  ge-qml),
- and headless tools that build a `CommitStore` for a one-off task.

```{tip}
The `instance()` classmethods present on some components
(`DSCommitStoreNotifier.instance()`) are a convenience for single-store
applications, **not** a requirement. ge-qml deliberately avoids them and
injects an explicit notifier into every component.
```

## Integration recipe

A minimal Commit-based application built on `dsviper-components` does
five things, in this order:

```python
from dsviper import CommitStore, CommitDatabase
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from dsviper_components.ds_commits_dialog       import DSCommitsDialog
from dsviper_components.ds_commit_undo_dialog   import DSCommitUndoDialog
# … any other dialog the application wants

# 1. Build the store (one or many).
store = CommitStore()

# 2. Wire the notifier so the runtime can emit Qt Signals.
notifier = DSCommitStoreNotifier()
store.set_notifier(notifier)        # CommitStore consumes CommitStoreNotifying

# 3. Open or create the database, then attach it to the store.
database = CommitDatabase.open("model.cdb")
store.set_database(database)
store.notify_database_did_open()

# 4. Instantiate the dialogs the application wants. Each receives the
#    same store. They subscribe to the notifier on their own and react
#    to state_did_change, database_did_open, etc.
commits_dialog = DSCommitsDialog(store)
undo_dialog    = DSCommitUndoDialog(store)

# 5. Wire the application's own UI to the same notifier, so the domain
#    panels redraw in lock-step with the shared dialogs.
notifier.state_did_change.connect(self._refresh_my_panel)
```

Steps 1–3 are the runtime side. Step 4 is what `dsviper-components`
adds: every shared widget instantiated with the running store. Step 5
is the only application-specific wiring left.

```{note}
The notifier is subscribed in **two** directions: the runtime tells it
"state changed", and the UI listens for the corresponding Qt Signal.
The notifier never reaches into the runtime — it only translates
notifications.
```

## Why this matters

The administrative surface of a Commit application — DAG browsing, undo
navigation, blob inspection, remote sync, embedded scripting — operates on
the runtime concepts, not on any specific domain, so it is identical
across applications. Adopting `dsviper-components` delegates that surface
and leaves only the domain-specific part to write.

For the catalogue of what the library exposes, see
[Widgets](widgets.md). For a worked example of the integration in a
real application, see the
[ge-py walk-through](../commit-apps/ge-py.md).
