#!/bin/bash
# fetch-nictation.sh — 抓取钛媒体快报频道（近十天）
# 用法: ./fetch-nictation.sh

CACHE_DIR="${XDG_CACHE_DIR:-$HOME/.cache/tmtpost}"
mkdir -p "$CACHE_DIR"
CACHE="$CACHE_DIR/nictation.html"
TTL=300  # 5分钟缓存

if [[ -f "$CACHE" ]]; then
  age=$(($(date +%s) - $(stat -f %m "$CACHE" 2>/dev/null || stat -c %Y "$CACHE" 2>/dev/null)))
  if (( age < TTL )); then
    cat "$CACHE"
    exit 0
  fi
fi

html=$(curl -sL "https://www.tmtpost.com/nictation" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  --max-time 15)

if [[ -z "$html" ]]; then
  echo '[]'
  exit 1
fi

echo "$html" > "$CACHE"
echo "$html"
