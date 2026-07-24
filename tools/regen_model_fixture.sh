#!/usr/bin/env bash
# Regenerate the committed Tuto SDK fixture at source/_fixtures/model/.
#
# This package is the Kibo-generated output for source/_fixtures/Tuto/model.dsm.
# It is imported by the "Using your generated SDK" doctests so their examples
# run against the real generated surface. It is a build artifact — never edit it
# by hand; rerun this script after any change to the DSM fixture or to the
# kibo-template-viper Python templates, then `git diff` to review the delta
# (that diff is the drift check the publish CI cannot run, since CI has no JDK).
#
# Overrides: KIBO_JAR, KIBO_TEMPLATES (defaults resolve via sibling checkout).
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"        # devkit-doc/
sibling_root="$(cd "$here/.." && pwd)"                          # repos root (devkit-doc's parent)

dsm="$here/source/_fixtures/Tuto/model.dsm"
dst="$here/source/_fixtures/model"
tools="$sibling_root/dsviper-tools/dsm_util.py"

jar="${KIBO_JAR:-$(ls "$sibling_root"/kibo/target/kibo-*.jar 2>/dev/null | sort -V | tail -1)}"
templates="${KIBO_TEMPLATES:-$sibling_root/kibo-template-viper}/python"

[ -f "$jar" ]           || { echo "kibo jar not found (set KIBO_JAR)"; exit 1; }
[ -d "$templates" ]     || { echo "templates not found: $templates (set KIBO_TEMPLATES)"; exit 1; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
( cd "$work" && python3 "$tools" create_python_package --kibo "$jar" --templates "$templates" "$dsm" )

rm -rf "$dst"
cp -R "$work/model" "$dst"
rm -rf "$dst/__pycache__"

echo "regenerated $dst from $dsm using $(basename "$jar")"
echo "review with: git -C \"$here\" diff -- source/_fixtures/model"
