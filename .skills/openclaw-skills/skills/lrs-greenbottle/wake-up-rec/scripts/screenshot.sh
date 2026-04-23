#!/bin/bash
# 截屏脚本 - 保存到 ~/Desktop/screenshot_YYYYMMDD_HHMMSS.png

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$HOME/Desktop/screenshot_${TIMESTAMP}.png"

/usr/sbin/screencapture "$OUTPUT"

if [ -f "$OUTPUT" ]; then
    echo "✅ 截图成功: $OUTPUT"
    echo "$OUTPUT"
else
    echo "❌ 截图失败"
    exit 1
fi
