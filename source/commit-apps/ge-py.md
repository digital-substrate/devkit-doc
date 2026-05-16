# ge-py

PySide6 desktop application that exercises the **whole DevKit value chain**
from a single DSM model: code generation with Kibo, persistence and
versioning through `dsviper`, and a Qt Widgets UI assembled from the shared
`dsviper-components` library.

* **Source repository** —
  [`digital-substrate/ge-py`](https://github.com/digital-substrate/ge-py).
* **Entry point** — `graph_editor.py`.
* **Dependencies** — `PySide6`, `dsviper` (from PyPI).

## What it demonstrates

ge-py is a worked example of every layer the documentation introduces in
isolation:

| Layer     | Where in ge-py               | DevKit doc                                            |
|-----------|------------------------------|-------------------------------------------------------|
| DSM model | DSM definitions of the Graph | [DSM](../dsm/index.rst)                               |
| Code-gen  | `ge/` package (Kibo output)  | [Kibo](../kibo/index.rst)                             |
| Runtime   | `dsviper.CommitStore` usage  | [dsviper](../dsviper/index.rst)                       |
| Shared UI | `dsviper_components/`        | [dsviper-components](../dsviper-components/index.rst) |

A single Python application reads its data model from one DSM source and
ships a versioned, undo-aware editor — the value-chain end-to-end.

## Architecture

Pure-Python applications collapse the C++ 6-layer architecture to **five
layers**, because business logic lives in the same language as the
application — function pools are no longer needed to cross a language
boundary.

```text
┌─────────────────────────────────────────────────────────────┐
│  1. UI Layer                                                │
│     PySide6 widgets (graph_editor.py, components/, render/) │
├─────────────────────────────────────────────────────────────┤
│  2. CommitStore Facade                                      │
│     model/context.py — singleton wrapping CommitStore       │
├─────────────────────────────────────────────────────────────┤
│  3. Business Logic (hand-written Python)                    │
│     model/*.py — vertex.py, graph.py, selection_*.py, …     │
├─────────────────────────────────────────────────────────────┤
│  4. Generated Data (Kibo output)                            │
│     ge/*.py — data, attachments, definitions, value_type    │
├─────────────────────────────────────────────────────────────┤
│  5. dsviper Runtime                                         │
│     CommitDatabase, CommitStore, CommitMutableState, Value  │
└─────────────────────────────────────────────────────────────┘
```

## Repository layout

```text
ge-py/
├── graph_editor.py          # Application entry point (QApplication, MainWindow)
├── ge/                      # Kibo-generated infrastructure
│   ├── data.py              # Concept keys, structures, enums
│   ├── attachments.py       # Typed attachment accessors
│   ├── definitions.py       # Embedded DSM definitions
│   └── value_type.py        # Type registry helpers
├── model/                   # Hand-written business logic
│   ├── context.py           # Singleton: store + graph_key + facade
│   ├── graph.py             # Graph creation
│   ├── vertex.py            # Vertex creation
│   ├── edge.py              # Edge creation
│   ├── graph_topology.py    # Topology operations
│   ├── selection_*.py       # Selection management
│   ├── random.py            # Random-data generators
│   └── script_*.py          # Reusable scripts
├── components/              # Project-specific widgets (vertex panel,
│                            #   list panel, render panel, comments, tags…)
├── dsviper_components/      # Vendored copy of the shared dsviper-components
│                            #   library (synced with dev/sync_dsviper_components.py)
├── render/                  # 2-D canvas (paint, hit-testing)
└── list/                    # List-view items
```

## The Context singleton

`model/context.py` is the single point of truth for the running database,
the active graph, and the `CommitStore` that drives undo/redo and UI
notifications. The UI never talks to a `CommitDatabase` directly.

```python
from dsviper import CommitStore, CommitDatabase, CommitState, CommitMutableState
from ge import attachments, definitions
from ge.data import Graph_GraphKey
from model import graph


class Context:

    @classmethod
    def instance(cls) -> "Context":
        if not hasattr(cls, "_instance"):
            setattr(cls, "_instance", cls())
        return getattr(cls, "_instance")

    def __init__(self):
        self.store = CommitStore()
        self.graph_key = Graph_GraphKey.create()

    def use(self, database: CommitDatabase):
        if not database.commit_ids():
            self._create_initial_commit(database, database.initial_state())
        commit_id = database.last_commit_id()
        self.store.set_state(database.state(commit_id))
        self.store.set_database(database)
        self.store.notify_database_did_open()
        self.load()
```

The `Context` exposes the store directly (`context.store.dispatch(...)`)
and adds a small facade for scripting (`context.dispatch`,
`context.undo`, `context.redo`).

See `ge-py/model/context.py` for the full implementation.

## The dispatch pattern

Every UI action that mutates the model goes through one entry point:
`store.dispatch(label, callable)`. The callable receives an
`AttachmentMutating` and applies all mutations for this transaction. After
the lambda returns, the store commits the mutations and notifies the UI.

```python
# graph_editor.py — "Random Vertex" menu action
def _random_vertex_triggered(self):
    context = Context.instance()
    size = self._render_component.render_widget().size()
    rect = Graph_Rectangle()
    rect.x, rect.y, rect.w, rect.h = 0, 0, size.width(), size.height()
    context.store.dispatch(
        "Random Vertex",
        lambda m: model_random.add_vertex(m, context.graph_key, rect),
    )
```

The body of the lambda is **plain Python** that calls into `model/`. Since
business logic is already in Python, no function pool is needed — the
lambda calls `model.random.add_vertex()` directly. This is the central
simplification that distinguishes ge-py (and ge-qml) from the C++
equivalent.

```{tip}
The dispatch label (`"Random Vertex"` above) is what appears in the undo
stack and in the commit history. Pick labels that describe user intent,
not implementation steps.
```

## Business logic — `model/`

`model/` is hand-written Python organised by functional domain. Each module
exposes pure functions taking an `AttachmentMutating` plus the keys/values
they need to operate on, and returns the keys they create. They are
trivially unit-testable in isolation.

```python
# model/vertex.py
def add(attachment_mutating: AttachmentMutating,
        graph_key: Graph_GraphKey,
        value: int,
        position: Graph_Position,
        color: Graph_Color) -> Graph_VertexKey:
    vertex_key = create(attachment_mutating, value, position, color)

    vertex_keys = Set_Graph_VertexKey()
    vertex_keys.add(vertex_key)
    attachments.graph_graph_topology_union_vertex_keys(
        attachment_mutating, graph_key, vertex_keys)

    return vertex_key
```

`model/` modules import from `ge/` (the generated layer) — never the other
way around.

## Generated data — `ge/`

`ge/` is the Kibo output for the Python target. It is regenerated from the
DSM model and never edited by hand. The four files most consumed by the
rest of the app:

| File                | Purpose                                                |
|---------------------|--------------------------------------------------------|
| `ge/data.py`        | Concept keys (`Graph_VertexKey`), structures, enums    |
| `ge/attachments.py` | Typed accessors (`graph_vertex_visual_attributes_set`) |
| `ge/definitions.py` | Embedded DSM definitions, loaded into the database     |
| `ge/value_type.py`  | Type registry helpers                                  |

The mapping from DSM concepts to Python identifiers follows
[Kibo's naming conventions](../kibo/index.rst).

## Notification flow

The `CommitStore` exposes signals that the UI subscribes to. The two most
load-bearing for ge-py:

```python
# graph_editor.py — _setup_connections
notifier.database_did_open.connect(self._store_database_did_open)
notifier.state_did_change.connect(self._store_state_did_change)
```

Their handlers refresh every panel that reads from the store. This is the
**only** path by which the UI updates: a dispatch returns, the store fires
`state_did_change`, and the connected slots redraw.

```text
UI action  ──►  store.dispatch(label, λ)
                       │
                       ▼
                 λ(mutating)            ← business logic runs here
                       │
                       ▼
            store.commit_mutations()    ← persisted to the DAG
                       │
                       ▼
       store.notify_state_did_change()  ← Qt signal
                       │
                       ▼
              UI handlers redraw
```

## What dsviper-components ships with the application

Beyond the panels ge-py builds for its own domain (`components/`), the
application **inherits a complete suite of administration, collaboration
and scripting features by importing from `dsviper-components`**. None of
this code lives in ge-py — the application only instantiates the widgets
and wires them into its menus.

This is the load-bearing reason every Commit-based application in the
ecosystem is built on `dsviper-components`: the moment you adopt the
shared library, your application gets a database inspector, a commit-DAG
browser, an undo-stack viewer, a remote-server sync pipeline, and an
embedded Python REPL — none of which are domain-specific.

### The Admin menu — database introspection and history

The `Admin` menu of ge-py is assembled from eight pre-built dialogs:

```python
# graph_editor.py — _setup_dialog
store = Context.instance().store
self._inspect_dialog = DSInspectDialog()
self._commits_dialog = DSCommitsDialog(store)
self._commit_documents_dialog = DSCommitDocumentsDialog(store)
self._commit_program_dialog = DSCommitProgramDialog(store)
self._commit_undo_dialog = DSCommitUndoDialog(store)
self._commit_blobs_dialog = DSCommitBlobsDialog(store)
self._commit_actions_dialog = DSCommitActionsDialog(store)
self._commit_sync_log_dialog = DSCommitSyncLogDialog()
```

Each dialog is constructed with the running `CommitStore` and reacts on
its own to `state_did_change` notifications — the application has nothing
to do beyond toggling visibility.

| Dialog                    | What it shows                                          |
|---------------------------|--------------------------------------------------------|
| `DSInspectDialog`         | Live tree of every attachment / structure in the state |
| `DSCommitsDialog`         | The full commit DAG (browse, jump to, compare commits) |
| `DSCommitDocumentsDialog` | Documents + attachments grouped by commit              |
| `DSCommitProgramDialog`   | Python program embedded in a commit (replayable)       |
| `DSCommitSettingsDialog`  | Per-commit settings                                    |
| `DSCommitUndoDialog`      | The undo stack as a navigable list                     |
| `DSCommitBlobsDialog`     | Every blob referenced across commits                   |
| `DSCommitActionsDialog`   | Enable / disable / reset commits in batch              |

Adopting these dialogs is what turns a domain editor into a
fully-introspectable Commit application. The same set is consumed by
every Commit-based editor in the ecosystem.

### Collaboration — fetch / push / sync over a commit server

ge-py's File menu and toolbar expose three actions — **Fetch**, **Push**,
**Sync** — that operate on a remote commit server. The wiring is again
fully in `dsviper-components`:

```python
# graph_editor.py
from dsviper_components.ds_commit_synchronizer_thread import DSCommitSynchronizerThread
from dsviper_components.ds_connect_to_server_dialog import DSConnectToServerDialog
from dsviper_components.ds_commit_sync_log_dialog import DSCommitSyncLogDialog

self._sync_logger = DSLogger(Logging.LEVEL_ALL)
self._sync_logging = Logging.create(self._sync_logger)
```

`DSConnectToServerDialog` collects the server address and credentials.
`DSCommitSynchronizerThread` runs the sync I/O off the UI thread and emits
progress signals consumed by `DSCommitSyncLogDialog` (the sync log
visible from the Admin menu). Three menu actions drive the workflow:

- **Fetch** — pull remote commits into the local DAG without applying them.
- **Push** — send local commits that the server does not yet have.
- **Sync** — fetch + push in one step.

The shared DAG itself is a property of the `CommitDatabase` — there is no
separate "merge" step in the application. Convergence is what the commit
DAG is for.

### Embedded Python scripting — DSCodeEditorDialog

ge-py embeds a fully functional Python editor that runs scripts in the
**same interpreter** as the running application — with the application's
`Context` and `CommitStore` exposed as globals:

```python
# graph_editor.py — _setup_dialog
from dsviper_components.python_editor_model import PythonEditorModel

scripts_folder = str(Path(__file__).parent / "scripts")
self._python_editor_model = PythonEditorModel(
    scripts_folder,
    namespace_vars={
        "ctx": Context.instance(),
        "store": store,
        "render_model": self._render_component,
        "_documents_panel": self._commit_documents_dialog,
    },
)
self._code_editor_dialog = DSCodeEditorDialog(self._python_editor_model)
self._python_editor_model.run_init_script()
```

The scripts a user writes from the Editor have direct access to:

- `ctx.dispatch("label", lambda m: …)` — the same dispatch path the UI uses.
- `store.state()`, `store.attachment_getting()` — read-only access to the
  current state.
- domain modules (`from model import …`) — the same business logic
  exposed to the menu actions.

The editor itself contributes a pre-wired **Editor menu** (open / save /
run / show description / refresh syntax). ge-py's `_setup_menu` simply
appends those actions:

```python
# graph_editor.py — _setup_menu
editor = self._code_editor_dialog.editor
editor_menu = self.menuBar().addMenu(self.tr("&Editor"))
editor_menu.addAction(editor.open_script_action)
editor_menu.addAction(editor.save_script_action)
# ...
editor_menu.addAction(editor.run_script_action)
editor_menu.addAction(editor.show_description_action)
```

```{tip}
Scripts run in the live interpreter — they can build complex sequences of
mutations that go through the same `dispatch` path as menu actions, which
means **every script ends up as a single commit in the DAG**, replayable
and undoable like any other operation.
```

For the catalogue of what `dsviper-components` exposes and the
conventions for instantiating each widget, see
[dsviper-components](../dsviper-components/index.rst). The model-agnostic
limit case — generic database editors with no DSM model of their own —
is walked through in [cdbe](cdbe.md).

## Where to read first

1. `graph_editor.py` lines around `_setup_connections` — how the UI wires
   itself to the store's signals.
2. `model/context.py` — the singleton facade and database lifecycle.
3. `model/vertex.py`, `model/graph.py` — the smallest, most readable
   examples of model functions.
4. `graph_editor.py` lines around `_random_vertex_triggered` — a complete
   round trip: UI action → dispatch → model → notification → redraw.
5. `components/list.py` — a panel built on `dsviper-components` that both
   reads the state and dispatches selection mutations back.

## Reference

* [DSM](../dsm/index.rst) — the language ge-py's data model is written in.
* [Kibo](../kibo/index.rst) — the generator that produces `ge/`.
* [dsviper](../dsviper/index.rst) — the runtime exercised through
  `Context.store`.
* [dsviper-components](../dsviper-components/index.rst) — the shared
  widget library the UI is built on.
