# ge-qml — Graph Editor (QML)

PySide6 + QML desktop application — the QML port of [ge-py](ge-py.md). Same
DSM model, same generated `ge/` package, same hand-written `model/`
business logic, same `CommitStore` facade. The UI is QML, driven by Python
`QObject` models registered as QML context properties. Built on the Qt
Quick variant of `dsviper-components`.

* **Source repository** —
  [`digital-substrate/ge-qml`](https://github.com/digital-substrate/ge-qml).
* **Entry point** — `graph_editor.py` (shim that runs `graph_editor/main.py`).
* **Dependencies** — `PySide6` (Qt Quick + Quick Controls + Dialogs), `dsviper` (from PyPI).

## What it demonstrates

ge-qml is the same value-chain walk-through as ge-py, swapping Qt Widgets
for Qt Quick:

| Layer      | Where in ge-qml                           | DevKit doc                                            |
|------------|-------------------------------------------|-------------------------------------------------------|
| DSM model  | DSM definitions of the Graph              | [DSM](../dsm/index.rst)                               |
| Code-gen   | `graph_editor/ge/` package (Kibo output)  | [Kibo](../kibo/index.rst)                             |
| Runtime    | `dsviper.CommitStore` usage               | [dsviper](../dsviper/index.rst)                       |
| Shared QML | `dsviper_components_qml/` (vendored copy) | [dsviper-components](../dsviper-components/index.rst) |

The interesting comparison with ge-py is what changes — and what doesn't —
when the UI moves from imperative widgets to declarative QML. `model/`,
`ge/`, and `Context` are essentially identical to ge-py: the entire
business stack is reused.

## Architecture

QML adds one layer above ge-py's five-layer stack — a thin **QObject
bridge** that exposes the application state to QML through Qt properties
and slots. Six layers in total:

```text
┌─────────────────────────────────────────────────────────────┐
│  1. UI Layer (QML)                                          │
│     Main.qml + GraphVertexPanel.qml, GraphListPanel.qml, …  │
├─────────────────────────────────────────────────────────────┤
│  2. QObject Bridge (Python)                                 │
│     vertex_model.py, list_model.py, render_model.py, …      │
│     Properties + Slots, registered as QML context props     │
├─────────────────────────────────────────────────────────────┤
│  3. CommitStore Facade                                      │
│     model/context.py — singleton wrapping CommitStore       │
├─────────────────────────────────────────────────────────────┤
│  4. Business Logic (hand-written Python)                    │
│     model/*.py — vertex.py, graph.py, selection_*.py, …     │
├─────────────────────────────────────────────────────────────┤
│  5. Generated Data (Kibo output)                            │
│     ge/*.py — data, attachments, definitions, value_type    │
├─────────────────────────────────────────────────────────────┤
│  6. dsviper Runtime                                         │
│     CommitDatabase, CommitStore, CommitMutableState, Value  │
└─────────────────────────────────────────────────────────────┘
```

The bridge layer is what makes a QML application different from a Widgets
application — and why the `model/` and `ge/` layers are bit-for-bit
shareable with ge-py.

## Repository layout

```text
ge-qml/
├── graph_editor.py             # Entry-point shim — runs graph_editor/main.py
├── graph_editor/               # Application package
│   ├── main.py                 # QApplication + QQmlApplicationEngine setup
│   ├── Main.qml                # Root window (menus, layout)
│   ├── Graph*Panel.qml         # Domain panels (vertex, list, tags, comments, render)
│   ├── *_model.py              # QObject bridges exposed to QML
│   ├── transient_notifier.py   # Live-preview channel (illusion pattern)
│   ├── ge/                     # Kibo-generated infrastructure (same as ge-py)
│   ├── model/                  # Hand-written business logic (same as ge-py)
│   │   ├── context.py          # Singleton: store + graph_key + facade
│   │   ├── graph.py, vertex.py, edge.py, …
│   │   └── script_*.py         # Reusable scripts
│   ├── render/                 # 2-D canvas (paint, hit-testing)
│   ├── list/                   # List-view items
│   ├── scripts/                # User-editable Python scripts (run from the embedded editor)
│   └── images/                 # App icon and assets
└── dsviper_components_qml/     # Vendored copy of dsviper-components-qml
                                #   (synced with dev/sync_dsviper_components_qml.py)
```

The shim at the repo root keeps `python3 graph_editor.py` working from any
directory; the real entry point is `graph_editor/main.py`.

## The Context singleton

`graph_editor/model/context.py` is identical in spirit (and almost
character-for-character) to ge-py's `Context`. Same singleton, same
`CommitStore`, same `Graph_GraphKey`, same `use(database)` lifecycle,
same `dispatch` / `undo` / `redo` facade for scripting.

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

That this file is essentially copy-pasted between ge-py and ge-qml is the
point: **the Commit-facing layer is UI-agnostic**. Switching toolkits
costs you the bridge and the views, not the application core.

## The dispatch pattern

Every mutation still goes through `store.dispatch(label, callable)` — but
in QML, the trigger lives in a `@Slot` on a `QObject` model, called from
QML, instead of in a widget event handler:

```python
# vertex_model.py — value setter exposed to QML
@Slot(int)
def setValue(self, new_value: int):
    if not self._vertex_key:
        return
    label = f"Set Value '{new_value}' For Vertex '{self._value}'"
    self._context.store.dispatch(
        label,
        lambda m: attachments.graph_vertex_visual_attributes_set_value(
            m, self._vertex_key, new_value))
```

```qml
// GraphVertexPanel.qml
SpinBox {
    value: vertexModel.value
    onValueModified: vertexModel.setValue(value)
}
```

The body of the lambda is **plain Python** that calls into `model/` and
the generated `ge.attachments` API — exactly as in ge-py. The only
difference is the firing path: QML ➔ Slot ➔ dispatch ➔ business logic.

```{tip}
The dispatch label still drives the undo stack and the commit history.
The QML port keeps the same convention — labels describe user intent
(`"Set Value '7' For Vertex '3'"`), not implementation steps.
```

## The QObject bridge — `*_model.py`

This is the layer ge-py does not have. Each `*_model.py` is a
`QObject` subclass that:

- exposes view-state as Qt **Properties** with `notify` signals — QML
  bindings track them automatically;
- exposes user actions as `@Slot` methods — QML calls them by name;
- subscribes to `CommitStore` notifications (`state_did_change`,
  `database_did_open`, `database_did_close`) and re-reads the state
  every time the store changes.

```python
class VertexModel(QObject):
    valueChanged = Signal()

    def __init__(self, notifier, parent=None):
        super().__init__(parent)
        self._context = Context.instance()
        notifier.state_did_change.connect(self._configure)

    def _get_value(self) -> int:
        return self._value

    value = Property(int, _get_value, notify=valueChanged)

    @Slot(int)
    def setValue(self, new_value: int):
        self._context.store.dispatch(
            f"Set Value '{new_value}'",
            lambda m: attachments.graph_vertex_visual_attributes_set_value(
                m, self._vertex_key, new_value))

    def _configure(self):
        # re-read state on every notification, emit *Changed signals
        ...
```

`main.py` instantiates each model with the notifier from
`CommitAdminModel.notifier` and wires it to QML:

```python
ctx = engine.rootContext()
ctx.setContextProperty("vertexModel", VertexModel(notifier))
ctx.setContextProperty("listModel", ListModel(notifier))
ctx.setContextProperty("renderModel", RenderModel(notifier))
```

QML files reference these by name (`vertexModel.value`,
`listModel.entries`) — no Python imports, no QML/C++ type registration
in the application itself.

### Live preview — the `TransientNotifier`

QML controls (sliders, color pickers, draggable handles) emit a flood of
intermediate values that should not each become a commit. ge-qml uses a
**transient channel** — `TransientNotifier` — for the in-flight values,
and only calls `dispatch` on release.

```python
@Slot(QColor)
def previewColor(self, color: QColor):  # while the picker is open
    TransientNotifier.instance().notify_vertex_color(self._vertex_key, color)


@Slot(QColor)
def setColor(self, new_color: QColor):  # when the user accepts
    self._context.store.dispatch(
        f"Set Color For Vertex '{self._value}'",
        lambda m: attachments.graph_vertex_visual_attributes_set_color(
            m, self._vertex_key, _to_graph_color(new_color)))
```

Render and panels subscribe to `TransientNotifier` for the live preview
and to the store for the committed state. The two channels never mix —
only `dispatch` writes to the DAG.

## Business logic — `model/`

Identical role and almost identical code to ge-py: pure-Python functions
taking an `AttachmentMutating` plus the keys/values they need, returning
the keys they create.

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

`model/` modules import from `ge/` (the generated layer); the bridge
models import from `model/` and `ge/`. The dependency graph still flows
in one direction.

## Generated data — `ge/`

`graph_editor/ge/` is the Kibo Python output for the Graph DSM model —
same structure as ge-py:

| File                | Purpose                                                |
|---------------------|--------------------------------------------------------|
| `ge/data.py`        | Concept keys (`Graph_VertexKey`), structures, enums    |
| `ge/attachments.py` | Typed accessors (`graph_vertex_visual_attributes_set`) |
| `ge/definitions.py` | Embedded DSM definitions, loaded into the database     |
| `ge/value_type.py`  | Type registry helpers                                  |
| `ge/path.py`        | Field paths                                            |
| `ge/resources.py`   | Embedded definitions (base64 blob)                     |

Regenerated from the DSM model and never edited by hand. The mapping
follows [Kibo's naming conventions](../kibo/index.rst).

## Notification flow

QML's automatic property bindings make the redraw step implicit: once a
bridge model emits `xChanged`, every QML expression reading `model.x`
re-evaluates, and the affected items repaint. The flow:

```text
QML control  ──►  model.someSlot(value)
                       │
                       ▼
                 store.dispatch(label, λ)
                       │
                       ▼
                  λ(mutating)            ← business logic runs here
                       │
                       ▼
            store.commit_mutations()     ← persisted to the DAG
                       │
                       ▼
       store.notify_state_did_change()   ← Python signal
                       │
                       ▼
       VertexModel._configure()          ← re-reads state, emits Changed
                       │
                       ▼
        QML bindings re-evaluate         ← UI updates implicitly
```

The bridge is where the imperative Python world meets the declarative
QML world. Below it, everything is identical to ge-py.

## What dsviper-components-qml ships with the application

As in ge-py, the application **inherits a complete suite of
administration, collaboration and scripting features by importing from
`dsviper-components-qml`**. None of this code lives in ge-qml — `main.py`
instantiates the model classes and exposes them to QML; the QML side
does no Python-specific wiring.

This is the same load-bearing observation as in ge-py: adopting the
shared library gives a new application a database inspector, a commit-DAG
browser, an undo-stack viewer, a remote-server sync pipeline, and an
embedded Python REPL — all already implemented.

### The Admin model — database introspection and history

`CommitAdminModel` is a single black-box `QObject` that owns the entire
admin surface (notifier setup, settings, undo, actions, program, commits,
live mode, blobs, inspector). `main.py` instantiates it once and
registers its context properties:

```python
# main.py
commit_admin = CommitAdminModel(mgr, app, context.store,
                                on_reset_database=context.reset)
commit_admin.registerContextProperties(engine)
```

QML pulls in the corresponding `dsviper_components_qml` QML files
(commit dialogs, inspector, undo viewer…) and binds against the
properties exposed by `CommitAdminModel`. The application has nothing
domain-specific to wire — toggling visibility is the only handler it
writes.

### The Documents panel

`DocumentsPanelModel` is the QML equivalent of ge-py's
`DSCommitDocumentsDialog` — it owns abstraction / key / document /
navigation state, and `main.py` exposes it the same way:

```python
documents_panel = DocumentsPanelModel(mgr, commit_mode=True)
documents_panel.registerContextProperties(engine)
```

ge-qml's `RenderModel` wires its `inspectKey` signal into the
documents panel so that "Inspect this vertex" from the canvas
focuses the corresponding key in the panel:

```python
render_model.inspectKey.connect(documents_panel.navigateToKey)
```

### Embedded Python scripting — `PythonEditorModel`

Same pattern as ge-py's `DSCodeEditorDialog`, exposed to QML through a
single model. `main.py` builds it with the application's `Context` in the
script namespace:

```python
from dsviper_components_qml.python_editor_model import PythonEditorModel

scripts_folder = str(Path(__file__).parent / "scripts")
python_editor_model = PythonEditorModel(scripts_folder, namespace_vars={
    "ctx": context,
    "render_model": render_model,
    "_documents_panel": documents_panel,
})
ctx.setContextProperty("pythonEditorModel", python_editor_model)
# ...
python_editor_model.runInitScript()
```

Scripts execute in the live interpreter and can drive the application
through `ctx.dispatch("label", lambda m: …)` — every script ends up as a
single commit in the DAG, replayable and undoable like any other
operation.

For the catalogue of model classes and the conventions for instantiating
each one, see [dsviper-components](../dsviper-components/index.rst). The
model-agnostic limit case — generic database editors with no DSM model of
their own — is walked through in [cdbe](cdbe.md).

## Where to read first

1. `graph_editor/main.py` — the wiring spine: `Context`, the admin /
   documents / scripting models, the domain bridge models, and the QML
   engine boot.
2. `graph_editor/model/context.py` — the singleton facade and database
   lifecycle (compare side-by-side with ge-py's `model/context.py`).
3. `graph_editor/vertex_model.py` — a complete bridge model:
   Properties, Slots, notifier subscription, `TransientNotifier`
   preview, dispatch.
4. `graph_editor/GraphVertexPanel.qml` — how QML binds to a bridge
   model (`vertexModel.value`, `vertexModel.setValue(...)`).
5. `graph_editor/Main.qml` — menus, layout, and the Admin / Documents
   / Editor menus assembled from the shared library.

## Reference

* [DSM](../dsm/index.rst) — the language ge-qml's data model is written in.
* [Kibo](../kibo/index.rst) — the generator that produces `ge/`.
* [dsviper](../dsviper/index.rst) — the runtime exercised through
  `Context.store`.
* [dsviper-components](../dsviper-components/index.rst) — the shared
  widget / QML library the UI is built on.
* [ge-py](ge-py.md) — the Qt Widgets sibling of this application.
