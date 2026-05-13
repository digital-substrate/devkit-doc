#!/usr/bin/env python3
"""Build a Markdown corpus tuned for LLM ingestion (NotebookLM, agents).

Produces a small set of concatenated .md files under build/notebooklm/, one
per maillon of the value chain. Bundles are numerically prefixed so the
intended reading order — orientation first, then dependency-ordered deep
dives — is conveyed even when a tool ingests them out of order:

    00-devkit-ecosystem  Map: naming, value-chains, pipeline, glossary,
                         and reference-app GitHub URLs (an agent fetches
                         the actual app code from those repos on demand)
    10-devkit-dsm        The modeling language (chain entry point)
    20-devkit-kibo       Code generation (DSM → C++ / Python)
    30-devkit-dsviper    Python runtime: API and concepts
    35-devkit-commit     The Commit Engine: versioned persistence,
                         modes of use, dual-layer contract
    40-devkit-tools      Tools and UI components consuming dsviper

Each original page is preceded by a `<!-- FILE: <relative-path> -->` marker
so an LLM can cite precise sources while keeping the bundle valid Markdown.

Auto-generated API stub pages under dsviper/api/generated/ are excluded:
they are noisy reference material that does not help conversational Q&A.
The curated dsviper/api/*.md category pages are kept inside the dsviper
bundle. Legal notices are excluded entirely (not useful for Q&A).

Alongside the bundles the script writes:

  INDEX.md           — one-line description of each bundle plus its
                       size/word count, so an LLM can pick the right
                       bundle to open for a given question.
  LICENSE_AND_USE.md — copied verbatim from tools/notebooklm_assets/, so
                       the licensing and permitted-use perimeter travels
                       with the corpus.

Usage:
    python tools/build_notebooklm.py
    make notebooklm
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Bundle:
    name: str
    description: str
    roots: tuple[str, ...]
    exclude: Callable[[Path], bool] = field(default=lambda _: False)


BUNDLES: tuple[Bundle, ...] = (
    Bundle(
        "00-devkit-ecosystem",
        "Orientation — naming, value chains, pipeline, glossary, reference-app pointers. Start here.",
        ("index.md", "ecosystem", "reference-apps"),
    ),
    Bundle(
        "10-devkit-dsm",
        "DSM — the modeling language: concepts, types, attachments, function pools, code generation.",
        ("dsm",),
    ),
    Bundle(
        "20-devkit-kibo",
        "Kibo — code generation from DSM to C++ / Python (per-app Bridge); template authoring.",
        ("kibo", "kibo-template-viper"),
    ),
    Bundle(
        "30-devkit-dsviper",
        "dsviper — Python runtime: types, structures, collections, serialization, error model.",
        ("dsviper",),
        exclude=lambda p: "api/generated" in p.as_posix(),
    ),
    Bundle(
        "35-devkit-commit",
        "The Commit Engine — versioned persistence: DAG, modes of use, dual-layer contract.",
        ("commit",),
    ),
    Bundle(
        "40-devkit-tools",
        "Tools and UI components consuming dsviper: editors, dsm_util, server, widgets.",
        ("dsviper-tools", "dsviper-components"),
    ),
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


@dataclass(frozen=True)
class BundleStats:
    bundle: Bundle
    page_count: int
    size_kb: float
    word_count: int


def write_index(out_path: Path, stats: list[BundleStats]) -> None:
    lines = [
        "# DevKit Documentation Bundle — Index",
        "",
        "This archive contains the DevKit documentation as Markdown bundles tuned",
        "for LLM ingestion (NotebookLM, RAG pipelines, coding agents). Each bundle",
        "is a concatenation of the original doc pages; every page is preceded by a",
        "`<!-- FILE: <relative-path> -->` marker so you can cite precise sources.",
        "",
        "Bundles are numerically prefixed to convey the intended reading order:",
        "orientation first, then dependency-ordered deep dives.",
        "",
        "| Bundle | Topic | Pages | Size | Words |",
        "|---|---|---|---|---|",
    ]
    for s in stats:
        lines.append(
            f"| `{s.bundle.name}.md` | {s.bundle.description} | "
            f"{s.page_count} | {s.size_kb:.0f} KB | {s.word_count:,} |"
        )
    lines += [
        "",
        "## Other files in this archive",
        "",
        "- `INDEX.md` — this file.",
        "- `LICENSE_AND_USE.md` — licensing and permitted-use notice. Read this",
        "  before ingesting the corpus into a training pipeline.",
        "",
        "## Where to start",
        "",
        "Begin with `00-devkit-ecosystem.md` for a map of the project (naming,",
        "value chains, pipeline) before diving into a specific maillon. For a",
        "given question, the bundle descriptions above are written to let an LLM",
        "(or a human) decide which one to open first.",
        "",
        "## Canonical sources",
        "",
        "- Documentation: https://docs.digitalsubstrate.io/",
        "- DevKit downloads and release notes: https://devkit.digitalsubstrate.io/downloads/",
        "- dsviper on PyPI: https://pypi.org/project/dsviper/",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def copy_assets(assets_dir: Path, out_dir: Path) -> list[Path]:
    copied: list[Path] = []
    if not assets_dir.is_dir():
        return copied
    for asset in sorted(assets_dir.glob("*.md")):
        dest = out_dir / asset.name
        shutil.copyfile(asset, dest)
        copied.append(dest)
    return copied


def main() -> int:
    source_dir = Path(os.environ.get("SOURCE_DIR", "source"))
    build_dir = Path(os.environ.get("BUILD_DIR", "build"))
    md_dir = build_dir / "markdown"
    out_dir = build_dir / "notebooklm"
    assets_dir = Path(__file__).parent / "notebooklm_assets"

    print(f"running sphinx-build -b markdown → {md_dir}/")
    subprocess.run(
        ["sphinx-build", "-b", "markdown", str(source_dir), str(md_dir)],
        check=True,
    )

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"writing bundles to {out_dir}/")
    stats: list[BundleStats] = []
    for bundle in BUNDLES:
        files = collect_files(md_dir, bundle)
        out_path = out_dir / f"{bundle.name}.md"
        write_bundle(out_path, md_dir, files)
        size_kb = out_path.stat().st_size / 1024
        word_count = sum(len(f.read_text(encoding="utf-8").split()) for f in files)
        stats.append(BundleStats(bundle, len(files), size_kb, word_count))
        print(
            f"  {bundle.name}.md  {size_kb:>7.1f} KB  {word_count:>7} words  "
            f"({len(files)} pages)"
        )

    write_index(out_dir / "INDEX.md", stats)
    print(f"  INDEX.md  (generated)")

    for path in copy_assets(assets_dir, out_dir):
        print(f"  {path.name}  (asset)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
