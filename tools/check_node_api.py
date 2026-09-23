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

Exemptions are declared below, not read out of the prose. The first version of
this gate exempted any class whose summary contained INTERNAL DEVELOPMENT, which
looked like deriving the exception from the artefact rather than declaring it —
the cheaper of the two, since a derived exception cannot rot. It was not a
derivation: whether a class is product is a decision, and no sentence in the
binding states it as a fact. A better docstring dropped the phrase two days
later and the gate went red on prose that had improved.

A declared exemption needs a stale guard, so each entry is checked both ways: a
name that is no longer exported fails, and so does one that has since been given
a page. The list cannot quietly outlive its reasons.

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

# Declared exemptions: a class that is exported but deliberately kept out of the
# reference, with the reason. Both directions are guarded below.
EXEMPT: dict[str, str] = {
    # Empty on purpose. DefinitionsMapper sat here while its summary was a
    # verdict — "a class used for INTERNAL DEVELOPMENT" — with nothing a reader
    # could act on. It now states what it rewrites and why the caller carries
    # the risk, which is describable, so it has a page on both bindings like
    # every other exported class.
}

DECL = re.compile(r"^export class (?P<name>\w+)", re.M)
AUTOCLASS = re.compile(r"\{js:autoclass\}\s+(\w+)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="describe, never fail")
    args = ap.parse_args()

    if not DTS.exists():
        print(f"  node-api  {DTS.relative_to(HERE)} is not installed; nothing to check")
        return 0

    exported = {m.group("name") for m in DECL.finditer(DTS.read_text(encoding="utf-8"))}

    documented: set[str] = set()
    for f in PAGES.rglob("*.md"):
        documented |= set(AUTOCLASS.findall(f.read_text(encoding="utf-8")))

    missing = sorted(exported - documented - set(EXEMPT))
    ghost = sorted(documented - exported)
    stale_gone = sorted(set(EXEMPT) - exported)
    stale_documented = sorted(set(EXEMPT) & documented)

    print(f"  node-api  {len(exported)} exported, {len(documented)} documented, "
          f"{len(EXEMPT)} exempt by declaration")
    for n, why in sorted(EXEMPT.items()):
        print(f"              exempt: {n} — {why}")

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
