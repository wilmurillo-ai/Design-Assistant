#!/usr/bin/env bash
set -euo pipefail

SLUG="${1:-}"
if [[ -z "$SLUG" ]]; then
  echo "Usage: $0 <plugin-slug> [dir]"
  exit 1
fi

ROOT="${2:-.}"
DIR="$ROOT/$SLUG"
mkdir -p "$DIR"

cat > "$DIR/package.json" <<EOF
{
  "name": "$SLUG",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "main": "index.js",
  "openclaw": {
    "extensions": ["./index.js"],
    "compat": {
      "pluginApi": ">=2026.4.9",
      "minGatewayVersion": ">=2026.4.9"
    },
    "build": {
      "openclawVersion": "2026.4.9",
      "pluginSdkVersion": "2026.4.9"
    }
  }
}
EOF

cat > "$DIR/openclaw.plugin.json" <<EOF
{
  "id": "$SLUG",
  "name": "$SLUG",
  "version": "0.1.0",
  "runtime": "node",
  "entry": "index.js",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
EOF

cat > "$DIR/index.js" <<'EOF'
export default {
  name: '__PLUGIN_SLUG__',
  setup() {
    return {
      ok: true,
      message: 'starter plugin loaded'
    };
  }
};
EOF

sed -i '' "s/__PLUGIN_SLUG__/$SLUG/g" "$DIR/index.js" 2>/dev/null || \
  sed -i "s/__PLUGIN_SLUG__/$SLUG/g" "$DIR/index.js"

echo "[ok] plugin scaffold created: $DIR"
echo "Next: run plugin workbench preflight"
echo "  ./skills/openclaw-plugin-workbench/scripts/plugin-preflight.sh $DIR"
echo "Then submit in ClawHub Dashboard -> Publish Plugin"
