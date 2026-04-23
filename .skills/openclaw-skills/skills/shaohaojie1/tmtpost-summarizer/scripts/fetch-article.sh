#!/bin/bash
# fetch-latest.sh — 从钛媒体抓取最新文章 URL
# 用法: ./fetch-article.sh [max_articles]
# 输出: JSON 数组，每项 { title, url, time, views }

MAX="${1:-5}"
CACHE_DIR="${XDG_CACHE_DIR:-$HOME/.cache/tmtpost}"
mkdir -p "$CACHE_DIR"
CACHE="$CACHE_DIR/latest.json"

# 缓存 5 分钟内的结果，减少重复请求
if [[ -f "$CACHE" ]]; then
  age=$(($(date +%s) - $(stat -f %m "$CACHE" 2>/dev/null || stat -c %Y "$CACHE" 2>/dev/null)))
  if (( age < 300 )); then
    cat "$CACHE"
    exit 0
  fi
fi

html=$(curl -sL "https://www.tmtpost.com/" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  --max-time 15)

if [[ -z "$html" ]]; then
  echo '[]'
  exit 1
fi

# 提取文章列表: title, URL, 时间, 阅读量
echo "$html" | grep -oE 'https://www\.tmtpost\.com/[0-9]+\.html' \
  | sort -u \
  | head -n "$MAX" \
  | while read url; do
    # 简单的标题推断（实际以文章页为准）
    id=$(echo "$url" | grep -oE '[0-9]+')
    echo "$url"
  done > "$CACHE_DIR/urls.tmp"

# 返回 JSON
count=0
echo '['
while IFS= read -r url; do
  ((count++))
  id=$(echo "$url" | grep -oE '[0-9]+')
  [[ -z "$id" ]] && continue
  comma=""
  [[ $count -gt 1 ]] && comma=","
  # 注意：精确标题需二次抓取文章页获取 <title>
  # 此处简化返回 URL，由调用方负责获取标题
  printf '  %s{"id":"%s","url":"%s"}\n' "$comma" "$id" "$url"
done < "$CACHE_DIR/urls.tmp"
echo ']'
