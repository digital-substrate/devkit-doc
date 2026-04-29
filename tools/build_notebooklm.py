#!/usr/bin/env python3
"""Build NotebookLM-friendly text bundles from Sphinx text builder output.

Produces a small set of concatenated .txt files under build/notebooklm/, one
per top-level section of the documentation. Each original page is preceded by
a `FILE: <relative-path>` header so NotebookLM can cite precise sources.

Auto-generated API stub pages under python/api/generated/ are excluded: they
are noisy reference material that does not help conversational Q&A. The 11
curated python/api/*.txt category pages are kept inside the Python guide
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

SEPARATOR = "=" * 50


@dataclass(frozen=True)
class Bundle:
    name: str
    roots: tuple[str, ...]
    exclude: Callable[[Path], bool] = field(default=lambda _: False)


BUNDLES: tuple[Bundle, ...] = (
    Bundle("devkit-overview", ("index.txt",)),
    Bundle("devkit-dsm", ("dsm",)),
    Bundle(
        "devkit-python-guide",
        ("python",),
        exclude=lambda p: "api/generated" in p.as_posix(),
    ),
    Bundle("devkit-tools", ("tools",)),
)


def collect_files(text_dir: Path, bundle: Bundle) -> list[Path]:
    files: list[Path] = []
    for root in bundle.roots:
        target = text_dir / root
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files.extend(sorted(target.rglob("*.txt")))
    return [f for f in files if not bundle.exclude(f.relative_to(text_dir))]


def write_bundle(out_path: Path, text_dir: Path, files: list[Path]) -> None:
    with out_path.open("w", encoding="utf-8") as out:
        for f in files:
            rel = f.relative_to(text_dir).as_posix()
            out.write(f"\n\n{SEPARATOR}\nFILE: {rel}\n{SEPARATOR}\n\n")
            out.write(f.read_text(encoding="utf-8"))


def main() -> int:
    source_dir = Path(os.environ.get("SOURCE_DIR", "source"))
    build_dir = Path(os.environ.get("BUILD_DIR", "build"))
    text_dir = build_dir / "text"
    out_dir = build_dir / "notebooklm"

    print(f"running sphinx-build -b text → {text_dir}/")
    subprocess.run(
        ["sphinx-build", "-b", "text", str(source_dir), str(text_dir)],
        check=True,
    )

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"writing bundles to {out_dir}/")
    for bundle in BUNDLES:
        files = collect_files(text_dir, bundle)
        out_path = out_dir / f"{bundle.name}.txt"
        write_bundle(out_path, text_dir, files)
        size_kb = out_path.stat().st_size / 1024
        word_count = sum(len(f.read_text(encoding="utf-8").split()) for f in files)
        print(f"  {bundle.name}.txt  {size_kb:>7.1f} KB  {word_count:>7} words  ({len(files)} pages)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
