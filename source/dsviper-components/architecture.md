# Architecture

The library's components share two conventions: **signal-based state
updates** (the Notifier Bridge) and **constructor-based store injection**
(composition over inheritance).

## The Notifier Bridge

```{seealso}
The framework-agnostic `CommitStoreNotifying` protocol — what
notifications exist, when each fires — is documented on
[CommitStore — The notification protocol](../commit/commit_store.md#4-the-notification-protocol).
This section covers the **Python / Qt adapter** that translates those
notifications into Qt Signals.
```

The dsviper runtime emits change notifications through the
`CommitStoreNotifying` protocol. For Qt to consume them, they must
become Qt **Signals**.

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
each component, so it imposes no single topology. Both ge-py and ge-qml run one
`CommitStore` behind a `Context` singleton; what differs is how each supplies
the notifier:

- **ge-py** has each component reach the `DSCommitStoreNotifier.instance()`
  convenience singleton;
- **ge-qml** injects an explicit notifier into every component instead;
- **headless tools** build a `CommitStore` for a one-off task.

```{tip}
The `instance()` classmethods on some components
(`DSCommitStoreNotifier.instance()`) are a convenience, **not** a requirement.
```

## Integration recipe

A minimal Commit-based application built on `dsviper-components` does
four things, in this order:

```python
from dsviper import CommitStore, CommitDatabase
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from dsviper_components.ds_commits_dialog       import DSCommitsDialog
from dsviper_components.ds_commit_undo_dialog   import DSCommitUndoDialog
# … any other dialog the application wants

# 1. Build the store (one or many) and attach a database.
store = CommitStore()
store.use(CommitDatabase.open("model.cdb"))

# 2. Wire the notifier so the runtime can emit Qt Signals.
notifier = DSCommitStoreNotifier()
store.set_notifier(notifier)        # CommitStore consumes CommitStoreNotifying
store.notify_database_did_open()

# 3. Instantiate the dialogs the application wants. Each receives the
#    same store. They subscribe to the notifier on their own and react
#    to state_did_change, database_did_open, etc.
commits_dialog = DSCommitsDialog(store)
undo_dialog    = DSCommitUndoDialog(store)

# 4. Wire the application's own UI to the same notifier, so the domain
#    panels redraw in lock-step with the shared dialogs.
notifier.state_did_change.connect(self._refresh_my_panel)
```

Steps 1–2 are the runtime side. Step 3 is what `dsviper-components`
adds: every shared widget instantiated with the running store. Step 4
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
