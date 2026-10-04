# dsviper-ge-qml

PySide6 + QML desktop application — the QML port of [dsviper-ge](dsviper-ge.md). Same
DSM model, same generated `gei/` package, same hand-written `ge/`
business logic, same `CommitStore` facade. The UI is QML, driven by Python
`QObject` models registered as QML context properties. Built on the Qt
Quick variant of `dsviper-components`.

* **Source repository** —
  [`digital-substrate/dsviper-ge-qml`](https://github.com/digital-substrate/dsviper-ge-qml).
* **Entry point** — `graph_editor.py` (shim that runs `graph_editor/main.py`).
* **Dependencies** — `PySide6` (Qt Quick + Quick Controls + Dialogs), `dsviper` (from PyPI).

## What it demonstrates

dsviper-ge-qml is the same value-chain walk-through as dsviper-ge, swapping Qt Widgets
for Qt Quick:

| Layer      | Where in dsviper-ge-qml                           | DevKit doc                                            |
|------------|-------------------------------------------|-------------------------------------------------------|
| DSM model  | DSM definitions of the Graph              | [DSM](../dsm/index.rst)                               |
| Code-gen   | `graph_editor/gei/` package (Kibo output) | [Kibo](../kibo/index.rst), [Python SDK](../using-generated-sdk/python.md) |
| Runtime    | `dsviper.CommitStore` usage               | [dsviper](../dsviper-python/index.rst)                       |
| Shared QML | `dsviper_components_qml/` (vendored copy) | [dsviper-components](../dsviper-components/index.rst) |

The interesting comparison with dsviper-ge is what changes — and what doesn't —
when the UI moves from imperative widgets to declarative QML. `ge/`,
`gei/`, and `Context` are essentially identical to dsviper-ge: the entire
business stack is reused.

## Architecture

QML adds one layer above dsviper-ge's five-layer stack — a thin **QObject
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
│     ge/context.py — singleton wrapping CommitStore          │
├─────────────────────────────────────────────────────────────┤
│  4. Business Logic (hand-written Python)                    │
│     ge/*.py — vertex.py, graph.py, selection_*.py, …        │
├─────────────────────────────────────────────────────────────┤
│  5. Generated Data (Kibo output)                            │
│     gei/ — the graph unit, containers, definitions()        │
├─────────────────────────────────────────────────────────────┤
│  6. dsviper Runtime                                         │
│     CommitDatabase, CommitStore, CommitMutableState, Value  │
└─────────────────────────────────────────────────────────────┘
```

The bridge layer is what makes a QML application different from a Widgets
application — and why the `ge/` and `gei/` layers are shareable with
dsviper-ge: `gei/` is generated identically in both, and of `ge/` only
`context.py` differs — a few comments and one extra scripting facade method.

## Repository layout

```text
dsviper-ge-qml/
├── graph_editor.py             # Entry-point shim — runs graph_editor/main.py
├── graph_editor/               # Application package
│   ├── main.py                 # QApplication + QQmlApplicationEngine setup
│   ├── Main.qml                # Root window (menus, layout)
│   ├── Graph*Panel.qml         # Domain panels (vertex, list, tags, comments, render)
│   ├── *_model.py              # QObject bridges exposed to QML
│   ├── transient_notifier.py   # Live-preview channel (illusion pattern)
│   ├── gei/                    # Kibo-generated infrastructure (same as dsviper-ge)
│   ├── ge/                     # Hand-written business logic (same as dsviper-ge)
│   │   ├── context.py          # Singleton: store + graph_key + facade
│   │   ├── graph.py, vertex.py, edge.py, …
│   │   └── script_*.py         # Reusable scripts
│   ├── render/                 # 2-D canvas (paint, hit-testing)
│   ├── list/                   # List-view items
│   ├── scripts/                # User-editable Python scripts (run from the embedded editor)
│   └── images/                 # App icon and assets
├── dsviper_components_qml/     # Vendored copy of dsviper-components-qml
│                               #   (synced with dev/sync_dsviper_components_qml.py)
└── kibo.toml                   # How graph_editor/gei is generated from the DSM model
```

The shim at the repo root keeps `python3 graph_editor.py` working from any
directory; the real entry point is `graph_editor/main.py`.

## The Context singleton

`graph_editor/ge/context.py` is identical in spirit (and almost
character-for-character) to dsviper-ge's `Context`. Same singleton, same
`CommitStore`, same `graph.GraphKey`, same `use(database)` lifecycle,
same `dispatch` / `undo` / `redo` facade for scripting.

```python
from dsviper import CommitStore, CommitDatabase, CommitStateBuilder, CommitState, CommitMutableState, ValueCommitId

from gei import definitions, graph
from gei.graph import attachments
from ge import graph as ge_graph


class Context:

    @classmethod
    def instance(cls) -> Context:
        if not hasattr(cls, "_instance"):
            setattr(cls, "_instance", cls())
        return getattr(cls, "_instance")

    def __init__(self):
        self.store = CommitStore()
        self.graph_key = graph.GraphKey.create()

    def use(self, database: CommitDatabase):
        if not database.commit_ids():
            self._create_initial_commit(database, CommitStateBuilder.initial_state(database))

        commit_id = database.last_commit_id()
        self.store.set_state(CommitStateBuilder.state(database, commit_id))
        self.store.set_database(database)
        self.store.notify_database_did_open()

        self.load()
```

That this file is essentially copy-pasted between dsviper-ge and dsviper-ge-qml is the
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
        lambda m: attachments.Vertex.visual_attributes.set_value(
            m, self._vertex_key, new_value))
```

```qml
// GraphVertexPanel.qml — preview while the stepper is held, commit on release
SpinBox {
    id: vertexValueSpinBox
    value: vertexModel.value
    editable: true
    property bool stepping: up.pressed || down.pressed
    onValueModified: {
        if (stepping)
            vertexModel.previewValue(value)
        else
            vertexModel.setValue(value)
    }
    onSteppingChanged: {
        if (!stepping)
            vertexModel.setValue(value)
    }
}
```

The body of the lambda is **plain Python** that calls into `ge/` and
the generated `gei.graph.attachments` API — exactly as in dsviper-ge:
`attachments.Vertex.visual_attributes.set_value` is the field operation `set_value` of
the attachment `visual_attributes`, keyed on the concept `Vertex`. The only
difference is the firing path: QML ➔ Slot ➔ dispatch ➔ business logic.

```{tip}
The dispatch label still drives the undo stack and the commit history.
The QML port keeps the same convention — labels describe user intent
(`"Set Value '7' For Vertex '3'"`), not implementation steps.
```

## The QObject bridge — `*_model.py`

This is the layer dsviper-ge does not have. Each `*_model.py` is a
`QObject` subclass that:

- exposes view-state as Qt **Properties** with `notify` signals — QML
  bindings track them automatically;
- exposes user actions as `@Slot` methods — QML calls them by name;
- subscribes to `CommitStore` notifications (`state_did_change`,
  `database_did_open`, `database_did_close`) and re-reads the state
  every time the store changes.

```python
# vertex_model.py — abridged
from ge.context import Context
from gei.graph import attachments
from gei import graph


class VertexModel(QObject):
    """Exposes vertex value/color/position to QML when exactly 1 vertex is selected."""

    valueChanged = Signal()
    # ...

    def __init__(self, notifier, parent=None):
        super().__init__(parent)
        self._context = Context.instance()
        self._vertex_key: graph.VertexKey | None = None
        self._value: int = 0
        # ...
        notifier.database_did_open.connect(self._on_database_did_open)
        notifier.database_did_close.connect(self._on_database_did_close)
        notifier.state_did_change.connect(self._configure)

    def _get_value(self) -> int:
        return self._value

    value = Property(int, _get_value, notify=valueChanged)

    @Slot(int)
    def setValue(self, new_value: int):
        if not self._vertex_key:
            return
        label = f"Set Value '{new_value}' For Vertex '{self._value}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.Vertex.visual_attributes.set_value(
                m, self._vertex_key, new_value))

    # _configure re-reads the state on every notification and emits the *Changed signals
```

`main.py` instantiates each model with the notifier from
`CommitAdminModel.notifier` and wires it to QML:

```python
notifier = commit_admin.notifier
list_model = ListModel(notifier)
vertex_model = VertexModel(notifier)
render_model = RenderModel(notifier)
# ...
ctx = engine.rootContext()
ctx.setContextProperty("listModel", list_model)
ctx.setContextProperty("vertexModel", vertex_model)
ctx.setContextProperty("renderModel", render_model)
```

QML files reference these by name (`vertexModel.value`,
`listModel.entries`) — no Python imports, no QML/C++ type registration
in the application itself.

### Live preview — the `TransientNotifier`

QML controls (sliders, color pickers, draggable handles) emit a flood of
intermediate values that should not each become a commit. dsviper-ge-qml uses a
**transient channel** — `TransientNotifier` — for the in-flight values,
and only calls `dispatch` on release.

```python
@Slot(QColor)
def setColor(self, new_color: QColor):
    if not self._vertex_key:
        return
    color = graph.Color()
    color.red = new_color.redF()
    color.green = new_color.greenF()
    color.blue = new_color.blueF()
    label = f"Set Color For Vertex '{self._value}'"
    self._context.store.dispatch(
        label,
        lambda m: attachments.Vertex.visual_attributes.set_color(
            m, self._vertex_key, color))

@Slot(QColor)
def previewColor(self, color: QColor):
    """Transient color preview"""
    if not self._vertex_key:
        return
    TransientNotifier.instance().notify_vertex_color(self._vertex_key, color)
```

Render and panels subscribe to `TransientNotifier` for the live preview
and to the store for the committed state. The two channels never mix —
only `dispatch` writes to the DAG.

## Business logic — `ge/`

Identical role and almost identical code to dsviper-ge: pure-Python functions
taking an `AttachmentMutating` plus the keys/values they need, returning
the keys they create.

```python
# ge/vertex.py
def add(attachment_mutating: AttachmentMutating,
        graph_key: graph.GraphKey,
        value: int,
        position: graph.Position,
        color: graph.Color) -> graph.VertexKey:

    vertex_key = create(attachment_mutating, value, position, color)

    vertex_keys = containers.Set_of_Graph_VertexKey()
    vertex_keys.add(vertex_key)
    attachments.Graph.topology.union_vertex_keys(attachment_mutating, graph_key, vertex_keys)

    return vertex_key
```

`ge/` modules import from `gei/` (the generated layer); the bridge
models import from `ge/` and `gei/`. The dependency graph still flows
in one direction.

## Generated data — `gei/`

`graph_editor/gei/` is the Kibo Python output for the Graph DSM model, generated with
kibo 2 and the kibo-template-viper 2.0 pack — the same package as dsviper-ge's. The
`kibo.toml` at the root of the repository declares it, with `output = "graph_editor"`,
and [kibo-project](../kibo/kibo-project.md) regenerates it after a model change
(`python3 ../kibo-project/kibo_project.py generate`):

| Name                      | What it is                                                      |
|---------------------------|-----------------------------------------------------------------|
| `gei.graph`               | The DSM namespace `Graph`: keys (`graph.VertexKey`), structures (`graph.Color`) |
| `gei.graph.attachments`   | The attachments, by concept: `attachments.Vertex.visual_attributes.set_color(…)` |
| `gei.containers`          | One class per container shape: `containers.Set_of_Graph_VertexKey` |
| `gei.definitions()`       | The model's definitions, loaded into the database               |
| `gei/resources.py`        | The embedded definitions `definitions()` decodes                |

Never edited by hand. The mapping from DSM names to Python identifiers is described in
[Using the generated SDK — Python](../using-generated-sdk/python.md).

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
QML world. Below it, everything is identical to dsviper-ge.

## What dsviper-components-qml ships with the application

As in dsviper-ge, the application **inherits a complete suite of
administration, sync, and scripting features by importing from
`dsviper-components-qml`**. None of this code lives in dsviper-ge-qml — `main.py`
instantiates the model classes and exposes them to QML; the QML side
does no Python-specific wiring.

This is the same load-bearing observation as in dsviper-ge: adopting the
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

`DocumentsPanelModel` is the QML equivalent of dsviper-ge's
`DSCommitDocumentsDialog` — it owns abstraction / key / document /
navigation state, and `main.py` exposes it the same way:

```python
documents_panel = DocumentsPanelModel(mgr, commit_mode=True)
documents_panel.registerContextProperties(engine)
```

dsviper-ge-qml's `RenderModel` wires its `inspectKey` signal into the
documents panel so that "Inspect this vertex" from the canvas
focuses the corresponding key in the panel:

```python
render_model.inspectKey.connect(documents_panel.navigateToKey)
```

### Embedded Python scripting — `PythonEditorModel`

Same pattern as dsviper-ge's `DSCodeEditorDialog`, exposed to QML through a
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
2. `graph_editor/ge/context.py` — the singleton facade and database
   lifecycle (compare side-by-side with dsviper-ge's `ge/context.py`).
3. `graph_editor/vertex_model.py` — a complete bridge model:
   Properties, Slots, notifier subscription, `TransientNotifier`
   preview, dispatch.
4. `graph_editor/GraphVertexPanel.qml` — how QML binds to a bridge
   model (`vertexModel.value`, `vertexModel.setValue(...)`).
5. `graph_editor/Main.qml` — menus, layout, and the Admin / Documents
   / Editor menus assembled from the shared library.

## Reference

* [DSM](../dsm/index.rst) — the language dsviper-ge-qml's data model is written in.
* [Kibo](../kibo/index.rst) — the generator that produces `gei/`, driven by
  [kibo-project](../kibo/kibo-project.md).
* [Using the generated SDK — Python](../using-generated-sdk/python.md) — the surface of `gei/`.
* [dsviper](../dsviper-python/index.rst) — the runtime exercised through
  `Context.store`.
* [dsviper-components](../dsviper-components/index.rst) — the shared
  widget / QML library the UI is built on.
* [dsviper-ge](dsviper-ge.md) — the Qt Widgets sibling of this application.
