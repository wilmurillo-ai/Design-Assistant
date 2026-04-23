#!/bin/bash
# search-nictation.sh — 从钛媒体快报中搜索含关键词的条目
# 用法: ./search-nictation.sh "关键词1,关键词2"
# 输出: 匹配的 JSON 数组

KEYWORDS="${1:-}"
[[ -z "$KEYWORDS" ]] && echo "Usage: $0 \"关键词1,关键词2\"" && exit 1

IFS=',' read -ra KW <<< "$KEYWORDS"
CACHE_DIR="${XDG_CACHE_DIR:-$HOME/.cache/tmtpost}"
mkdir -p "$CACHE_DIR"

# 尝试读缓存（5分钟有效）
if [[ -f "$CACHE_DIR/nictation.html" ]]; then
  age=$(($(date +%s) - $(stat -f %m "$CACHE_DIR/nictation.html" 2>/dev/null || stat -c %Y "$CACHE_DIR/nictation.html" 2>/dev/null)))
  if (( age < 300 )); then
    html=$(cat "$CACHE_DIR/nictation.html")
  fi
fi

# 无缓存则抓取
if [[ -z "$html" ]]; then
  html=$(curl -sL "https://www.tmtpost.com/nictation" \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
    -H "Accept-Language: zh-CN,zh;q=0.9" \
    --max-time 15)
  echo "$html" > "$CACHE_DIR/nictation.html"
fi

[[ -z "$html" ]] && echo '[]' && exit 1

# 用 grep + python 做多关键词过滤
echo "$html" | grep -oP '(?<=href="/nictation/)[0-9]+(?=\.html")' | sort -u > "$CACHE_DIR/nictation_ids.tmp"

# 简化：用 bash 循环过滤（适合少量条目）
# 提取所有快報条目文本块
echo "$html" | grep -oP '\[[^\]]+\](/nictation/[0-9]+\.html\)[^\[]+' | while read line; do
  for kw in "${KW[@]}"; do
    kw=$(echo "$kw" | xargs)  # trim whitespace
    if echo "$line" | grep -qi "$kw"; then
      url=$(echo "$line" | grep -oP '(?<=href=")[^"]+(?=")')
      title=$(echo "$line" | sed 's/.*\[\(.*\)\].*/\1/')
      echo "{\"keyword\":\"$kw\",\"title\":\"$title\",\"url\":\"https://www.tmtpost.com$url\"}"
      break
    fi
  done
done | python3 -c "
import sys, json
items = []
for line in sys.stdin:
    line = line.strip()
    if line:
        try:
            items.append(json.loads(line))
        except: pass
print(json.dumps(items, ensure_ascii=False, indent=2))
"
