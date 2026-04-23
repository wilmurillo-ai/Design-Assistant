#!/usr/bin/env bash
set -euo pipefail

PLUGIN_DIR="${1:-.}"
cd "$PLUGIN_DIR"

echo "[preflight] plugin dir: $(pwd)"

missing=0
for f in openclaw.plugin.json package.json; do
  if [[ ! -f "$f" ]]; then
    echo "[error] missing required file: $f"
    missing=1
  fi
done

if [[ $missing -ne 0 ]]; then
  exit 2
fi

if command -v jq >/dev/null 2>&1; then
  echo "[check] validating JSON syntax"
  jq empty openclaw.plugin.json >/dev/null
  jq empty package.json >/dev/null

  echo "[check] required keys"
  jq -e '.name and .version' package.json >/dev/null || { echo "[error] package.json requires name+version"; exit 3; }
  jq -e '.id and .name and .runtime' openclaw.plugin.json >/dev/null || { echo "[error] openclaw.plugin.json requires id+name+runtime"; exit 3; }

  echo "[check] clawhub plugin metadata"
  jq -e '.openclaw.compat.pluginApi' package.json >/dev/null || { echo "[error] missing package.json: openclaw.compat.pluginApi"; exit 4; }
  jq -e '.openclaw.build.openclawVersion' package.json >/dev/null || { echo "[error] missing package.json: openclaw.build.openclawVersion"; exit 4; }

  # Optional but recommended for dashboard compatibility insight.
  if ! jq -e '.openclaw.build.pluginSdkVersion' package.json >/dev/null 2>&1; then
    echo "[warn] recommended package.json field missing: openclaw.build.pluginSdkVersion"
  fi

  echo "[check] package quality fields"
  PKG_DESC="$(jq -r '.description // ""' package.json)"
  if [[ -z "${PKG_DESC// }" ]]; then
    echo "[warn] package.json description is empty; quality checks may flag low clarity"
  fi

  echo "[check] manifest version alignment"
  PKG_VER="$(jq -r '.version' package.json)"
  PLUGIN_VER="$(jq -r '.version // empty' openclaw.plugin.json)"
  if [[ -n "$PLUGIN_VER" && "$PKG_VER" != "$PLUGIN_VER" ]]; then
    echo "[error] version mismatch: package.json=$PKG_VER, openclaw.plugin.json=$PLUGIN_VER"
    exit 5
  fi
else
  echo "[warn] jq not found, skipped deep JSON checks"
fi

echo "[check] docs presence"
if [[ ! -f README.md && ! -f Readme.md && ! -f readme.md ]]; then
  echo "[warn] README.md not found; quality checks may reduce trust score"
fi

echo "[check] static-analysis risk patterns"
if grep -RIn "child_process\|execSync\|spawn" . --include='*.js' --include='*.mjs' --include='*.ts' >/dev/null 2>&1; then
  echo "[warn] detected potentially risky patterns (child_process/spawn)."
  echo "       This can trigger marketplace static-analysis warnings."
fi

echo "[ok] preflight passed"
echo "Next: open ClawHub Dashboard -> Publish Plugin -> upload this plugin package/repo"
echo "Dashboard required fields reminder: changelog, source repo, source commit, source ref"
