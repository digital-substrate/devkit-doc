# web-cdbe

Flask web application that demonstrates a **generic Commit Database
Editor** built directly on top of `dsviper`. Pure HTML5, no JavaScript:
every interaction is a normal browser navigation or a `POST` form.

The canonical generic Commit Database Editor is the Qt Widgets tool
[`cdbe.py`](../dsviper-tools/editors.md), shipped in `dsviper-tools` —
that is the full-featured production editor. `web-cdbe` is a derived
demonstration of the same idea, deliberately reduced to a minimum
surface so the runtime API is visible without the framework noise of a
desktop GUI.

* **Source repository** —
  [`digital-substrate/web-cdbe`](https://github.com/digital-substrate/web-cdbe).
* **Entry point** — `app.py`.
* **Dependencies** — `flask >= 3.0`, `dsviper >= 1.2.7` (from PyPI).

## What it demonstrates

Unlike `ge-py` / `ge-qml`, web-cdbe is **not specialised for a particular
DSM model**. It opens any commit database and reads its schema at
runtime through dsviper's introspection API — there is no Kibo-generated
package, no hand-written business logic, no domain widgets.

| Layer        | Where in web-cdbe                            | DevKit doc                                          |
|--------------|----------------------------------------------|-----------------------------------------------------|
| Schema       | `definitions()` from any opened database     | [DSM](../dsm/index.rst) (the language behind it)    |
| Runtime      | `CommitDatabase`, `CommitMutableState`       | [dsviper](../dsviper/index.rst)                     |
| Rendering    | `DocumentNode` tree → HTML in Python         | [dsviper](../dsviper/index.rst) (DocumentNode API)  |
| Mutation     | `attachment_mutating().update(...)` + commit | [dsviper](../dsviper/index.rst) (CommitMutableState)|

The takeaway: a working editor for **any** commit database in ~450
lines of Python plus three Jinja templates. The same introspection API
powers `dsviper-tools` (Qt Widgets, including `cdbe.py`) and
`dsviper-tools-qml`; web-cdbe is the browser-shaped sibling.

## Architecture

```text
┌──────────────────────────────────────────────────────────┐
│  Browser                                                 │
│     HTML5 + CSS only — no JavaScript                     │
├──────────────────────────────────────────────────────────┤
│  Flask routes (app.py)                                   │
│     /, /keys/<a>, /documents/<a>/<c>/<i>, POST /update   │
├──────────────────────────────────────────────────────────┤
│  HTML rendering (html_documents_renderer.py)             │
│     DocumentNode tree → <details>/<form> tree            │
├──────────────────────────────────────────────────────────┤
│  dsviper Runtime                                         │
│     CommitDatabase, definitions, AttachmentGetting,      │
│     DocumentNode, CommitMutableState                     │
└──────────────────────────────────────────────────────────┘
```

There is no service layer between Flask and dsviper; each request opens
the database, reads the last commit, renders or mutates, and returns.

## Repository layout

```text
web-cdbe/
├── app.py                       # Flask routes and request handlers
├── html_documents_renderer.py   # DocumentNode → HTML (forms + <details>)
├── html_renderer.py             # Small span/keyword/uuid helpers
├── templates/
│   ├── abstractions.html        # Top-level: list of concept / club types
│   ├── keys.html                # Instances of one abstraction
│   └── documents.html           # Editable attachments of one instance
├── static/
│   └── style.css                # Syntax-style colouring for values
├── database.link                # Symlink to the .rapmc / .graph database
└── requirements.txt
```

## Pointing the server at a database

`app.py` reads the database through a `database.link` symlink in the
project root — there is no config file:

```bash
ln -sf ~/Databases/Raptor/demo_sync_server.rapmc database.link
flask run --debug
```

If the symlink is missing, the server prints two example invocations
and exits. This keeps the demo decoupled from any hard-coded path while
still allowing different `.rapmc` / `.graph` databases to be swapped in
without restarting the editor more than once.

## Three views, one introspection chain

Each route is a thin wrapper around a step of the dsviper introspection
API.

### `/` — abstractions

The landing page lists every editable top-level type in the database
(concepts, clubs, and the `ANY_CONCEPT` attachment if present), sorted
by representation:

```python
# app.py — abstractions
@app.get('/')
def abstractions():
    db = CommitDatabase.open(FILENAME)
    definitions = db.definitions()
    types = []
    for concept in definitions.concepts():
        types.append(concept)
    for club in definitions.clubs():
        types.append(club)
    for attachment in definitions.attachments():
        if attachment.key_type() == Type.ANY_CONCEPT:
            types.append(Type.ANY_CONCEPT)
            break
    types.sort(key=lambda t: t.representation())
    return render_template("abstractions.html", types=types)
```

Each row links to `/keys/<abstraction_runtime_id>`. The `runtime_id` is
the stable type identifier dsviper assigns to every concept / club —
re-resolvable on the next request via `definitions.check_type(...)`.

### `/keys/<a>` — instances of one type

```python
# app.py — keys (excerpt)
abstraction_runtime_id = ValueUUId.create(str(abstraction_runtime_id))
db = CommitDatabase.open(FILENAME)
definitions = db.definitions()
viper_type = definitions.check_type(abstraction_runtime_id)
type_key = TypeKey(viper_type)
collected_keys = ValueSet(TypeSet(type_key))
attachment_getting = db.state(db.last_commit_id()).attachment_getting()

for attachment in definitions.attachments():
    if attachment.type_key() == type_key:
        collected_keys |= attachment_getting.keys(attachment)
```

The route gathers every `ValueKey` referenced by an attachment whose
key-type matches the requested abstraction, then asks a `KeyNamer` for
a human-readable name for each one. The result is a flat table of
`(instance_id, name)` pairs linking to the document view.

### `/documents/<a>/<c>/<i>` — editable attachments

The document view materialises an instance as a `DocumentNode` tree
rooted at its `ValueKey`:

```python
# app.py — documents (excerpt)
attachment_getting = db.state(db.last_commit_id()).attachment_getting()
doc = DocumentNode.create_documents(key, attachment_getting)
renderer = HtmlDocumentsRenderer(doc, abstraction_runtime_id,
                                 key_namer, attachment_getting)
content = renderer.html()
```

`DocumentNode.create_documents(...)` is the same tree that the Qt
Widgets `DSDocumentsCommitStore` and the QML `DocumentsPanel` consume —
web-cdbe is just another renderer on top of it.

## Rendering: `DocumentNode` → HTML

`html_documents_renderer.py` walks the node tree and emits two kinds of
elements:

* **Expandable nodes** become `<details>` blocks with a `<summary>`
  showing the field name and (for collections) the value count. The
  current path is rendered with `open`, the rest collapsed.
* **Leaf nodes** become a `<div>` with either a read-only value or a
  small `<form method="post" action="/update">` carrying the four
  identifiers Flask needs to round-trip the mutation.

```python
# html_documents_renderer.py — render_value (excerpt)
if editable:
    self.write(f'<form method="post" action="{url_for("update")}"…>')
    self.write(f'<input type="hidden" name="abstraction_runtime_id" …/>')
    self.write(f'<input type="hidden" name="concept_runtime_id" …/>')
    self.write(f'<input type="hidden" name="instance_id" …/>')
    self.write(f'<input type="hidden" name="node_uuid" …/>')

    if node.is_boolean():     self.render_value_boolean(node)
    elif node.is_integer():   self.render_value_integer(node)
    elif node.is_real():      self.render_value_real(node)
    elif node.is_string():    self.render_value_string(node)
    elif node.is_enumeration(): self.render_value_enumeration(node)

    self.write("<button type='submit' class='update'>Update</button>")
    self.write(f'</form>')
```

Integer inputs honour the underlying signed / unsigned width
(`uint8` → `min=0 max=255`, `int32` → `min=-2147483648 max=2147483647`,
etc.), so the browser does the first-pass validation for free.

Cross-instance references rendered as `ValueKey` become hyperlinks back
into `/documents/...`, which is what lets the user navigate the graph
of attachments by clicking through.

## The update round-trip

A successful field edit is a single `POST /update` with five form
fields: the three identifiers locating the instance, the `node_uuid`
locating the node inside its `DocumentNode` tree, and the new `value`.

```python
# app.py — update (excerpt)
db = CommitDatabase.open(FILENAME)
definitions = db.definitions()
concept = definitions.check_concept(concept_runtime_id)
key = ValueKey.create(concept, instance_id)
attachment_getting = db.state(db.last_commit_id()).attachment_getting()
doc = DocumentNode.create_documents(key, attachment_getting)

node = find_node(node_uuid, doc)
if node:
    value = value_to_python(node, value)
    state = db.state(db.last_commit_id())
    mutable_state = CommitMutableState(state)
    mutable_state.attachment_mutating().update(
        node.attachment(), node.key(),
        node.path().regularized().const(), value)
    db.commit_mutations("Update From The Web", mutable_state)

return redirect(url_for("documents_node", ...))
```

This is the **canonical edit-commit pattern** that every dsviper
application repeats: open the current state, derive a
`CommitMutableState`, ask `attachment_mutating().update(...)` to apply
the change at a node path, then `commit_mutations(message, state)`.
The commit message — `"Update From The Web"` here — shows up in the
database's commit history exactly like any other client's mutation.

`value_to_python(node, value)` coerces the raw form string into the
Python type the node expects (`bool`, `int`, `float`, `str`); the
typed `update(...)` call enforces the rest at the dsviper layer.

After commit, the response is a `redirect` back to
`/documents_node/<a>/<c>/<i>/<node_uuid>`. This rerenders the document
with the edited node's subtree left `open`, so the user keeps their
place in the tree — without a single line of JavaScript.

## Why "no JavaScript" is the point

Removing JavaScript is not a stylistic choice; it makes web-cdbe the
**minimum-surface demonstration** of the dsviper runtime in a web
context:

* No client-side framework, no build step, no transpiler — only Python,
  Flask, Jinja, and the browser's native form handling.
* Every state transition is a normal HTTP request, so the server is the
  single source of truth and the commit DAG is the only state machine.
* Anyone with a copy of dsviper can run the demo against their own
  database and immediately see what's stored, what's editable, and what
  changing it looks like in commit history.

## Where to read first

1. `app.py` lines around `abstractions` — the entry point and how the
   schema is discovered.
2. `app.py` lines around `documents` — how a `DocumentNode` tree is
   built from a `ValueKey`.
3. `html_documents_renderer.py` `render_value` — leaf nodes that
   become editable HTML forms.
4. `app.py` lines around `update` — the open / mutate / commit
   sequence every dsviper application repeats.

## Reference

* [dsviper](../dsviper/index.rst) — the runtime web-cdbe is built on,
  including `CommitDatabase`, `CommitMutableState`, and `DocumentNode`.
* [DSM](../dsm/index.rst) — the modelling language whose definitions
  are read back here through `db.definitions()`.
