#!/usr/bin/env bash
# Regenerate the committed Tuto SDK fixture at source/_fixtures/model/.
#
# This package is the kibo 2 output for source/_fixtures/Tuto/model.dsm, rendered by
# kibo-project from the kibo-template-viper pack. It is imported by the "Using your generated
# SDK" doctests so their examples run against the real generated surface. It is a build
# artifact — never edit it by hand; rerun this script after any change to the DSM fixture or to
# the pack, then `git diff` to review the delta (that diff is the drift check the publish CI
# cannot run, since CI has no JDK).
#
# Overrides: KIBO_JAR, KIBO_TEMPLATES, KIBO_PROJECT (defaults resolve via sibling checkouts).
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"        # devkit-doc/
sibling_root="$(cd "$here/.." && pwd)"                          # repos root (devkit-doc's parent)

dsm="$here/source/_fixtures/Tuto/model.dsm"
dst="$here/source/_fixtures/model"
tool="${KIBO_PROJECT:-$sibling_root/kibo-project/kibo_project.py}"
export KIBO_JAR="${KIBO_JAR:-$(ls "$sibling_root"/kibo/target/kibo-*.jar 2>/dev/null | sort -V | tail -1)}"
export KIBO_TEMPLATES="${KIBO_TEMPLATES:-$sibling_root/kibo-template-viper}"

[ -f "$tool" ]           || { echo "kibo-project not found: $tool (set KIBO_PROJECT)"; exit 1; }
[ -f "$KIBO_JAR" ]       || { echo "kibo jar not found (set KIBO_JAR)"; exit 1; }
[ -d "$KIBO_TEMPLATES" ] || { echo "templates not found: $KIBO_TEMPLATES (set KIBO_TEMPLATES)"; exit 1; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir "$work/definitions"
cp "$dsm" "$work/definitions/"
cat > "$work/kibo.toml" <<TOML
[project]
definitions = "definitions"
infrastructure = "model"

[generator]
templates = "2"

[target.python]
features = ["Base"]
output = "generated"
TOML
python3 "$tool" generate "$work/kibo.toml"

rm -rf "$dst"
cp -R "$work/generated/model" "$dst"
find "$dst" -name __pycache__ -type d -prune -exec rm -rf {} +

echo "regenerated $dst from $dsm using $(basename "$KIBO_JAR")"
echo "review with: git -C \"$here\" diff -- source/_fixtures/model"
