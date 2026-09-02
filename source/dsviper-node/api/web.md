# HTML Rendering

Two classes turn a Viper document into HTML. `DocumentNode` walks a document as a
typed tree, carrying the metadata a renderer needs — component name, value,
editability, and the concrete type behind each leaf. `Html` renders, either the whole
tree in one call or one piece at a time.

**When to use**: reach for {js:class}`Html` when the default rendering will do, and
for {js:class}`DocumentNode` directly when the markup is yours — a form, a custom
layout, a template engine's data. Nothing here is browser-specific: the same tree
feeds a server-rendered page, and the Qt widgets do the same thing with it.

## Quick Start

An Express route rendering one document as a collapsible tree:

```js
const express = require('express');
const { CommitDatabase, CommitStateBuilder, DocumentNode, Html, ValueKey } =
    require('@digitalsubstrate/dsviper');

const app = express();

app.get('/document/:instanceId', (req, res) => {
    const db = CommitDatabase.open('model.cdb');
    try {
        const key = ValueKey.create(concept, ValueUUId.create(req.params.instanceId));
        const getting = CommitStateBuilder.state(db, db.lastCommitId()).attachmentGetting();

        // Build the document tree for every attachment on that key.
        const nodes = DocumentNode.createDocuments(key, getting);

        res.send(Html.document('Document', Html.style(),
                               Html.body(Html.documentsDetails(nodes, true))));
    } finally { db.close(); }
});
```

`Html.style()` returns the stylesheet the other helpers assume, `Html.body()` wraps
content, and `Html.document()` assembles a standalone page — so a working page needs
no CSS of its own.

## Walking the tree yourself

`DocumentNode` answers what a renderer needs to decide, so a custom renderer is a
recursion over predicates:

```js
function renderNode(node, level = 0) {
    if (node.isExpandable()) {
        const children = node.children().map((c) => renderNode(c, level + 1)).join('');
        return `<details open><summary>${node.stringComponent()}</summary>${children}</details>`;
    }
    if (node.isEditable()) {
        if (node.isBoolean()) return checkbox(node);
        if (node.isEnumeration()) return select(node);
        if (node.isString()) return textInput(node);
    }
    return `<div>${node.stringComponent()} = ${node.stringValue()}</div>`;
}
```

The predicate family is wide — `isPrimitive`, `isCollection`, `isKey`, `isNumeric`
and the exact-width `isInt32` / `isUint64` / `isFloat` … — so a renderer can be as
coarse or as precise as it needs. `Html.type(node.value().type())` renders the type
itself when a column should show it.

```{seealso}
`dsviper-node-web-cdbe` is a complete worked example: an Express Commit Database
Editor, pure HTML5 with no client JavaScript, built on exactly these two classes.
Its Python twin `dsviper-web-cdbe` renders the same tree through Flask.
```

## Key classes

| Class | Purpose | Example |
|-------|---------|---------|
| {js:class}`DocumentNode` | A document as a typed, walkable tree | `DocumentNode.createDocuments(key, getting)` |
| {js:class}`Html` | Render values, types, documents, or a whole page | `Html.documentsDetails(nodes, true)` |

The mirror of this page for the Python binding is {doc}`../../dsviper-python/api/web`.

## Classes

| Class | Description |
|-------|-------------|
| {js:class}`DocumentNode` | A class used to represent a node in the tree representation of a value |
| {js:class}`Html` | A class used to generate HTML representation |

## Reference

```{js:autoclass} DocumentNode
:members:
```

```{js:autoclass} Html
:members:
```

