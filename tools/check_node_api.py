#!/usr/bin/env python3
"""Say which exported Node classes the reference documents, and refuse a gap.

The Python reference has this already: sphinx's coverage builder lists the
classes the module exports and no page documents. The Node side had nothing,
and it cost two releases' worth of silence — BlobArrayBuilder and
BlobPackBuilder shipped in 1.2.12 as the headline addition and reached no page
until someone read the served site by hand.

The reverse failure is quieter still. A `js:autoclass` naming a class the
package does not export renders nothing: no page, no warning, no error, and a
green build. Nothing else in this repository can see it.

A class whose summary says INTERNAL DEVELOPMENT is exempt from needing a page.
That marker is the binding's own convention, written where the reader meets it;
this reads it rather than keeping a second list here that would drift from it.

    python3 tools/check_node_api.py            # gate
    python3 tools/check_node_api.py --report   # say what it sees, never fail
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DTS = HERE / "node_modules/@digitalsubstrate/dsviper/index.d.ts"
PAGES = HERE / "source/dsviper-node"

INTERNAL = "INTERNAL DEVELOPMENT"
# a class, with the JSDoc block immediately above it when there is one
DECL = re.compile(r"(?:/\*\*(?P<doc>.*?)\*/\s*)?^export class (?P<name>\w+)", re.M | re.S)
AUTOCLASS = re.compile(r"\{js:autoclass\}\s+(\w+)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="describe, never fail")
    args = ap.parse_args()

    if not DTS.exists():
        print(f"  node-api  {DTS.relative_to(HERE)} is not installed; nothing to check")
        return 0

    exported: dict[str, bool] = {}          # name -> marked internal
    for m in DECL.finditer(DTS.read_text(encoding="utf-8")):
        exported[m.group("name")] = INTERNAL in (m.group("doc") or "")

    documented: set[str] = set()
    for f in PAGES.rglob("*.md"):
        documented |= set(AUTOCLASS.findall(f.read_text(encoding="utf-8")))

    internal = {n for n, flag in exported.items() if flag}
    missing = sorted(set(exported) - documented - internal)
    ghost = sorted(documented - set(exported))
    exempt = sorted(internal & (set(exported) - documented))

    print(f"  node-api  {len(exported)} exported, {len(documented)} documented, "
          f"{len(exempt)} exempt")
    for n in exempt:
        print(f"              exempt: {n} — its summary says {INTERNAL}")

    failures: list[str] = []
    if ghost:
        failures.append(
            "these pages document classes the package does not export, so the "
            "directive renders nothing and the build stays green:\n      "
            + "\n      ".join(ghost))
    if missing:
        failures.append(
            "these exported classes reach no page:\n      " + "\n      ".join(missing)
            + "\n    Add a {js:autoclass} under source/dsviper-node/, or mark the class "
              f"{INTERNAL} in the binding if it is not product.")

    if failures and not args.report:
        for f in failures:
            print(f"\nERROR: {f}", file=sys.stderr)
        return 1
    for f in failures:
        print(f"  node-api  WOULD FAIL: {f.splitlines()[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
