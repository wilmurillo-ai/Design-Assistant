#!/usr/bin/env bash
set -euo pipefail

REPO="jeeaay/coding-plan-usage"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$SCRIPT_DIR}"

uname_s="$(uname -s)"
uname_m="$(uname -m)"

case "$uname_s" in
  Darwin) goos="darwin" ;;
  Linux) goos="linux" ;;
  *)
    echo "unsupported os: $uname_s"
    exit 1
    ;;
esac

case "$uname_m" in
  x86_64|amd64) goarch="amd64" ;;
  arm64|aarch64) goarch="arm64" ;;
  *)
    echo "unsupported arch: $uname_m"
    exit 1
    ;;
esac

asset="coding-plan-usage-${goos}-${goarch}.tar.gz"
url="https://github.com/${REPO}/releases/latest/download/${asset}"

mkdir -p "$TARGET_DIR"
archive_path="${TARGET_DIR}/${asset}"
bundle_dir="${TARGET_DIR}/coding-plan-usage-${goos}-${goarch}-bundle"

curl -fL "$url" -o "$archive_path"
tar -xzf "$archive_path" -C "$TARGET_DIR"
chmod +x "${bundle_dir}/coding-plan-usage"

echo "installed_bundle=${bundle_dir}"
echo "binary=${bundle_dir}/coding-plan-usage"
