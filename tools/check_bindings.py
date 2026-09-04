#!/usr/bin/env python3
"""Say which binding this build documents, and refuse a stale one.

Both API references are generated from the INSTALLED binding: autosummary reads
the `dsviper` package, sphinx-js runs TypeDoc over
`node_modules/@digitalsubstrate/dsviper`. On a tag build that is right — the
published documentation describes the published packages.

While improving documentation it is silently wrong, and it went wrong twice in
one session. The Node reference was read from the published npm package while
two days of JSDoc sat unread in the working copy, and the Python reference was
read from a frozen copy in a scratch virtualenv while the docstrings it was
supposed to render were a patch newer. Neither failed. Neither warned. Both
produced pages that looked finished and described the previous release.

The signal that you are one of those sessions is that the binding repository is
sitting next to this one. When it is, this refuses to build against anything
else; when it is not — a CI runner, a reader with a checkout of the docs alone —
it says which published versions it used and passes.

    python3 tools/check_bindings.py            # gate
    python3 tools/check_bindings.py --report   # say what is installed, never fail
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SIBLINGS = ("../com.digitalsubstrate.viper", "../viper")


def viper_repo() -> Path | None:
    """The binding working copy, if it is checked out beside this repository."""
    env = os.environ.get("VIPER")
    for candidate in ([env] if env else []) + list(SIBLINGS):
        if not candidate:
            continue
        p = (HERE / candidate).resolve() if not Path(candidate).is_absolute() else Path(candidate)
        if (p / "dsviper_wheel").is_dir() and (p / "dsviper_node").is_dir():
            return p
    return None


def python_binding() -> tuple[str, str]:
    """(path of the imported dsviper package, version) — or ('', reason)."""
    code = "import dsviper,os;print(os.path.dirname(dsviper.__file__));" \
           "print('.'.join(map(str,dsviper.version())))"
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    if r.returncode != 0:
        return "", "not importable"
    path, version = r.stdout.strip().splitlines()
    return path, version


def node_binding() -> tuple[str, str]:
    pkg = HERE / "node_modules" / "@digitalsubstrate" / "dsviper"
    if not pkg.exists():
        return "", "not installed"
    meta = json.loads((pkg / "package.json").read_text())
    # a linked working copy is a symlink; resolve() gives what TypeDoc will read
    return str(pkg.resolve()), meta.get("version", "?")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true",
                    help="print what is installed and always succeed")
    args = ap.parse_args()

    repo = viper_repo()
    py_path, py_version = python_binding()
    node_path, node_version = node_binding()

    print(f"  Python  {py_version:<12} {py_path or '(' + 'not importable' + ')'}")
    print(f"  Node    {node_version:<12} {node_path or '(not installed)'}")

    if args.report:
        return 0
    if repo is None:
        print("  the binding repository is not beside this one — documenting the "
              "published packages, which is what a release build does")
        return 0

    wheel, node_src = str(repo / "dsviper_wheel"), str(repo / "dsviper_node")
    stale = []
    if not py_path.startswith(wheel):
        stale.append(("Python", py_version, py_path or "not importable", wheel,
                      f"pip install -e {os.path.relpath(wheel, HERE)}"))
    if node_path != node_src:
        stale.append(("Node", node_version, node_path or "not installed", node_src,
                      f"(cd {os.path.relpath(node_src, HERE)} && npm link) && "
                      "npm link @digitalsubstrate/dsviper"))

    if not stale:
        print(f"  both read the working copy at {repo}")
        return 0

    print(f"\n⚠️  {len(stale)} reference(s) would be generated from a binding that is "
          f"not the working copy sitting at\n    {repo}\n")
    for name, version, got, want, fix in stale:
        print(f"  {name}: reads {version} from\n      {got}\n    expected\n      {want}\n"
              f"    fix with\n      {fix}\n")
    print("Every docstring written in that working copy is invisible to this build, "
          "and\nthe pages will look finished while describing the previous release.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
