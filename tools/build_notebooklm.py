#!/usr/bin/env python3
"""Build NotebookLM-friendly Markdown bundles from Sphinx markdown output.

Produces a small set of concatenated .md files under build/notebooklm/, one
per top-level section of the documentation. Each original page is preceded by
a `<!-- FILE: <relative-path> -->` marker so NotebookLM can cite precise
sources while keeping the bundle valid Markdown.

Auto-generated API stub pages under python/api/generated/ are excluded: they
are noisy reference material that does not help conversational Q&A. The 11
curated python/api/*.md category pages are kept inside the Python guide
bundle.

Usage:
    python tools/build_notebooklm.py
    make notebooklm
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Bundle:
    name: str
    roots: tuple[str, ...]
    exclude: Callable[[Path], bool] = field(default=lambda _: False)


BUNDLES: tuple[Bundle, ...] = (
    Bundle("devkit-overview", ("index.md",)),
    Bundle("devkit-dsm", ("dsm",)),
    Bundle(
        "devkit-python-guide",
        ("python",),
        exclude=lambda p: "api/generated" in p.as_posix(),
    ),
    Bundle("devkit-tools", ("tools",)),
)


def collect_files(src_dir: Path, bundle: Bundle) -> list[Path]:
    files: list[Path] = []
    for root in bundle.roots:
        target = src_dir / root
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files.extend(sorted(target.rglob("*.md")))
    return [f for f in files if not bundle.exclude(f.relative_to(src_dir))]


def write_bundle(out_path: Path, src_dir: Path, files: list[Path]) -> None:
    with out_path.open("w", encoding="utf-8") as out:
        for f in files:
            rel = f.relative_to(src_dir).as_posix()
            out.write(f"\n\n<!-- FILE: {rel} -->\n\n")
            out.write(f.read_text(encoding="utf-8"))


def main() -> int:
    source_dir = Path(os.environ.get("SOURCE_DIR", "source"))
    build_dir = Path(os.environ.get("BUILD_DIR", "build"))
    md_dir = build_dir / "markdown"
    out_dir = build_dir / "notebooklm"

    print(f"running sphinx-build -b markdown → {md_dir}/")
    subprocess.run(
        ["sphinx-build", "-b", "markdown", str(source_dir), str(md_dir)],
        check=True,
    )

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"writing bundles to {out_dir}/")
    for bundle in BUNDLES:
        files = collect_files(md_dir, bundle)
        out_path = out_dir / f"{bundle.name}.md"
        write_bundle(out_path, md_dir, files)
        size_kb = out_path.stat().st_size / 1024
        word_count = sum(len(f.read_text(encoding="utf-8").split()) for f in files)
        print(f"  {bundle.name}.md  {size_kb:>7.1f} KB  {word_count:>7} words  ({len(files)} pages)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
