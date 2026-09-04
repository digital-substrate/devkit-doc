"""Sphinx extension: the Node twin of ``autosummary``.

The Python API pages list their classes with ``autosummary``, which reads the
installed module and writes the summary column itself. The Node pages had no
equivalent, so the same column was copied by hand into 268 Markdown rows while
the prototypes below them came from TypeDoc. Two sources for one fact: the
halves of a page drift apart silently, and both look plausible.

This directive restores the ``autosummary`` contract on the Node side. The page
still lists the class names — the grouping into rubrics is editorial and worth
writing — and the description is read from the same ``index.d.ts`` sphinx-js is
pointed at, so a JSDoc edit reaches the table and the prototype together.

Usage, in MyST::

    ```{js-summary}
    TypeVoid
    TypeBool
    ```
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from docutils.parsers.rst import Directive
from docutils.statemachine import StringList

CLASS_DOC = re.compile(
    r"/\*\*((?:[^*]|\*(?!/))*)\*/\s*export (?:declare )?class ([A-Za-z_0-9]+)\b"
)

_summaries: dict[str, str] = {}


def _first_sentence(jsdoc: str) -> str:
    """The summary column: the first sentence of the JSDoc's first paragraph.

    Matches what ``autosummary`` takes from a Python docstring, so the two
    references read the same way.
    """
    body = " ".join(l.lstrip().lstrip("*").strip() for l in jsdoc.splitlines()).strip()
    paragraph = re.split(r"\s{2,}", body)[0]
    m = re.match(r"(.*?[.!?])(?:\s|$)", paragraph)
    return (m.group(1) if m else paragraph).strip().rstrip(".")


def load_summaries(app: Any) -> None:
    """Read every class JSDoc from the .d.ts sphinx-js was given."""
    source = getattr(app.config, "js_source_path", None)
    if isinstance(source, (list, tuple)):
        source = source[0] if source else None
    if not source:
        return
    path = Path(source)
    if path.is_dir():
        path = path / "index.d.ts"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    _summaries.clear()
    for m in CLASS_DOC.finditer(text):
        _summaries[m.group(2)] = _first_sentence(m.group(1))


class JsSummary(Directive):
    has_content = True

    def run(self):
        names = [n.strip() for n in self.content if n.strip()]
        rows = ["| Class | Description |", "|-------|-------------|"]
        for name in names:
            summary = _summaries.get(name)
            if summary is None:
                # a name the .d.ts does not carry is a page pointing at nothing;
                # say so on the page rather than rendering a blank cell
                self.state.document.reporter.warning(
                    f"js-summary: no class {name!r} in the TypeScript declarations",
                    line=self.lineno,
                )
                summary = ""
            # a quoted type expression is read as a link target inside a table
            summary = re.sub(r"'([^']*<[^']*>)'", r"`\1`", summary)
            rows.append(f"| {{js:class}}`{name}` | {summary} |")
        node = self.state.document.__class__("", self.state.document.settings)
        self.state.nested_parse(StringList(rows, source=""), self.content_offset, node)
        return node.children


def setup(app: Any) -> dict[str, Any]:
    app.connect("builder-inited", load_summaries)
    app.add_directive("js-summary", JsSummary)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
