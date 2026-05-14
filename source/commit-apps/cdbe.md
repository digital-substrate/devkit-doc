# cdbe.py — Commit Database Editor

PySide6 desktop application that opens **any** commit database — no
domain, no Kibo output, no business logic. Built almost entirely by
composing widgets from
[`dsviper-components`](../dsviper-components/index.rst), driven by the
runtime introspection API of [`dsviper`](../dsviper/index.rst). Ships
inside [`dsviper-tools`](../dsviper-tools/index.rst) as the working
tool the DevKit uses to inspect, mutate, and synchronise commit
databases.

* **Source repository** —
  [`digital-substrate/dsviper-tools`](https://github.com/digital-substrate/dsviper-tools).
* **Entry point** — `cdbe.py`.
* **Dependencies** — `PySide6`, `dsviper` (from PyPI),
  `dsviper-components` (vendored in-tree).

## What it demonstrates

cdbe is the **degenerate case** of the Commit Application Model:
the same pattern as ge-py / ge-qml, but with the domain-specific
layers collapsed because there is no domain. It is what remains
when you take the
[Commit Application Model](model.md) and remove every domain-specific
piece.

| Layer of the Python profile      | Where in cdbe.py                                                                                 |
|----------------------------------|--------------------------------------------------------------------------------------------------|
| 1 — UI Layer                     | `cdbe.py` (`MainWindow` and dialogs)                                                             |
| 2 — Application Context (facade) | Singletons `CommitStore.instance()` + `DSCommitStoreNotifier.instance()`, hosted by `MainWindow` |
| 3 — Business Logic               | **Empty** — no domain, no `model/`                                                               |
| 4 — Generated Data (Kibo output) | **Empty** — no DSM model, no `ge/`                                                               |
| 5 — dsviper Runtime              | `CommitStore`, `CommitDatabase`, `CommitSynchronizer`, introspection API                         |

What replaces the missing layers 3 and 4 is the **runtime
introspection** built into `dsviper`: the documents widget
(`DSDocumentsCommitStore`) walks the live database through generic
APIs and renders editable forms based on the embedded DSM definitions
of whatever database has been opened. There is no compile-time
knowledge of the schema.

## Architecture

cdbe collapses the five-layer Python profile to **three effective
layers**, because the two domain-bearing layers (3 and 4) are absent:

```text
┌──────────────────────────────────────────────────────────────┐
│  1. UI Layer                                                 │
│     MainWindow + admin dialogs (all from dsviper-components) │
├──────────────────────────────────────────────────────────────┤
│  2. Application Context (host)                               │
│     CommitStore.instance() + DSCommitStoreNotifier.instance()│
│     — no domain state, no dispatch surface beyond raw store  │
├──────────────────────────────────────────────────────────────┤
│ ─── 3 (Business Logic) and 4 (Generated Data): not used ───  │
├──────────────────────────────────────────────────────────────┤
│  5. dsviper Runtime                                          │
│     Runtime introspection drives everything                  │
└──────────────────────────────────────────────────────────────┘
```

The UI is itself dominated by shared components: cdbe's
`MainWindow.setCentralWidget(...)` is a `DSDocumentsCommitStore` from
`dsviper-components`, not a domain widget written for cdbe.

## Repository layout

```text
dsviper-tools/
├── cdbe.py                  # Application entry point (QApplication, MainWindow)
├── dbe.py                   # Sibling — same shape, non-versioned Database backend
├── dsviper_components/      # Vendored copy of the shared dsviper-components library
├── scripts/                 # User scripts (run by the embedded Python editor)
└── resources_rc.py          # Compiled Qt resources (icons)
```

There is no `model/`, no `ge/`, no `components/`. Everything visible
to the user is either `cdbe.py` itself (≈800 lines of menu / action
plumbing) or imported from `dsviper_components`.

## The "Application Context" — singletons hosted by MainWindow

ge-py defines a `Context` class that owns its `CommitStore` and the
domain state (`graph_key`). cdbe has no domain state, so there is no
dedicated `Context` class either. Two roles take its place:

* **The runtime singletons** — `CommitStore.instance()` and
  `DSCommitStoreNotifier.instance()`. They are created once in `main`
  and bound together:

  ```python
  # cdbe.py — main()
  store    = CommitStore.instance()
  notifier = DSCommitStoreNotifier.instance()
  store.set_notifier(CommitStoreNotifying.create(notifier))
  ```

* **The `MainWindow`** — hosts the central widget and all the admin
  dialogs, owns the action set, the menus, the toolbar, and the
  database lifecycle (`open_database`, `close_database`,
  `_set_database`). Functionally it is the Application Context for
  cdbe — minus the domain.

The result: when there is no domain to model, the Application
Context degenerates into a Qt main window wired to the runtime
singletons. The pattern is intact; the body shrinks.

## The central widget — model-agnostic by construction

The single most informative line in `cdbe.py` is its central widget
setup:

```python
# cdbe.py — _setup_central_widget
def _setup_central_widget(self):
    self._documents = DSDocumentsCommitStore()
    self._documents.set_store(CommitStore.instance())
    self.setCentralWidget(self._documents)
```

`DSDocumentsCommitStore` is a generic documents browser shipped by
`dsviper-components`. It introspects the open `CommitStore` at runtime
to:

* enumerate the documents (concept instances) the database knows of,
* group them by their attachment categories,
* render editable forms whose fields come from the **embedded DSM
  definitions** of the database itself, not from compile-time types,
* apply edits as proper `CommitStore` mutations — every keystroke
  ends up as a commit on the DAG.

This is the load-bearing reason cdbe can open *any* commit database
without prior knowledge of its schema: the central widget itself
relies on runtime introspection, not on generated typed code.

```{tip}
The same widget is the central widget in any other Commit application
that wants a generic documents inspector. The QML counterpart is
`DS.DocumentsPanel` driven by `DocumentsPanelModel`, used the same way
by [`dsviper-tools-qml`](https://github.com/digital-substrate/dsviper-tools-qml).
```

## The dispatch surface — only raw store operations

Because cdbe has no domain, it never calls business functions. Its
"dispatch" reduces to raw runtime operations exposed by the store:

```python
# cdbe.py — Commit / Edit actions
def _forward_triggered(self):       CommitStore.instance().forward()


def _merge_heads_triggered(self):   CommitStore.instance().reduce_heads()


def _undo_triggered(self):          CommitStore.instance().undo()


def _redo_triggered(self):          CommitStore.instance().redo()
```

Domain mutations (editing a field, changing an attachment) come from
inside the central widget — `DSDocumentsCommitStore` calls
`store.dispatch(...)` itself when the user commits a form. The
`MainWindow` never touches dispatch with a domain lambda; it only
drives DAG navigation and undo/redo.

Compare with ge-py, where `_random_vertex_triggered` calls
`context.store.dispatch("Random Vertex", λ)` with a lambda routed to
`model.random.add_vertex(...)`. There is no equivalent in cdbe — the
moment domain logic is needed, you are no longer writing a generic
editor.

## Notification flow

Same shape as ge-py: the `MainWindow` connects to the notifier's
signals once, and every mutation arriving from the central widget or
from a sync round-trip lands in the same handlers.

```python
# cdbe.py — _setup_connections
notifier = DSCommitStoreNotifier.instance()
notifier.database_did_open.connect(self._store_database_did_open)
notifier.database_did_close.connect(self._store_database_did_close)
notifier.state_did_change.connect(self._store_state_did_change)
notifier.definitions_did_change.connect(self._store_definitions_did_change)
notifier.dispatch_error.connect(self._present_error)
notifier.stop_live.connect(self._store_stop_live)
notifier.reset_database.connect(self._store_reset_database)
notifier.database_will_reset.connect(self._store_database_will_reset)
```

`_store_state_did_change` simply re-validates the menu actions (can
undo? can redo?). The central widget reacts to the same signal on its
own through its own subscription to the store. Everything else
(commits dialog, undo dialog, blobs dialog…) is wired the same way
inside `dsviper-components` and refreshes itself when the state
changes.

## What dsviper-components ships with the application

cdbe is the cleanest example of "what `dsviper-components` actually
provides": almost every visible feature of cdbe is a shared dialog
constructed with the running `CommitStore`:

```python
# cdbe.py — _setup_dialog (abridged)
store = CommitStore.instance()
self._inspect_dialog = DSInspectDialog()
self._commits_dialog = DSCommitsDialog(store)
self._commit_program_dialog = DSCommitProgramDialog(store)
self._commit_undo_dialog = DSCommitUndoDialog(store)
self._commit_blobs_dialog = DSCommitBlobsDialog(store)
self._commit_actions_dialog = DSCommitActionsDialog(store)
self._commit_sync_log_dialog = DSCommitSyncLogDialog()
self._code_editor_dialog = DSCodeEditorDialog(self._python_editor_model)
```

| Dialog                   | What it shows                                     |
|--------------------------|---------------------------------------------------|
| `DSInspectDialog`        | Database metadata: path, UUID, codec, definitions |
| `DSCommitsDialog`        | The full commit DAG (browse, jump to, compare)    |
| `DSCommitProgramDialog`  | Python program embedded in a commit (replayable)  |
| `DSCommitSettingsDialog` | Per-commit settings                               |
| `DSCommitUndoDialog`     | The undo stack as a navigable list                |
| `DSCommitBlobsDialog`    | Every blob referenced across commits              |
| `DSCommitActionsDialog`  | Enable / disable / reset commits in batch         |
| `DSCommitSyncLogDialog`  | Live log of synchronizer activity                 |
| `DSCodeEditorDialog`     | Embedded Python editor wired to store + documents |

cdbe contributes the menus, the keyboard shortcuts, the action
plumbing, and the database lifecycle — but the **content** of every
dialog and the central widget itself come from the shared library.

### Sync — fetch / push / sync / live

The sync surface is composed in the same way:

```python
# cdbe.py
from dsviper_components.ds_commit_synchronizer_thread import DSCommitSynchronizerThread
from dsviper_components.ds_connect_to_server_dialog import DSConnectToServerDialog

self._sync_logger = DSLogger(Logging.LEVEL_ALL)
self._sync_logging = Logging.create(self._sync_logger)
```

`DSConnectToServerDialog` collects credentials and writes them to
settings; `_synchronize(mode)` calls
`DSSettings().create_synchronizer(mode, path)` to drive the
runtime-level `CommitSynchronizer` directly from the toolbar
(Fetch / Push / Sync). Every sync round-trip can update embedded
definitions, in which case the notifier is told to re-broadcast.

The **Live Mode** action goes one step further — it loops on a
`QTimer` and runs the configured synchronizer (with optional
head-merge) on every tick:

```python
# cdbe.py — _live_timer_timeout (abridged)
def _live_timer_timeout(self):
    if not self._live_enabled:
        return
    if self._synchronizer:
        thread = DSCommitSynchronizerThread(
            self._synchronizer, self._sync_logging, self)
        thread.syncDone.connect(self._live_synchronization_done)
        thread.start()
    else:
        self._live_schedule_if_safe_reduce_forward()
```

This is the simplest demonstration in the DevKit of **continuous
multi-author convergence**: cdbe will keep pulling and pushing in the
background, optionally reducing heads whenever a divergence appears.

### Embedded Python — DSCodeEditorDialog

Same as ge-py: a `PythonEditorModel` exposes the live `store` (and the
documents panel) as namespace globals to the embedded editor, so any
script written from inside cdbe operates on the open database.
Because cdbe has no domain, the namespace is minimal:

```python
# cdbe.py — _setup_dialog (Python Editor)
self._python_editor_model = PythonEditorModel(
    scripts_folder,
    namespace_vars={
        "store": store,
        "_documents_panel": self._documents,
    },
)
```

A user with cdbe open can write `store.dispatch("…", lambda m: …)`
against any opened database, using only the runtime API — no
domain-specific imports needed.

## Why cdbe is the right starting point

If you read the walkthroughs in order, **cdbe first** shows the
Commit Application Model **stripped of its domain** — the bare
skeleton of a Commit application: a Qt main window, the `CommitStore`

+ Notifier singletons, a model-agnostic central widget, and the
  shared library's admin dialogs. From there:

* [ge-py](ge-py.md) re-introduces the domain — a DSM model, Kibo
  output, business functions in `model/`, and a `Context` class that
  owns the `graph_key`. Same Model, with the layers 3 and 4 filled in.
* [ge-qml](ge-qml.md) keeps the same domain and swaps the
  presentation tier from Qt Widgets to Qt Quick / QML.
* [web-cdbe](web-cdbe.md) takes the same model-agnostic posture as
  cdbe but ports the central-widget idea to a server-rendered
  HTML/CSS surface.

Reading them in this order makes the structure visible: cdbe is what
remains of the pattern when nothing about the domain is known; the
others are what gets added back when the domain is known.

## Where to read first

1. `cdbe.py` — `_setup_central_widget` — the model-agnostic widget setup.
2. `cdbe.py` — `main()` and `_setup_connections` — singletons + notifier wiring.
3. `cdbe.py` — `_setup_dialog` — the eight shared admin dialogs.
4. `cdbe.py` — `_live_timer_timeout` and surrounding live-mode code —
   continuous multi-author sync in its simplest form.
5. `cdbe.py` — `_synchronize` and the connect-to-server dialog — manual
   sync workflow.

## Reference

* [Commit Application Model](model.md) — the pattern cdbe instantiates.
* [dsviper](../dsviper/index.rst) — the runtime exercised through the
  singleton `CommitStore`.
* [dsviper-components](../dsviper-components/index.rst) — the shared
  widget library that supplies the central widget and every dialog.
* [dsviper-tools](../dsviper-tools/index.rst) — the package cdbe ships
  with.
