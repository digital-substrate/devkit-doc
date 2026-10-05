"""Mark every page of a deprecated section with the same notice, under its title.

The kibo-1/ section documents kibo 1, which is deprecated. Writing the notice into each
page would copy one text a dozen times; this inserts it at read time, after the page's
title so that the title stays the page's first element.
"""

from __future__ import annotations

import re

NOTICE = (
    "Kibo 1 is deprecated. It receives fixes only, for the life of the LTS-1.2 line. "
    "New projects generate with kibo 2; existing projects move with the migration guides."
)

SECTIONS = {
    "kibo-1/": NOTICE,
}


def _links(docname: str, markdown: bool) -> str:
    depth = docname.count("/")
    up = "../" * depth
    if markdown:
        return (f"See {{doc}}`kibo 2 <{up}kibo/index>`, "
                f"{{doc}}`moving a template pack <{up}kibo/migrating>` and "
                f"{{doc}}`moving application code <{up}using-generated-sdk/migrating>`.")
    return (f"See :doc:`kibo 2 <{up}kibo/index>`, "
            f":doc:`moving a template pack <{up}kibo/migrating>` and "
            f":doc:`moving application code <{up}using-generated-sdk/migrating>`.")


def _insert_after_title(text: str, block: str, markdown: bool) -> str:
    if markdown:
        m = re.search(r"^# .*\n", text, re.M)
    else:
        m = re.search(r"^[^\n]+\n(=+|-+|\*+|#+)\n", text, re.M)
    if not m:
        return block + "\n" + text
    return text[:m.end()] + "\n" + block + "\n" + text[m.end():]


def on_source_read(app, docname: str, source: list[str]) -> None:
    for prefix, notice in SECTIONS.items():
        if not docname.startswith(prefix):
            continue
        markdown = app.env.doc2path(docname).suffix == ".md"
        if markdown:
            block = f"```{{warning}}\n{notice} {_links(docname, True)}\n```\n"
        else:
            block = f".. warning::\n\n   {notice} {_links(docname, False)}\n"
        source[0] = _insert_after_title(source[0], block, markdown)


def setup(app):
    app.connect("source-read", on_source_read)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
