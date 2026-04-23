#!/usr/bin/env bash
set -euo pipefail

ID="${1:-}"
TITLE_B64="${2:-}"
CONTENT_B64="${3:-}"

NOTEBOOKLM_BIN=/Users/block/notebooklm-env/bin/notebooklm \
ZK_SYNC_DIR=/Users/block/zk_sync \
NOTEBOOK_ID=e363ecbe-70bc-490e-acbe-329f7e6fb85c \
/Users/block/.openclaw/scripts/zk-post-save.sh "$ID" "$TITLE_B64" "$CONTENT_B64"