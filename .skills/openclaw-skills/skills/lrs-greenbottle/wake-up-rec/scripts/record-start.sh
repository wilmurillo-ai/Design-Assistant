#!/bin/bash
# 录屏启动脚本 - 开始录制

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$HOME/Desktop/recording_${TIMESTAMP}.mp4"

# 使用 avfoundation 捕获屏幕 (Mac专属)
# 设备0 = 屏幕，":none" = 不捕获音频
/opt/homebrew/bin/ffmpeg -f avfoundation -i "0:none" -r 30 -c:v libx264 -preset ultrafast -crf 23 -pix_fmt uyvy422 -movflags +faststart "$OUTPUT" > /dev/null 2>&1 &

echo "✅ 录屏已启动: $OUTPUT"
