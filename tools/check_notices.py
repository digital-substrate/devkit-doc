#!/usr/bin/env python3
"""Keep the published third-party notices equal to the ones that ship.

Three copies of the same obligation exist: the runtime repository keeps the
full list grouped by how each component is used, the wheel keeps the subset
embedded in the runtime, and this repository publishes that subset. Only the
last one is read by anyone who is not building Viper, and it is the one that
drifted: it lost pugixml when the XML wire format landed, and nothing noticed
for two months, because the page carries no statement of how many components
there should be.

Two checks, and the second runs even without the binding repository beside us:

  1. source/legal/THIRD-PARTY-NOTICES.txt is byte-identical to the wheel's,
     when the binding working copy is next to this one.
  2. the table on source/legal/third_party_notices.md has one row per
     component the notices file declares — the failure that actually happened.

    python3 tools/check_notices.py            # gate
    python3 tools/check_notices.py --report   # say what it sees, never fail
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
NOTICES = HERE / "source/legal/THIRD-PARTY-NOTICES.txt"
PAGE = HERE / "source/legal/third_party_notices.md"
SIBLINGS = ("../com.digitalsubstrate.viper", "../viper")

# "5. pugixml — MIT" on its own, banded by ==== rules. The em dash keeps the
# numbered clauses inside a license text (1. Redistributions ...) out of it.
ENTRY = re.compile(r"^={10,}\n(\d+)\. (.+?) — (.+?)\n={10,}$", re.M)
ROW = re.compile(r"^\| \[(?P<name>[^\]]+)\]\([^)]*\) \| (?P<version>[^|]*?) \| (?P<license>[^|]*?) \|$", re.M)


def wheel_notices() -> Path | None:
    env = os.environ.get("VIPER")
    for candidate in ([env] if env else []) + list(SIBLINGS):
        if not candidate:
            continue
        p = Path(candidate) if Path(candidate).is_absolute() else (HERE / candidate)
        f = (p / "dsviper_wheel/THIRD-PARTY-NOTICES.txt").resolve()
        if f.is_file():
            return f
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="describe, never fail")
    args = ap.parse_args()

    notices = NOTICES.read_text(encoding="utf-8")
    components = [(int(n), name, lic) for n, name, lic in ENTRY.findall(notices)]
    rows = ROW.findall(PAGE.read_text(encoding="utf-8"))
    failures: list[str] = []

    source = wheel_notices()
    if source is None:
        print("  notices  no binding working copy beside this repository; "
              "publishing the committed copy")
    elif source.read_text(encoding="utf-8") != notices:
        failures.append(
            f"source/legal/THIRD-PARTY-NOTICES.txt differs from the one the wheel ships.\n"
            f"    It is a copy, not a source. Refresh it:\n"
            f"      cp {source} {NOTICES.relative_to(HERE)}\n"
            f"    then add a row per component the page's table is missing.")
    else:
        print(f"  notices  identical to {source}")

    print(f"  notices  {len(components)} component(s) declared, {len(rows)} row(s) in the table")
    for number, name, lic in components:
        print(f"             {number}. {name} — {lic}")

    if len(components) != len(rows):
        failures.append(
            f"the notices file declares {len(components)} components and the page's "
            f"table has {len(rows)} rows.\n"
            f"    Every component that ships is listed on the page, or the page "
            f"under-reports the product.")
    if not components:
        failures.append("no component found in the notices file — the format changed, "
                        "and this check has stopped checking anything.")

    if failures and not args.report:
        for f in failures:
            print(f"\nERROR: {f}", file=sys.stderr)
        return 1
    if failures:
        for f in failures:
            print(f"  notices  WOULD FAIL: {f.splitlines()[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
