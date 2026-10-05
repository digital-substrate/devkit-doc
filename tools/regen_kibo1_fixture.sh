#!/usr/bin/env bash
# Regenerate the committed kibo 1 Tuto SDK fixture at source/_fixtures/kibo-1/model/.
#
# This package is the kibo 1 output (kibo 1.2.x, kibo-template-viper 1.2.x) for
# source/_fixtures/Tuto/model.dsm.
# It is imported by the kibo-1 section's doctests (`_use_sdk("kibo-1")`) so
# their examples run against the real generated surface. It is a build artifact — never edit it
# by hand; rerun this script after any change to the DSM fixture or to the
# kibo-template-viper Python templates, then `git diff` to review the delta
# (that diff is the drift check the publish CI cannot run, since CI has no JDK).
#
# KIBO_JAR and KIBO_TEMPLATES name kibo 1 and the 1.2 pack (dsm_util refuses a
# kibo 2 jar or pack); without them, dsm_util looks in sibling checkouts, which
# must then be on the 1.2 line. For example, from a DevKit:
#   KIBO_JAR=<devkit>/kibo-1/tools/kibo-1.2.13.jar KIBO_TEMPLATES=<devkit>/kibo-1/templates
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"        # devkit-doc/
sibling_root="$(cd "$here/.." && pwd)"                          # repos root (devkit-doc's parent)

dsm="$here/source/_fixtures/Tuto/model.dsm"
dst="$here/source/_fixtures/kibo-1/model"
tools="$sibling_root/dsviper-tools/dsm_util.py"

jar="${KIBO_JAR:-$(ls "$sibling_root"/kibo/target/kibo-1.*.jar 2>/dev/null | sort -V | tail -1)}"
templates="${KIBO_TEMPLATES:-$sibling_root/kibo-template-viper}/python"

[ -f "$jar" ]           || { echo "kibo 1 jar not found (set KIBO_JAR)"; exit 1; }
[ -d "$templates" ]     || { echo "templates not found: $templates (set KIBO_TEMPLATES)"; exit 1; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
( cd "$work" && python3 "$tools" create_python_package --kibo "$jar" --templates "$templates" "$dsm" )

rm -rf "$dst"
cp -R "$work/model" "$dst"
rm -rf "$dst/__pycache__"

echo "regenerated $dst from $dsm using $(basename "$jar")"
echo "review with: git -C \"$here\" diff -- source/_fixtures/kibo-1/model"
